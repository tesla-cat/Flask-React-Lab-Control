
import numpy
import scipy
import autograd.numpy as np
import matplotlib.pyplot as plt
import autograd
from odeIntAutograd import odeInt

def dag(C): return np.conjugate(C).T

def toNp(H0, Hcs, psi0, psig):
    H0 = H0.full()
    Hcs = np.array([Hci.full() for Hci in Hcs])
    if isinstance(psi0, list):
        psi0 = np.array([ psik.full() for psik in psi0 ]).T[0]
        psig = np.array([ psik.full() for psik in psig ]).T[0]
    else:
        psi0 = psi0.full()
        psig = psig.full()
    return H0, Hcs, psi0, psig

class Saver:
    def __init__(self):
        self.goal = 10.
    def save(self, goal, a):
        print('%.0e' % goal, end=' ')
        self.goal = goal; self.a = a
    def save2(self, msg):
        print(msg)
        self.msg = msg

def goat(H0, Hcs, T, nT, U0, Ug, nC):
    saver = Saver()
    H0, Hcs, U0, Ug = toNp(H0, Hcs, U0, Ug)
    a0 = np.ones([ len(Hcs), nC, 3 ])
    a0[:,:,1] /= T
    #=====================================
    mu = T/2
    env0 = np.exp( -0.5 * ( (0-mu)/T )**2 ) - 1e-3
    def envf(t):
        return np.exp( -0.5 * ( (t-mu)/T )**2 ) - env0
    pltCtrl(a0, T, nT, 'initial pulse', envf)
    def HpaHtf(a, t):
        s0, s1, s2 = a[:,:,0], a[:,:,1], a[:,:,2]
        c1 = np.sin(s1 * t + s2)
        env = envf(t)
        p = np.sum( s0*c1 , axis=1)
        H = H0 + np.sum( env * p[:,None,None] * Hcs , axis=0)
        return H
    def UpaUf(a):
        def func(t, U):
            H = HpaHtf( a, t )
            ptU = -1j * np.matmul( H, U )
            return ptU
        U = odeInt(func, x0=0, y0=U0, xT=T)
        return U
    UgDag = dag(Ug)
    UgUg = np.abs( np.sum(np.matmul( UgDag, Ug )) )
    def goalFun(x):
        a = x.reshape( a0.shape )
        U = UpaUf( a )
        fidC = np.sum(np.matmul( UgDag, U )) / UgUg
        fid = np.abs(fidC)
        goal = 1-fid
        if goal / saver.goal < 0.5: saver.save(goal, a)
        return goal
    autogradFun = autograd.grad( goalFun )
    def fun(x):        
        goal = numpy.array(goalFun(x), dtype=numpy.float64)
        grad = numpy.array(autogradFun(x).flatten(), dtype=numpy.float64)
        return goal, grad
    try:
        s = scipy.optimize.minimize(fun, x0=a0.flatten(), method='L-BFGS-B', jac=True, options={
            'ftol': 1e-15, 'gtol': 1e-15,
        })
        saver.save2(s.message)
    except KeyboardInterrupt:
        pass
    pltCtrl(saver.a, T, nT, 'optimized pulse infidelity = %.0e' % saver.goal, envf)

def pltCtrl(a, T, nT, name, envf):
    plt.title(name)
    t = np.linspace(0, T, nT)
    s0, s1, s2 = a[:,:,0,None], a[:,:,1,None], a[:,:,2,None]
    p = envf(t) * np.sum( s0 * np.sin(s1 * t + s2), axis=1)
    for pc in p:
        plt.plot(t, pc)
    plt.show()