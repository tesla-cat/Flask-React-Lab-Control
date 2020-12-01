
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
#print(serNumToIdx)

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

    def setValues(self, dic):
        i = self.i 
        result = 0
        if 'freq' in dic:
            result |= vnx.fnLMS_SetFrequency(devices[i], int(dic['freq'] / 10))
        if 'pow' in dic:
            result |= vnx.fnLMS_SetPowerLevel(devices[i], int(dic['pow'] / 0.25))
        status = 'success' if result == 0 else 'error'
        return status, result
    
    def getValues(self, keys=['freq', 'pow']):
        i = self.i
        res = {}
        if 'freq' in keys:
            freq = vnx.fnLMS_GetFrequency(devices[i]) * 10
            res['freq'] = freq
        if 'pow' in keys:
            pow2 = self.data['pow']['range'][1]
            power = pow2 - vnx.fnLMS_GetPowerLevel(devices[i]) * 0.25
            res['pow'] = power
        return 'success', res

    def stop(self):
        result = vnx.fnLMS_CloseDevice(devices[i])
        status = 'success' if result == 0 else 'error'
        return status, result

if __name__ == '__main__':
    brick = LabBrick(serialNumber = 24352)
    print(brick.data)
    brick.setValues({'freq': 7e9, 'pow': -12})
    print(brick.getValues())
    brick.stop()