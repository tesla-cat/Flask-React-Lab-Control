
import time, json, pickle
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from Instruments.SA124B.SA124B import SA124B
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import program, infinite_loop_, play
from configuration import config, qubit_IF, qubit_LO, IQ_imbalance
import plotly.graph_objects as go
from datetime import datetime

class MixerTuner:
    def __init__(self, saveName):
        self.sa124B = SA124B(serialNumber = 19184645, mode = 'sweep')
        self.initQM()
        self.saveName = saveName

        self.carrier = 6e9
        self.sideBand = 50e6
        # a positive sideband frequency corresponds to tuning the upper sideband
        
    def initQM(self):
        qmm = QuantumMachinesManager()
        self.qm = qmm.open_qm(config)
        with program() as hello_qua:
            with infinite_loop_():
                play("CW", "qubit")
        self.job = self.qm.execute(hello_qua)

    def step1CoarseSweep(self):
        self.qm.set_dc_offset_by_qe("qubit", "I", float(-0.02))
        self.qm.set_dc_offset_by_qe("qubit", "Q", float(0))
        freqs, amps = self.sa124B.initSweep(6e9, 500e6, 100, -30)
        plt.plot(freqs, amps)
        plt.show()

    def step2CarrierLeakage(self):
        minI, minQ, span0 = 0, 0, 0.2
        def getRange(center, span):
            return [center-span/2, center+span/2]
        for i in range(2):
            span = span0 / 2**i
            Irange, Qrange = getRange(minI, span), getRange(minQ, span)
            print("Irange, Qrange, minI, minQ:", Irange, Qrange, minI, minQ)
            minI, minQ = self.step2CarrierLeakageOneIter(Irange, Qrange, i)
        print('final minI, minQ', minI, minQ)
            
    def step2CarrierLeakageOneIter(self, Irange, Qrange, iteration):
        _, amps = self.sa124B.initSweepSingle(center=self.carrier, power=-30)
        print('sweep len:', len(amps))
        Ivals = np.linspace(Irange[0], Irange[1], 11)
        Qvals = np.linspace(Qrange[0], Qrange[1], 11)
        pows = np.zeros([len(Ivals), len(Qvals)])
        def save():
            with open('./MixerTunerData/%s-step2CarrierLeakage-iter%d.pkl' % (self.saveName, iteration), 'wb') as f:
                pickle.dump({"Ivals": Ivals, "Qvals": Qvals, "pows": pows}, f)
        for i, Ival in enumerate(Ivals):
            for q, Qval in enumerate(Qvals):
                self.qm.set_dc_offset_by_qe("qubit", "I", float(Ival))
                self.qm.set_dc_offset_by_qe("qubit", "Q", float(Qval))
                pows[i, q] = self.sa124B.getSweepSingle(len(amps))
                print(pows[i, q])
        save()
        return self.plotStep2(iteration)
    
    def plotStep2(self, iteration):
        fileName = './MixerTunerData/%s-step2CarrierLeakage-iter%d.pkl' % (self.saveName, iteration)
        with (open(fileName, "rb")) as f:
            data = pickle.load(f)
        fig = go.Figure( data=[go.Surface(z=data['pows'], x=data['Ivals'], y=data['Qvals'])] )
        fig.update_layout(title=fileName, scene=dict(
            xaxis=dict(title='Ivals'),
            yaxis=dict(title='Qvals'),
            zaxis=dict(title='pows')
        ))
        fig.show()
        ind = np.unravel_index(np.argmin(data['pows'], axis=None), data['pows'].shape)
        minI, minQ = data['Ivals'][ind[0]], data['Qvals'][ind[1]]
        self.qm.set_dc_offset_by_qe("qubit", "I", float(minI))
        self.qm.set_dc_offset_by_qe("qubit", "Q", float(minQ))
        return minI, minQ

    def step3IqImbalance(self):
        phaseVals = np.linspace(-0.1, 0.1, 11)
        gainVals = np.linspace(-0.1, 0.1, 1)
        pows = np.zeros([len(phaseVals), len(gainVals)])
        def save():
            with open('./MixerTunerData/%s-step3IqImbalance.pkl' % self.saveName, 'wb') as f:
                pickle.dump({"phaseVals": phaseVals, "gainVals": gainVals, "pows": pows}, f)
        for p, phase in enumerate(phaseVals):
            for g, gain in enumerate(gainVals):
                self.qm.set_mixer_correction("mixer_qubit", qubit_IF, qubit_LO, IQ_imbalance(gain, phase))
                #pows[p, g] = self.sa124B.sweepSingle(center=self.carrier+self.sideBand, power=-30)
                print(pows[p, g])
        save()
        return pows[p, g]

if __name__ == '__main__':
    mixerTuner = MixerTuner(saveName='test2')
    
    #mixerTuner.step1CoarseSweep()
    mixerTuner.step2CarrierLeakage()
    
    mixerTuner.sa124B.stop()