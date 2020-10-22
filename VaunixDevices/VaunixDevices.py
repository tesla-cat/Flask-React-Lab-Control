
import os, json, ctypes

class VaunixDevices:
    def __init__(self, initValues={'freq': 6e9, 'pow': 6}):
        path = os.path.dirname(os.path.abspath(__file__))
        ddl = os.path.join(path, 'vnx_fmsynth.dll')
        self.vnx = ctypes.WinDLL(ddl)
        self.vnx.fnLMS_SetTestMode(False)
        self.devices = (ctypes.c_int*20)()
        self.numDevices = self.vnx.fnLMS_GetNumDevices()
        self.vnx.fnLMS_GetDevInfo(self.devices) # must do
        self.devicesData = [None for i in range(self.numDevices)]
        for i in range(self.numDevices):
            self.initDevice(i)
            self.getDeviceRange(i)
            self.setDeviceValue('freq', initValues['freq'], i)
            self.setDeviceValue('pow', initValues['pow'], i)
            self.getDeviceValues(i)
            self.stopDevice(i)
        print(self.devicesData)
    
    def initDevice(self, i=0):
        result = self.vnx.fnLMS_InitDevice(self.devices[i])
        status = 'success' if result == 0 else 'error'
        return status, result
    
    def getDeviceRange(self, i=0):
        freq1 = self.vnx.fnLMS_GetMinFreq(self.devices[i]) * 10
        freq2 = self.vnx.fnLMS_GetMaxFreq(self.devices[i]) * 10
        pow1 = self.vnx.fnLMS_GetMinPwr(self.devices[i]) * 0.25
        pow2 = self.vnx.fnLMS_GetMaxPwr(self.devices[i]) * 0.25
        self.devicesData[i] = {
            'freq':{'range': [freq1, freq2], 'unit': 'Hz'},
            'pow': {'range': [pow1 , pow2 ], 'unit': 'dB'},
        }
        return 'success', self.devicesData[i]

    def setDeviceValue(self, key, value, i=0):
        if key == 'freq':
            value = int(value / 10)
            result = self.vnx.fnLMS_SetFrequency(self.devices[i], value)
        else:
            pow2 = self.devicesData[i]['pow']['range'][1]
            value = int( (pow2-value) / 0.25)
            result = self.vnx.fnLMS_SetPowerLevel(self.devices[i], value)
        status = 'success' if result == 0 else 'error'
        return status, result
    
    def getDeviceValues(self, i=0):
        freq = self.vnx.fnLMS_GetFrequency(self.devices[i]) * 10
        power = self.vnx.fnLMS_GetPowerLevel(self.devices[i]) * 0.25
        self.devicesData[i]['freq']['value'] = freq
        self.devicesData[i]['pow']['value'] = power
        return 'success', {'freq': freq, 'pow': power}
    
    def stopDevice(self, i=0):
        result = self.vnx.fnLMS_CloseDevice(self.devices[i])
        status = 'success' if result == 0 else 'error'
        return status, result

vaunixDevices = VaunixDevices()
