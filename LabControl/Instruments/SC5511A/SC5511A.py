
import os, ctypes

path = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.WinDLL(os.path.join(path, 'sc5511a.dll'))
dll.sc5511a_open_device.restype = ctypes.POINTER(ctypes.c_int)

# see definition in './c/sc5511a.h'
class device_rf_params_t(ctypes.Structure):
    _fields_ = [
        ('rf1_freq', ctypes.c_ulonglong),
        ('start_freq', ctypes.c_ulonglong),
        ('stop_freq', ctypes.c_ulonglong),
        ('step_freq', ctypes.c_ulonglong),
        ('sweep_dwell_time', ctypes.c_uint),
        ('sweep_cycles', ctypes.c_uint),
        ('buffer_points', ctypes.c_uint),
        ('rf_level', ctypes.c_float),
        ('rf2_freq', ctypes.c_ushort)
    ]

class SC5511A:
    def __init__(self, serialNumber, name=None):
        self.serialNumber = serialNumber
    
    def start(self):
        self.handle = dll.sc5511a_open_device(b'%d' % self.serialNumber)
        dll.sc5511a_set_rf_mode(self.handle, 0)
        dll.sc5511a_set_output(self.handle, 1)
        print(self.handle)

    def setValues(self, dic):
        result = 0
        if 'rf1_freq' in dic:
            result |= dll.sc5511a_set_freq(self.handle, ctypes.c_ulonglong(int(dic['rf1_freq'])))

    def getValues(self, keys = None):
        device_rf_params = device_rf_params_t()
        dll.sc5511a_get_rf_parameters(self.handle, device_rf_params)
        print(device_rf_params.rf1_freq)
        print(device_rf_params.start_freq)
        print(device_rf_params.stop_freq)
        print(device_rf_params.step_freq)
        print(device_rf_params.sweep_dwell_time)
        print(device_rf_params.sweep_cycles)
        print(device_rf_params.buffer_points)
        print(device_rf_params.rf_level)
        print(device_rf_params.rf2_freq)

if __name__ == '__main__':
    sc5511A = SC5511A(serialNumber = 10002657)
    sc5511A.start()
    sc5511A.setValues({'rf1_freq': 1e9})
    sc5511A.getValues()