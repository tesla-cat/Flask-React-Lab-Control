
from ctypes import (
  CDLL, Structure, POINTER,
  c_float, c_int, 
  c_ubyte, c_ushort, c_uint, c_ulonglong,
  c_void_p, c_char_p
)
import os

class RFParameters(Structure):
  _fields_ = [
    ('rf1_freq', c_ulonglong),
    ('start_freq', c_ulonglong),
    ('stop_freq', c_ulonglong),
    ('step_freq', c_ulonglong),
    ('sweep_dwell_time', c_uint),
    ('sweep_cycles', c_uint),
    ('buffer_points', c_uint),
    ('rf_level', c_float),
    ('rf2_freq', c_ushort)
  ]
class ListMode(Structure):
  _fields_ = [(name, c_ubyte) for name in (
    'sss_mode', 'weep_dir', 'tri_waveform', 'hw_trigger', 
    'step_on_hw_trig', 'return_to_start', 'trig_out_enable', 'trig_out_on_cycle'
  )]
class OperateStatus(Structure):
  _fields_ = [(name, c_ubyte) for name in (
    'rf1_lock_mode', 'rf1_loop_gain', 'device_access', 'rf2_standby', 
    'rf1_standby', 'auto_pwr_disable', 'alc_mode', 'rf1_out_enable', 
    'ext_ref_lock_enable', 'ext_ref_detect', 'ref_out_select', 'list_mode_running',
    'rf1_mode', 'over_temp', 'harmonic_ss'
  )]
class PllStatus(Structure):
  _fields_ = [(name, c_ubyte) for name in (
    'sum_pll_ld', 'crs_pll_ld', 'fine_pll_ld', 'crs_ref_pll_ld', 
    'crs_aux_pll_ld', 'ref_100_pll_ld', 'ref_10_pll_ld', 'rf2_pll_ld'
  )]

class DeviceStatus(Structure):
  _fields_ = [
    ('list_mode', ListMode),
    ('operate_status', OperateStatus),
    ('pll_status', PllStatus)
  ]

path = os.path.dirname(os.path.abspath(__file__))
dll = CDLL(os.path.join(path, 'sc5511a.dll'))

dll.sc5511a_open_device.argtypes = [c_char_p]
dll.sc5511a_open_device.restype = c_void_p
dll.sc5511a_close_device.argtypes = [c_void_p]
dll.sc5511a_close_device.restype = c_int
dll.sc5511a_set_freq.argtypes = [c_void_p, c_ulonglong]
dll.sc5511a_set_freq.restype = c_int
dll.sc5511a_set_level.argtypes = [c_void_p, c_float]
dll.sc5511a_set_level.restype = c_int
dll.sc5511a_set_output.argtypes = [c_void_p, c_ubyte]
dll.sc5511a_set_output.restype = c_int
dll.sc5511a_get_rf_parameters.argtypes = [c_void_p, POINTER(RFParameters)]
dll.sc5511a_get_rf_parameters.restype = c_int
dll.sc5511a_get_device_status.argtypes = [c_void_p, POINTER(DeviceStatus)]
dll.sc5511a_get_device_status.restype = c_int

class SC5511A:
  def __init__(self, serialNumber, name=None):
    self.serialNumber = serialNumber

    self.name = name or 'SC5511A: %d' % serialNumber
    self.data = {
      'freq': {'actions': ['set', 'get'], 'hint': 'type: number, unit: Hz, range: [1e8, 2e10]' },
      'pow': {'actions': ['set', 'get'], 'hint': 'type: number, unit: dB, range: [-30, 13]' },
      'output': {'actions': ['set', 'get'], 'hint': 'type: list, values: [0, 1]' },
    }

  def start(self):
    self.handle = dll.sc5511a_open_device(str(self.serialNumber).encode())
    status = 'success' if self.handle else 'error'
    return status, self.handle
  
  def setValues(self, dic):
    result = 0
    if 'output' in dic:
      result |= dll.sc5511a_set_output(self.handle, dic['output'])
    if 'freq' in dic:
      result |= dll.sc5511a_set_freq(self.handle, int(dic['freq']))
    if 'pow' in dic:
      result |= dll.sc5511a_set_level(self.handle, dic['pow'])
    status = 'success' if result == 0 else 'error'
    return status, result

  def getValues(self, keys = None):
    params = RFParameters()
    dll.sc5511a_get_rf_parameters(self.handle, params)
    status = DeviceStatus()
    dll.sc5511a_get_device_status(self.handle, status)
    res = {
      'freq': params.rf1_freq, 
      'pow': float(params.rf_level),
      'output': status.operate_status.rf1_out_enable,
    }
    return 'success', res

  def stop(self):
    result = dll.sc5511a_close_device(self.handle)
    status = 'success' if result == 0 else 'error'
    return status, result

if __name__ == '__main__':
  dev = SC5511A(serialNumber= 10002657 )
  print(dev.start())
  print(dev.setValues({'freq': 11000000000, 'pow': 6, 'output': 0}))
  print(dev.getValues())
  print(dev.stop())
