
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
    def __init__(self, serialNumber, name=None):
        self.serialNumber = serialNumber
        self.start()
        
        self.name = name or 'SA124B: %d' % serialNumber
        self.data = {
            'freq': {'actions': ['set', 'get'], 'hint': 'type: number, unit: Hz, range: [%.2e, %.2e]' % (self.freq1, self.freq2) },
            'pow':  {'actions': ['set', 'get'], 'hint': 'type: number, unit: dB, range: %s' % ( str([self.pow1,  self.pow2]) ) },
        }
    
    def start(self):
        i = self.i = serNumToIdx[self.serialNumber]
        vnx.fnLMS_InitDevice(devices[i])
        self.freq1 = vnx.fnLMS_GetMinFreq(devices[i]) * 10
        self.freq2 = vnx.fnLMS_GetMaxFreq(devices[i]) * 10
        self.pow1 = vnx.fnLMS_GetMinPwr(devices[i]) * 0.25
        self.pow2 = vnx.fnLMS_GetMaxPwr(devices[i]) * 0.25
        return 'success', 0

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
            power = self.pow2 - vnx.fnLMS_GetPowerLevel(devices[i]) * 0.25
            res['pow'] = power
        return 'success', res

    def stop(self):
        result = vnx.fnLMS_CloseDevice(devices[i])
        status = 'success' if result == 0 else 'error'
        return status, result

if __name__ == '__main__':
    brick = LabBrick(serialNumber = 24352)
    brick.setValues({'freq': 7e9, 'pow': -12})
    print(brick.getValues())
    brick.stop()