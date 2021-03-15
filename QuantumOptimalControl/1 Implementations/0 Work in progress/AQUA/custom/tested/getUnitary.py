
import autograd.numpy as np
from qutip import sigmax, qeye, rand_herm, propagator, Qobj, fidelity

from .odeIntAutograd import odeInt

def getUnitary(U0, Ht, T):
    y0 = U0
    def fun(t, y):
        U = y
        H = Ht(t)
        ptU = -1j * np.dot( H, U )
        return ptU 
    y = odeInt(f=fun, x0=0, y0=y0, xT=T) 
    return y

def test1():
    U0 = np.array(qeye(2).full())
    sx = np.array(sigmax().full())
    def Ht(t):
        return sx
    T = np.pi
    U = getUnitary(U0, Ht, T)
    print(U)

def test2():
    N = 6
    U0 = qeye(N)
    U0np = np.array(U0.full())
    H0 = rand_herm(N)
    H0np = np.array(H0.full())
    def Ht(t, *args):
        return H0 * t
    def Htnp(t, *args):
        return H0np * t
    T = np.pi
    U1 = getUnitary(U0np, Htnp, T)
    U2 = propagator(Ht, T).full()
    diff = np.mean(np.abs(U1 - U2))
    print(diff)

def test3():
    for _ in range(10):
        test2()

if __name__ == '__main__':
    test1()
    test3()