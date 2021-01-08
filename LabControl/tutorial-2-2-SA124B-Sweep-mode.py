
import rpyc
from scipy.signal import get_window
import numpy as np
import matplotlib.pyplot as plt
import json
from Instruments.SA124B.SA124B import SA_MIN_MAX, SA_LOG_SCALE, SA124Bdoc

r"""
please read Instruments\SA124B\SA-API-Manual.pdf
please read Instruments\SA124B\SA-API-Manual.pdf
please read Instruments\SA124B\SA-API-Manual.pdf
"""

def plotSweep(val):
    sweep = np.array(val['sweep']['max'])
    info = val['sweep_info']
    freqs = [info["start_freq"] + i * info["bin_size"] for i in range(info["sweep_length"])]
    plt.plot(freqs, sweep)

def extractSingleFreqFromSweep(val, freq):
    sweep = np.array(val['sweep']['max'])
    info = val['sweep_info']
    freqs = [info["start_freq"] + i * info["bin_size"] for i in range(info["sweep_length"])]
    for idx, f in enumerate(freqs):
        if f > freq:
            return sweep[idx]
    

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

# ========== shared parameters by LabBrick and SA124B ==========
print(SA124Bdoc)
center_Hz, span_Hz = 6e9, 1e6
ref_level_dBm = 5
# Available RBWs are [0.1Hz – 100kHz] and 250kHz, 6MHz 
# For best performance use RBW as the VBW.
resolution_bandwidth_Hz = video_bandwidth_Hz = 1e3

# ========== LabBrick ==========
#brick = Instruments.LabBrick(serialNumber = 24352)
#brick.setValues({'freq': center_Hz , 'pow': ref_level_dBm})

# ========== example 2: sweep mode ==========
sa124B_sweep = Instruments.SA124B(serialNumber = 19184645, mode = 'sweep')
sa124B_sweep.setValues({
    'center_span': [center_Hz, span_Hz], 
    'level': ref_level_dBm, 
    'sweep_coupling': [ resolution_bandwidth_Hz, video_bandwidth_Hz, 0], 
    'acquisition': [SA_MIN_MAX, SA_LOG_SCALE],
})
sa124B_sweep.start()
for i in range(10):
    val = sa124B_sweep.getValues()[1]
    plotSweep( val )
    powAtCenter = extractSingleFreqFromSweep(val, center_Hz)
    print(powAtCenter)
plt.show()
sa124B_sweep.stop()
#brick.stop()

