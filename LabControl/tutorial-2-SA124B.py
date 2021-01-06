
import rpyc

from scipy.signal import get_window
import numpy as np
import matplotlib.pyplot as plt

# ========== simple plot functions ==========
def dBm(x): return 10 * np.log10(x)

def plotIQ(val):
    IQ = np.array(val['IQ'])
    f1 = center_span[0] - center_span[1] / 2
    f2 = center_span[0] + center_span[1] / 2
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

def plotSweep(val):
    sweep = np.array(val['sweep']['max'])
    info = val['sweep_info']
    freqs = [info["start_freq"] + i * info["bin_size"] for i in range(info["sweep_length"])]
    plt.plot(freqs, sweep)
    plt.show()

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

# ========== example 1: IQ mode ==========
sa124B_IQ = Instruments.SA124B(serialNumber = 19184645, mode = 'IQ')
center_span = [869.0e6, 1.0e3]
sa124B_IQ.setValues({
    'center_span': center_span, 'level': -10.0, 'IQ': [1, 250.0e3]
})
sa124B_IQ.start()
plotIQ( sa124B_IQ.getValues()[1] )
sa124B_IQ.stop()

# ========== example 2: sweep mode ==========
"""
sa124B_sweep = Instruments.SA124B(serialNumber = 19184645, mode = 'sweep')
sa124B_sweep.setValues({
    'center_span': [1e9, 100e6], 'level': -30.0, 
    'sweep_coupling': [10e3, 10e3, 0], 'acquisition': [0, 0],
})
sa124B_sweep.start()
plotSweep( sa124B_sweep.getValues()[1] )
sa124B_sweep.stop()
"""