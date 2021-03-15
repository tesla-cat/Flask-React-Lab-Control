from configuration import config
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import SimulationConfig
import matplotlib.pyplot as plt

N = 1000
th = -0.1

with program() as active_reset:

    n = declare(int)

    I = declare(fixed)
    I_stream = declare_stream()

    Q = declare(fixed)
    Q_stream = declare_stream()

    measure('readout', 'rr', None, demod.full('integW1', I))

    with for_(n, 0, n < 3, n + 1):

            play("pi", "qubit", condition=I > th)
            align('qubit', 'rr')
            measure('readout', 'rr', None, demod.full('integW1', I), demod.full('integW2', Q))

            save(I, I_stream)
            save(Q, Q_stream)

    with stream_processing():

        I_stream.save_all("I")
        Q_stream.save_all("Q")


qmm = QuantumMachinesManager(host="18.193.150.71")
qm = qmm.open_qm(config)
job = qm.simulate(active_reset, SimulationConfig(2000))
samps = job.get_simulated_samples()
I_q1 = samps.con1.analog.get('1')
Q_q1= samps.con1.analog.get('2')
I_rr1 = samps.con1.analog.get('3')
Q_rr1 = samps.con1.analog.get('4')
fig, axes = plt.subplots(4)
axes[0].plot(I_q1)
axes[1].plot(Q_q1)
axes[2].plot(I_rr1)
axes[3].plot(Q_rr1)
plt.tight_layout()
plt.show()
