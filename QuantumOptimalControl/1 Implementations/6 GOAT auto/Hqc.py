
import numpy as np
from qutip import qeye, destroy, tensor, coherent

def Hqc(NQ, NC, drive, chi, kerrQ, kerrC):
    aC = tensor(qeye(NQ), destroy(NC)); aCd = aC.dag()
    aQ = tensor(destroy(NQ), qeye(NC)); aQd = aQ.dag()
    H0 = chi * aCd*aC * aQd*aQ 
    H0 += kerrQ/2 * aQd*aQd * aQ*aQ 
    H0 += kerrC/2 * aCd*aCd * aC*aC
    H0 *= (2*np.pi)
    drive *= (2*np.pi)
    xQ = drive * (aQ + aQd)
    yQ = drive * (aQ - aQd) * 1j
    xC = drive * (aC + aCd)
    yC = drive * (aC - aCd) * 1j
    Hcs = [xQ, yQ, xC, yC]
    return H0, Hcs

def cat(N, alpha):
    return (coherent(N, alpha) + coherent(N, -alpha)).unit()