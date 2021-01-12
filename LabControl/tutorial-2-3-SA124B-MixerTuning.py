
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from Instruments.SA124B.SA124B import SA124B
# qm
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import program, infinite_loop_, play
from configuration import config, qubit_IF, qubit_LO, IQ_imbalance

class MixerTuner:
    def __init__(self, carrier, sideBand, power):
        self.sa124B = SA124B(serialNumber = 19184645, mode = 'sweep')
        self.initQM()

        self.carrier = carrier
        self.sideBand = sideBand # pos / neg <=> upper / lower
        self.power = power
        
    def initQM(self):
        qmm = QuantumMachinesManager()
        self.qm = qmm.open_qm(config)
        with program() as hello_qua:
            with infinite_loop_():
                play("CW", "qubit")
        self.job = self.qm.execute(hello_qua)

    def step1CoarseSweep(self):
        self.qm.set_dc_offset_by_qe("qubit", "I", float(0))
        self.qm.set_dc_offset_by_qe("qubit", "Q", float(0))
        freqs, amps = self.sa124B.initSweep(self.carrier, self.sideBand*10, 100, self.power)
        plt.plot(freqs, amps)
        plt.show()

    def minimize(self, centers, spans, callback, amps, numIters=2, numGrids=[11, 11]):
        def minimizeIter(centers_, spans_):
            x = np.linspace(centers_[0]-spans_[0]/2, centers_[0]+spans_[0]/2, numGrids[0])
            y = np.linspace(centers_[1]-spans_[1]/2, centers_[1]+spans_[1]/2, numGrids[1])
            power = np.zeros(numGrids)
            for i, xi in enumerate(x):
                for j, yj in enumerate(y):
                    callback(xi, yj)
                    power[i, j] = self.sa124B.getSweepSingle(len(amps))
                    print(power[i, j], end=' ')
            fig = go.Figure( data=[go.Surface(z=power, x=x, y=y)] )
            fig.show()
            ind = np.unravel_index(np.argmin(power, axis=None), power.shape)
            minx, miny = x[ind[0]], y[ind[1]]
            return minx, miny
        for i in range(numIters):
            print('iter, centers, spans:', i, centers, spans)
            centers = minimizeIter(centers, spans)
            spans = spans / 2**i
        print('final centers:', centers)
            
    def step2CarrierLeakage(self):
        print('step2CarrierLeakage')
        _, amps = self.sa124B.initSweepSingle(center=self.carrier, power=self.power)
        def callback(I, Q):
            self.qm.set_dc_offset_by_qe("qubit", "I", float(I))
            self.qm.set_dc_offset_by_qe("qubit", "Q", float(Q))
        self.minimize(centers=[0,0], spans=[0.2, 0.2], callback=callback, amps=amps)
    
    def step3IqImbalance(self):
        print('step3IqImbalance')
        _, amps = self.sa124B.initSweepSingle(center=self.carrier+self.sideBand, power=self.power)
        def callback(gain, phase):
            self.qm.set_mixer_correction("mixer_qubit", qubit_IF, qubit_LO, IQ_imbalance(gain, phase))
        self.minimize(centers=[0,0], spans=[0.2, 0.2], callback=callback, amps=amps)

if __name__ == '__main__':
    mixerTuner = MixerTuner(carrier = 6e9, sideBand = 50e6, power = -30)
    
    mixerTuner.step1CoarseSweep()
    mixerTuner.step2CarrierLeakage()
    mixerTuner.step3IqImbalance()

    mixerTuner.sa124B.stop()