
from ctypes import (
  CDLL, Structure, POINTER, byref,
  c_float, c_int, 
  c_ubyte, c_ushort, c_uint, c_ulonglong, 
  c_void_p, c_char_p
)
import os

class RFParameters(Structure):
  _fields_ = [
    ('frequency', c_ulonglong),
    ('powerLevel', c_float), 
  ] + [ (name, c_ubyte) for name in (
    'rfEnable', 'alcOpen', 'autoLevelEnable', 'fastTune',
    'tuneStep', 'referenceSetting',
  )]

class DeviceStatus(Structure):
  _fields_ = [(name, c_ubyte) for name in (
    'tcxoPllLock', 'vcxoPllLock', 'finePllLock', 'coarsePllLock', 
    'sumPllLock', 'extRefDetected', 'refClkOutEnable', 'extRefLockEnable', 
    'alcOpen', 'fastTuneEnable', 'standbyEnable', 'rfEnable',
    'pxiClkEnable', 
  )]

path = os.path.dirname(os.path.abspath(__file__))
dll = CDLL(os.path.join(path, 'sc5503b_usb.dll'))

dll.sc5503b_OpenDevice.argtypes = [c_char_p, POINTER(c_void_p)]
dll.sc5503b_OpenDevice.restype = c_int

dll.sc5503b_CloseDevice.argtypes = [c_void_p]
dll.sc5503b_CloseDevice.restype = c_int

dll.sc5503b_SetFrequency.argtypes = [c_void_p, c_ulonglong]
dll.sc5503b_SetFrequency.restype = c_int

dll.sc5503b_SetPowerLevel.argtypes = [c_void_p, c_float]
dll.sc5503b_SetPowerLevel.restype = c_int

dll.sc5503b_SetRfOutput.argtypes = [c_void_p, c_ubyte]
dll.sc5503b_SetRfOutput.restype = c_int

dll.sc5503b_GetRfParameters.argtypes = [c_void_p, POINTER(RFParameters)]
dll.sc5503b_GetRfParameters.restype = c_int

dll.sc5503b_GetDeviceStatus.argtypes = [c_void_p, POINTER(DeviceStatus)]
dll.sc5503b_GetDeviceStatus.restype = c_int

class SC5503B:
  def __init__(self, serialNumber, name=None):
    self.serialNumber = serialNumber

    self.name = name or 'SC5503B: %d' % serialNumber
    self.data = {
      'freq': {'actions': ['set', 'get'], 'hint': 'type: number, unit: Hz, range: [5e7, 1e10]' },
      'pow': {'actions': ['set', 'get'], 'hint': 'type: number, unit: dB, range: [-60, 10]' },
      'output': {'actions': ['set', 'get'], 'hint': 'type: list, values: [0, 1]' },
    }

  def start(self):
    self.handle = c_void_p()
    result = dll.sc5503b_OpenDevice(str(self.serialNumber).encode(), byref(self.handle))
    status = 'success' if result == 0 else 'error'
    return status, result
  
  def setValues(self, dic):
    result = 0
    if 'output' in dic:
      result |= dll.sc5503b_SetRfOutput(self.handle, dic['output'])
    if 'freq' in dic:
      result |= dll.sc5503b_SetFrequency(self.handle, int(dic['freq']))
    if 'pow' in dic:
      result |= dll.sc5503b_SetPowerLevel(self.handle, dic['pow'])
    status = 'success' if result == 0 else 'error'
    return status, result

  def getValues(self, keys = None):
    params = RFParameters()
    dll.sc5503b_GetRfParameters(self.handle, params)
    status = DeviceStatus()
    dll.sc5503b_GetDeviceStatus(self.handle, status)
    res = {
      'freq': params.frequency, 
      'pow': float(params.powerLevel),
      'output': status.rfEnable,
    }
    return 'success', res

  def stop(self):
    result = dll.sc5503b_CloseDevice(self.handle)
    status = 'success' if result == 0 else 'error'
    return status, result

if __name__ == '__main__':
  dev = SC5503B(serialNumber= 10002656 )
  print(dev.start())
  print(dev.setValues({'freq': 3e9, 'pow': 3, 'output': 0}))
  print(dev.getValues())
  print(dev.stop())
