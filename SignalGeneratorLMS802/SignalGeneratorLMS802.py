
import os
from ctypes import *

class SignalGeneratorsLMS802:
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        ddlPath = os.path.join(path, 'vnx_fmsynth.dll')

        self.vnx = WinDLL(ddlPath)
        self.vnx.fnLMS_SetTestMode(False)        
        DeviceIDArray = c_int * 20
        self.Devices = DeviceIDArray()
        self.numDevices = self.vnx.fnLMS_GetNumDevices()
        print(str(self.numDevices), ' device(s) found')
        dev_info = self.vnx.fnLMS_GetDevInfo(self.Devices)
        print('GetDevInfo returned', str(dev_info))

    def getDeviceInfo(self, index):
        if index >= self.numDevices:
            print('self.numDevices = %d' % self.numDevices)
            return
        ser_num = self.vnx.fnLMS_GetSerialNumber(self.Devices[0])
        print('Serial number:', str(ser_num))
        init_dev = self.vnx.fnLMS_InitDevice(self.Devices[0])
        print('InitDevice returned', str(init_dev))
        min_freq = self.vnx.fnLMS_GetMinFreq(self.Devices[0])
        max_freq = self.vnx.fnLMS_GetMaxFreq(self.Devices[0])
        min_freq_in_MHz = int(min_freq / 100000)
        max_freq_in_MHz = int(max_freq / 100000)
        print('Minimum output frequency for LMS device in MHz:', min_freq_in_MHz)
        print('Maximum output frequency for LMS device in MHz:', max_freq_in_MHz)
        min_power = self.vnx.fnLMS_GetMinPwr(self.Devices[0])
        max_power = self.vnx.fnLMS_GetMaxPwr(self.Devices[0])
        min_pow = min_power / 4
        max_pow = max_power / 4
        print('Minimum power for LMS device:', min_pow)
        print('Maximum power for LMS device:', max_pow)

    def setDeviceFreq(self, index, freq): 
        Hz = freq * 1000000
        frequency = Hz / 10
        result = self.vnx.fnLMS_SetFrequency(self.Devices[index], int(frequency))
        if result != 0:
            print('SetFrequency returned error', result)
    
    def setDevicePower(self, index, freq): 
        pass


print('Enter desired power level in db: ', end = '')

# This is what allows the user to enter in the desired power for the LMS device
power = float(input())

# Tis loop prevents the user from entering a power outside of the device's range
while power > max_pow or power < min_pow:
    print('Enter a value between', min_pow,'and', max_pow,': ', end = '')
    power = float(input())
    
powerlevel = power / .25

# This sets the power for the LMS device
result_1 = self.vnx.fnLMS_SetPowerLevel(self.Devices[0], int(powerlevel))
if result_1 != 0:
    print('SetPowerLevel returned error', result_1)

print()

# These two functions get the output frequency and the power of the LMS device
result = self.vnx.fnLMS_GetFrequency(self.Devices[0])
result_1 = self.vnx.fnLMS_GetPowerLevel(self.Devices[0])


freq = (result * 10) / 1000000
power = (max_power - result_1) / 4

print('Output frequency for the LMS device:', freq)
print('Power level for LMS device:', power)

# This function closes the device
# You should always close the devie when finished with it
closedev = self.vnx.fnLMS_CloseDevice(self.Devices[0])
if closedev != 0:
    print('CloseDevice returned an error', closedev)
