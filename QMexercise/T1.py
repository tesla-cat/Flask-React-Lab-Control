from configuration import config
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import SimulationConfig
import matplotlib.pyplot as plt

with program() as experiment:
    I = declare(fixed); I_stream = declare_stream()
    Q = declare(fixed); Q_stream = declare_stream()

    n = declare(int)
    t = declare(int)
    with for_(n, 0, n < 10, n + 1):
        with for_(t, 10, t < 1000, t + 10):
            play("pi", "qubit")
            wait(t, 'qubit', 'rr')

            align('qubit', 'rr')
            measure('readout', 'rr', None, demod.full('integW1', I), demod.full('integW2', Q))
            save(I, I_stream)
            save(Q, Q_stream)

    with stream_processing():
        I_stream.save_all("I")
        Q_stream.save_all("Q")

qmm = QuantumMachinesManager(host="18.193.150.71")
qm = qmm.open_qm(config)
job = qm.simulate(experiment, SimulationConfig(2000))
samps = job.get_simulated_samples()

fig, axes = plt.subplots(4)
labels = ['I_q1', 'Q_q1', 'I_rr1', 'Q_rr1']
for i in range(4):
    axes[i].plot(samps.con1.analog.get(str(i+1)))
    axes[i].set_title(labels[i])
plt.tight_layout()
plt.show()
