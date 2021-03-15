
import autograd.numpy as np
from qutip import qeye, sigmax, sigmay, tensor, fock
from tested.getCtrl import getCtrl, pltCtrl
from tested.getFid import getFid
from tested.minimize import minimize

a0 = np.ones([2, 6, 3])
T = np.pi
sx = np.array(sigmax().full())
sy = np.array(sigmay().full())
U0 = np.array(qeye(2).full())
Ugoal = sx
Hcs = [sx, sy]
def Hat(a,t):
    c = getCtrl(a, t, T)
    return sum([ c[i]*Hcs[i] for i in range(len(Hcs)) ])
def goalFunc(U):
    return 1 - getFid(U, Ugoal)
a = minimize(a0, U0, Hat, T, goalFunc)
pltCtrl(a, T)