import time
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from Instruments.SA124B.SA124B import SA124B
# qm
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import program, infinite_loop_, play
from configuration import config, qubit_IF, qubit_LO, IQ_imbalance
from scipy.optimize import minimize

class MixerTuner:
    def __init__(self, carrier, sideBand, power, sa124B, qm):
        self.sa124B = sa124B
        self.qm = qm
        self.carrier = carrier
        self.sideBand = sideBand # pos / neg <=> upper / lower
        self.power = power

    def step1CoarseSweep(self, I=0, Q=0, gain=0, phase=0, span=500e6, N=100):
        self.qm.set_dc_offset_by_qe("qubit", "I", float(I))
        self.qm.set_dc_offset_by_qe("qubit", "Q", float(Q))
        self.qm.set_mixer_correction("mixer_qubit", qubit_IF, qubit_LO, IQ_imbalance(gain, phase))
        freqs, amps = self.sa124B.initSweep(self.carrier, span, N, self.power)
        plt.figure()
        plt.plot(freqs, amps)

    def minimize(self, centers, spans, callback, amps, numIters, numGrids, shrink):
        spans = np.array(spans)
        def minimizeIter(centers_, spans_):
            x = np.linspace(centers_[0]-spans_[0]/2, centers_[0]+spans_[0]/2, numGrids[0])
            y = np.linspace(centers_[1]-spans_[1]/2, centers_[1]+spans_[1]/2, numGrids[1])
            power = np.zeros(numGrids)
            for i, xi in enumerate(x):
                for j, yj in enumerate(y):
                    callback(xi, yj)
                    power[i, j] = self.sa124B.getSweepSingle(len(amps))
            if numGrids[0] == 1:
                plt.plot(y, power[0, :])
                plt.show()
            elif numGrids[1] == 1:
                plt.plot(x, power[:, 0])
                plt.show()
            else:
                fig = go.Figure( data=[go.Surface(z=power, x=x, y=y)] )
                fig.show()
            ind = np.unravel_index(np.argmin(power, axis=None), power.shape)
            minx, miny = x[ind[0]], y[ind[1]]
            return minx, miny
        for i in range(numIters):
            print('iter, centers, spans:', i, centers, spans)
            centers = minimizeIter(centers, spans)
            spans = spans * shrink**(i+1)
        print('final centers:', centers)
        return centers
      
    def step2CarrierLeakage(self, centers, spans, numIters, numGrids, shrink):
        print('step2CarrierLeakage')
        _, amps = self.sa124B.initSweepSingle(center=self.carrier, power=self.power)
        def callback(I, Q):
            self.qm.set_dc_offset_by_qe("qubit", "I", float(I))
            self.qm.set_dc_offset_by_qe("qubit", "Q", float(Q))
        return self.minimize(centers, spans, callback, amps, numIters, numGrids, shrink)
    
    def step3IqImbalance(self, centers, spans, numIters, numGrids, shrink):
        print('step3IqImbalance')
        _, amps = self.sa124B.initSweepSingle(center=self.carrier+self.sideBand, power=self.power)
        def callback(gain, phase):
            self.qm.set_mixer_correction("mixer_qubit", qubit_IF, qubit_LO, IQ_imbalance(gain, phase))
        return self.minimize(centers, spans, callback, amps, numIters, numGrids, shrink)

if __name__ == '__main__':
    sa124B = SA124B(serialNumber = 19184645, mode = 'sweep')
    qmm = QuantumMachinesManager()
    qm = qmm.open_qm(config)
    with program() as hello_qua:
        with infinite_loop_():
            play("CW", "qubit")
    job = qm.execute(hello_qua)

    mixerTuner = MixerTuner(carrier = 6e9, sideBand = 50e6, power = 0, sa124B=sa124B, qm=qm)