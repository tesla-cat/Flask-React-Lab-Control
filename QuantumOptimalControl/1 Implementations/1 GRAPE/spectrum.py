
import numpy as np
from scipy.fftpack import fft
import h5py, os
import matplotlib.pyplot as plt

def spectrum(name, amp0 = 1e-2):
    h5f = h5py.File( os.path.join( os.path.dirname(os.path.realpath(__file__)), name ) ,'r')
    p, goal, T = h5f['p'][:], h5f['goal'][()], h5f['T'][()]
    h5f.close()
    N = p.shape[1]
    dt = T/N
    t = np.linspace(0, T, N)
    pfft = 2/N * np.abs(fft(p)[:, :N//2])
    tfft = np.linspace(0, 1/(2*dt), N//2)
    _, axs = plt.subplots(p.shape[0], 2, figsize=(12, p.shape[0]*3))
    for i in range(p.shape[0]):
        axs[i,0].plot(t, p[i], '.')
        axs[i,1].plot(tfft, pfft[i], '.')
        axs[i,1].title.set_text( '%d components amp > %.0e' % (np.sum(pfft[i]>amp0), amp0) )
    plt.tight_layout()
    plt.show()
