
import autograd.numpy as np
import autograd
import scipy
from odeIntAutograd import odeInt

def prod(C,D): return np.abs(np.sum( np.conjugate(C) * D ))

def minimize(U0, Ug, T, H0, Hcs, a0):
    # fidelity  
    UgUg = prod(Ug, Ug)
    # envelope
    mu = T/2; sig = T/4
    gau0 = np.exp(-0.5*( -mu/sig )**2) - 1e-6
    # goal
    def goalFunc(a):
        def f(t, U):
            a0 = a[:,:,0]; a1 = a[:,:,1]; a2 = a[:,:,2]
            c = a0 * np.sin( 2*np.pi * a1 * t + a2 )
            gau = np.exp(-0.5*( (t-mu)/sig )**2)
            c = np.sum( c, axis= 1 ) * (gau - gau0)
            H = H0 + sum([ c[i]*Hci for i, Hci in enumerate(Hcs) ])
            return -1j * np.dot( H, U )
        U = odeInt(f, x0=0, y0=U0, xT=T)
        return 1 - prod(Ug, U) / UgUg
    gradFunc = autograd.grad(goalFunc)
    shape = a0.shape
    def fun(x):
        a = x.reshape(shape)
        goal = goalFunc(a)
        grad = gradFunc(a).flatten()
        print('%.0e'%goal, end=' ')
        return goal, grad
    scipy.optimize.minimize(fun, x0=a0.flatten(), jac=True, method='L-BFGS-B')