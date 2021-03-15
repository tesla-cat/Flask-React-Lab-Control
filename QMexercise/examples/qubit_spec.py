from configuration import config
from qm.qua import *
from qm import SimulationConfig
import numpy as np
import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager

###############
# rr_spec_prog:
###############

f_min = 37e6
f_max = 43e6
df = 0.2e6


with program() as qubit_spec:

    ##############################
    # declare real-time variables:
    ##############################

    n = declare(int)        # Averaging
    f = declare(int)        # Frequencies
    I = declare(fixed)
    Q = declare(fixed)

    ###############
    # the sequence:
    ###############

    with for_(n, 0, n < 10, n + 1):

        with for_(f, f_min, f < f_max, f + df):

            update_frequency("qubit", f)
            play("saturation", "qubit")

            align("qubit", "rr")
            measure("readout", "rr", None, demod.full("integW1", I),
                                           demod.full("integW2", Q))

            save(I, "I")
            save(Q, "Q")


qmm = QuantumMachinesManager(host="18.193.150.71")
qm = qmm.open_qm(config)
job = qm.simulate(qubit_spec, SimulationConfig(50000))
samples = job.get_simulated_samples()
samples.con1.plot()
plt.show()