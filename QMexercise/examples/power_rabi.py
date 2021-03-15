from configuration import config
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
import numpy as np
import matplotlib.pyplot as plt

##################
# power_rabi_prog:
##################

a_min = 0.0
a_max = 1.0
da = 0.1


with program() as power_rabi:

    ##############################
    # declare real-time variables:
    ##############################

    n = declare(int)        # Averaging
    a = declare(fixed)      # Amplitudes
    I = declare(fixed)
    Q = declare(fixed)

    ###############
    # the sequence:
    ###############

    with for_(n, 0, n < 10, n + 1):

        with for_(a, a_min, a < a_max, a + da):

            play("gaussian" * amp(a), "qubit")

            align("qubit", "rr")
            measure("readout", "rr", None, demod.full("integW1", I),
                                           demod.full("integW2", Q))

            save(I, "I")
            save(Q, "Q")


qmm = QuantumMachinesManager(host="18.193.150.71")
qm = qmm.open_qm(config)
job = qm.simulate(power_rabi, SimulationConfig(5000))
samples = job.get_simulated_samples()
samples.con1.plot()
plt.show()