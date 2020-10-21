
import os, json, ctypes

class VaunixDevices:
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        ddl = os.path.join(path, 'vnx_fmsynth.dll')
        vnx = ctypes.WinDLL(ddl)
        vnx.fnLMS_SetTestMode(False)        
        DeviceIDArray = ctypes.c_int * 20
        Devices = DeviceIDArray()           
        numDevices = vnx.fnLMS_GetNumDevices()
        dev_info = vnx.fnLMS_GetDevInfo(Devices)
        #print('GetDevInfo returned', str(dev_info))
        self.vnx = vnx; self.Devices = Devices; self.numDevices = numDevices
        self.devicesInfo = []
        for i in range(numDevices):
            self.initDevice(i)
        print(self.devicesInfo)

    def initDevice(self, index):
        vnx = self.vnx; Devices = self.Devices; numDevices = self.numDevices
        if index >= numDevices: return 'error', 'index out of range'
        ser_num = vnx.fnLMS_GetSerialNumber(Devices[index])
        init_dev = vnx.fnLMS_InitDevice(Devices[index])
        #print('InitDevice %d returned' % index, str(init_dev))
        min_freq = vnx.fnLMS_GetMinFreq(Devices[index])
        max_freq = vnx.fnLMS_GetMaxFreq(Devices[index])
        min_freq_in_MHz = int(min_freq / 100000)
        max_freq_in_MHz = int(max_freq / 100000)
        min_power = vnx.fnLMS_GetMinPwr(Devices[index])
        max_power = vnx.fnLMS_GetMaxPwr(Devices[index])
        min_pow = min_power / 4
        max_pow = max_power / 4
        deviceInfo = {
            'type': 'VaunixDevice', 
            'info': {'serialNumber': ser_num},
            'values':{
                'frequency': {'unit': 'MHz', 'range': [min_freq_in_MHz, max_freq_in_MHz]},
                'power': {'unit': 'db', 'range': [min_pow, max_pow]},
            },
        }
        self.devicesInfo.append(deviceInfo)
    
    def setDevice(self, index, name, value):
        vnx = self.vnx; Devices = self.Devices; numDevices = self.numDevices
        if index >= numDevices: return 'error', 'index out of range'
        if name == 'frequency':
            freq = value
            Hz = freq * 1000000
            frequency = Hz / 10
            result = vnx.fnLMS_SetFrequency(Devices[index], int(frequency))
        elif name == 'power':
            power = value
            powerlevel = power / .25
            result = vnx.fnLMS_SetPowerLevel(Devices[index], int(powerlevel))
        status = 'success' if result == 0 else 'error'
        print(status, result)
        return status, result

    def getDevice(self, index):
        vnx = self.vnx; Devices = self.Devices; numDevices = self.numDevices
        if index >= numDevices: return 'error', 'index out of range'
        result = vnx.fnLMS_GetFrequency(Devices[index])
        result_1 = vnx.fnLMS_GetPowerLevel(Devices[index])
        freq = (result * 10) / 1000000
        power = (self.devicesInfo[index]['values']['power']['range'][1]*4 - result_1) / 4
        res = {'frequency': freq, 'power': power}
        print(res)
        return res

    def stopDevice(self, index):
        vnx = self.vnx; Devices = self.Devices; numDevices = self.numDevices
        if index >= numDevices: return 'error', 'index out of range'
        result = vnx.fnLMS_CloseDevice(Devices[index])
        status = 'success' if result == 0 else 'error'
        print(status, result)
        return status, result

vaunixs = VaunixDevices()
status, result = vaunixs.setDevice(0, 'frequency', 6e3)
status, result = vaunixs.setDevice(0, 'power', 10)
result = vaunixs.getDevice(0)
status, result = vaunixs.stopDevice(0)
