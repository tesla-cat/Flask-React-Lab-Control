
import time
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from Instruments.SA124B.SA124B import SA124B
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import program, infinite_loop_, play
from configuration import config, qubit_IF, qubit_LO, IQ_imbalance

class MixerTuner:
    def __init__(self):
        self.sa124B = SA124B(serialNumber = 19184645, mode = 'sweep')
        self.initQM()
        
    def initQM(self):
        qmm = QuantumMachinesManager()
        self.qm = qmm.open_qm(config)
        with program() as hello_qua:
            with infinite_loop_():
                play("CW", "qubit")
        self.job = self.qm.execute(hello_qua)

    def step1CoarseSweep(self):
        freqs, amps = self.sa124B.sweep(6e9, 1e3, 100, -30)
        plt.plot(freqs, amps)
        plt.show()

    def step2CarrierLeakage(self):
        Ivals = np.linspace(-0.2, 0.1, 10)
        Qvals = np.linspace(-0.2, 0.1, 1)
        pows = np.zeros([len(Ivals), len(Qvals)])
        for i, Ival in enumerate(Ivals):
            for q, Qval in enumerate(Qvals):
                #while not self.job.is_paused():
                    #time.sleep(5)
                #=====================
                self.qm.set_dc_offset_by_qe("qubit", "I", float(Ival))
                self.qm.set_dc_offset_by_qe("qubit", "Q", float(Qval))
                pows[i, q] = self.sa124B.sweepSingle(center=6e9, power=-30)
                print(pows[i, q])
                #=====================
                #self.job.resume()
                #time.sleep(5)
        plt.plot(Ivals, pows[:, 0])
        plt.show()
        return pows

"""
    def step3IqImbalance(self):
        phaseVals = np.linspace(-0.2, 0.1, 11)
        gainVals = np.linspace(-0.2, 0.1, 11)
        powLs = np.zeros([len(phaseVals), len(gainVals)])
        powHs = np.zeros([len(phaseVals), len(gainVals)])
        for p, phase in enumerate(phaseVals):
            for g, gain in enumerate(gainVals):
                self.qm.set_mixer_correction("mixer_qubit", qubit_IF, qubit_LO, IQ_imbalance(gain, phase))
                time.sleep(1)
                val = self.sa124B.getValues()[1]
                #freqs, amps = getFreqsAndAmps(val)
                #newAmps = interpolateAmps(freqs, amps, [6e9 - 50e3, 6e9 + 50e3])
                print(newAmps)
                powLs[p, g] = newAmps[0]
                powHs[p, g] = newAmps[1]
        plt.pcolormesh(phaseVals, gainVals, powLs)
        plt.show()
        plt.pcolormesh(phaseVals, gainVals, powHs)
        plt.show()
        return powLs, powHs
"""

if __name__ == '__main__':
    mixerTuner = MixerTuner()
    
    mixerTuner.step1CoarseSweep()
    mixerTuner.step2CarrierLeakage()
    
    mixerTuner.sa124B.stop()