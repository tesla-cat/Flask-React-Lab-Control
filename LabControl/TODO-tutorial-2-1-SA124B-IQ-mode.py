
import rpyc
from scipy.signal import get_window
import numpy as np
import matplotlib.pyplot as plt
import json

r"""
please read Instruments\SA124B\SA-API-Manual.pdf
please read Instruments\SA124B\SA-API-Manual.pdf
please read Instruments\SA124B\SA-API-Manual.pdf
"""

def dBm(x): return 10 * np.log10(x)
def plotIQ(val):
    IQ = np.array(val['IQ'])
    f1 = freqCenter - 250e3
    f2 = freqCenter + 250e3
    freq = np.linspace(f1, f2, len(IQ)) 
    window = get_window('hamming', len(IQ))
    window *= len(window) / sum(window)
    fft = np.fft.fftshift(np.fft.fft(IQ * window) / len(window))
    power = dBm( fft.real ** 2 + fft.imag ** 2 )
    plt.plot(freq, power)
    plt.title("This example configures the receiver for IQ acquisition and\n plots the spectrum of a single IQ acquisition.")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("FFT power [dBm]")
    plt.show()

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

# ========== shared parameters by LabBrick and SA124B ==========
powerLevel = 10
freqCenter = 6e9

# ========== LabBrick ==========
brick = Instruments.LabBrick(serialNumber = 24352)
brick.setValues({'freq': freqCenter , 'pow': powerLevel})
print(brick.getValues())

# ========== example 1: IQ mode ==========
sa124B_IQ = Instruments.SA124B(serialNumber = 19184645, mode = 'IQ')
print(json.dumps(sa124B_IQ.data, indent=4))
sa124B_IQ.setValues({
    'center_span': [freqCenter, 1e6], 'level': powerLevel, 'IQ_config': [1, 250e3]
})
sa124B_IQ.start()
plotIQ( sa124B_IQ.getValues()[1] )
sa124B_IQ.stop()
brick.stop()
