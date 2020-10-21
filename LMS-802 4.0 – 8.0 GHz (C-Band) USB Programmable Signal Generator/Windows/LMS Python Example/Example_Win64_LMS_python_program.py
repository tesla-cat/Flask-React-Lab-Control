# This is an example program of how to use the Vaunix LMS DLL
# from python to control a single LMS device

from ctypes import *
#vnx= cdll.vnx_fmsynth
vnx = WinDLL(r"D:\GitHub\Django-React-Lab-Control\LMS-802 4.0 – 8.0 GHz (C-Band) USB Programmable Signal Generator\Windows\LMS Python Example\vnx_fmsynth.dll")
vnx.fnLMS_SetTestMode(False)        # Use actual devices
DeviceIDArray = c_int * 20
Devices = DeviceIDArray()           # This array will hold the list of device handles
                                    # returned by the DLL

# GetNumDevices will determine how many LMS devices are availible
numDevices = vnx.fnLMS_GetNumDevices()
print(str(numDevices), ' device(s) found')

# GetDevInfo generates a list, stored in the devices array, of
# every availible LMS device attached to the system
# GetDevInfo will return the number of device handles in the array
dev_info = vnx.fnLMS_GetDevInfo(Devices)
print('GetDevInfo returned', str(dev_info))

# GetSerialNumber will return the devices serial number
ser_num = vnx.fnLMS_GetSerialNumber(Devices[0])
print('Serial number:', str(ser_num))

#InitDevice wil prepare the device for operation
init_dev = vnx.fnLMS_InitDevice(Devices[0])
print('InitDevice returned', str(init_dev))

print()

# These functions will get the frequency range of the LMS device
# and those frequencies will be turned into MHz
min_freq = vnx.fnLMS_GetMinFreq(Devices[0])
max_freq = vnx.fnLMS_GetMaxFreq(Devices[0])
min_freq_in_MHz = int(min_freq / 100000)
max_freq_in_MHz = int(max_freq / 100000)
print('Minimum output frequency for LMS device in MHz:', min_freq_in_MHz)
print('Maximum output frequency for LMS device in MHz:', max_freq_in_MHz)


print('Enter desired output frequency in MHz: ', end = '')
# This is where the user can enter in the output frequency for the LMS device
freq = float(input())

# This prevents the user from entering an output frequency outside of
# the devices range
while freq > max_freq_in_MHz or freq < min_freq_in_MHz:
    print('Enter a value between', min_freq_in_MHz, 'and', max_freq_in_MHz,': ', end = '')
    freq = float(input())
    
Hz = freq * 1000000
frequency = Hz / 10

# This sets the output frequency for the LMS device
result = vnx.fnLMS_SetFrequency(Devices[0], int(frequency))
if result != 0:
    print('SetFrequency returned error', result)
    
print()

# These functions get the minimum and maximum power of the LMS device
min_power = vnx.fnLMS_GetMinPwr(Devices[0])
max_power = vnx.fnLMS_GetMaxPwr(Devices[0])

min_pow = min_power / 4
max_pow = max_power / 4
print('Minimum power for LMS device:', min_pow)
print('Maximum power for LMS device:', max_pow)
print('Enter desired power level in db: ', end = '')

# This is what allows the user to enter in the desired power for the LMS device
power = float(input())

# Tis loop prevents the user from entering a power outside of the device's range
while power > max_pow or power < min_pow:
    print('Enter a value between', min_pow,'and', max_pow,': ', end = '')
    power = float(input())
    
powerlevel = power / .25

# This sets the power for the LMS device
result_1 = vnx.fnLMS_SetPowerLevel(Devices[0], int(powerlevel))
if result_1 != 0:
    print('SetPowerLevel returned error', result_1)

print()

# These two functions get the output frequency and the power of the LMS device
result = vnx.fnLMS_GetFrequency(Devices[0])
result_1 = vnx.fnLMS_GetPowerLevel(Devices[0])


freq = (result * 10) / 1000000
power = (max_power - result_1) / 4

print('Output frequency for the LMS device:', freq)
print('Power level for LMS device:', power)

# This function closes the device
# You should always close the devie when finished with it
closedev = vnx.fnLMS_CloseDevice(Devices[0])
if closedev != 0:
    print('CloseDevice returned an error', closedev)
