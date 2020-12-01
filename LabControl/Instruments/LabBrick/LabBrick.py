
import os, json, ctypes

path = os.path.dirname(os.path.abspath(__file__))
vnx = ctypes.WinDLL(os.path.join(path, 'vnx_fmsynth.dll'))
vnx.fnLMS_SetTestMode(False)

devices = (ctypes.c_int*20)()
numDevices = vnx.fnLMS_GetNumDevices()
vnx.fnLMS_GetDevInfo(devices)
serNums = [ vnx.fnLMS_GetSerialNumber(devices[i]) for i in range(numDevices)]
serNumToIdx = {}
for i, serNum in enumerate(serNums): serNumToIdx[serNum] = i
print(serNumToIdx)

class LabBrick:
    def __init__(self, serialNumber):
        i = self.i = serNumToIdx[serialNumber]
        vnx.fnLMS_InitDevice(devices[i])
        freq1 = vnx.fnLMS_GetMinFreq(devices[i]) * 10
        freq2 = vnx.fnLMS_GetMaxFreq(devices[i]) * 10
        pow1 = vnx.fnLMS_GetMinPwr(devices[i]) * 0.25
        pow2 = vnx.fnLMS_GetMaxPwr(devices[i]) * 0.25
        self.data = {
            'freq':{'range': [freq1, freq2], 'unit': 'Hz'},
            'pow': {'range': [pow1 , pow2 ], 'unit': 'dB'},
        }

    def setValue(self, key, value):
        i = self.i
        if key == 'freq':
            value = int(value / 10)
            result = vnx.fnLMS_SetFrequency(devices[i], value)
        else:
            value = int(value / 0.25)
            result = vnx.fnLMS_SetPowerLevel(devices[i], value)
        status = 'success' if result == 0 else 'error'
        return status, result
    
    def getValues(self):
        i = self.i
        freq = vnx.fnLMS_GetFrequency(devices[i]) * 10
        pow2 = self.data['pow']['range'][1]
        power = pow2 - vnx.fnLMS_GetPowerLevel(devices[i]) * 0.25
        self.data['freq']['value'] = freq
        self.data['pow']['value'] = power
        return 'success', {'freq': freq, 'pow': power}

    def stop(self):
        result = vnx.fnLMS_CloseDevice(devices[i])
        status = 'success' if result == 0 else 'error'
        return status, result

if __name__ == '__main__':
    brick = LabBrick(serialNumber = 24352)
    print(brick.data)
    brick.setValue('freq', 6e9)
    brick.setValue('pow', -11)
    print(brick.getValues())
    brick.stop()