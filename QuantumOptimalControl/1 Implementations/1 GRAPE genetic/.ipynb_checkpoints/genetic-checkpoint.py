
import scipy
from scipy.linalg import expm
import numpy as np
import functools
import matplotlib.pyplot as plt

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

def envf(nT):
    t = np.arange(nT)
    mu = (t[0]+t[-1]) / 2
    env = np.exp(-0.5* ( (t-mu)/nT )**2 )
    env -= env[0]
    return env[None,:] / env[nT//2]

def dag(C): return np.conjugate(C).T

class Saver:
    def __init__(self, T):
        self.T = T
        self.goal0 = 10.
    def save(self, goal0, goal1, p):
        print('%.0e[%.0e]' % (goal0, goal1), end=' ')
        self.goal0 = goal0; self.goal1 = goal1; self.p = p
    def save2(self, msg):
        print(msg)
        self.msg = msg
    def show(self):
        pltCtrl(self.p, self.T, 'optimized pulse infidelity = %.1e' % self.goal0)

def costf(p):
    dp = p - np.roll(p, -1, axis=1)
    goal1 = np.sum( dp**2 )
    return goal1

def genetic(H0, Hcs, T, nT, psi0, psig, costWeight=1e-4, bound = 10.):
    saver = Saver(T)
    p0 = np.ones([len(Hcs), nT])
    env = envf(nT)
    pltCtrl(p0*env, T, 'initial pulse')
    dt = T / nT
    H0, Hcs, psi0, psig = toNp(H0, Hcs, psi0, psig)
    print('old shapes: p0 {}\t\t H0 {}\t Hcs {}\t\t psi0 {}'.format(p0.shape, H0.shape, Hcs.shape, psi0.shape))
    p0new = p0[:,:,None,None]; Hcs = Hcs[:,None,:,:]
    print('new shapes: p0 {}\t H0 {}\t Hcs {}\t psi0 {}'.format(p0new.shape, H0.shape, Hcs.shape, psi0.shape))
    # fun
    def goalFun(x):
        p = x.reshape(p0.shape) * env
        goal1 = costf(p) 
        pNew = p[:,:,None,None]
        H = np.sum(H0 + pNew * Hcs, axis=0)
        U = np.array([expm(-1j * Ht * dt) for Ht in H])
        goal0 = gradFun(H, U)
        goal1 *= costWeight
        if goal0 / saver.goal0 < 0.5: saver.save(goal0, goal1, p)
        return goal0 + goal1
    # gradFun
    psigDag = dag(psig)
    psig2 = np.abs(np.sum( np.dot( psigDag, psig ) ))
    def gradFun(H, U):
        future = [ np.dot(psigDag, U[-1]) ]; past = [ np.dot(U[0], psi0) ]
        for t in range(1, nT):
            past.append( np.dot( U[t], past[t-1] ) )
            # when t = nT-1, future[-1] = ...U[0], past[-1] = U[nT-1]...
        # goal
        fidC = np.sum( np.dot(future[0], past[nT-2]) ) / psig2
        fid = np.abs(fidC) 
        return 1-fid
    def fun(x):
        goal = goalFun(x)
        return goal
    # minimize
    try:
        bounds = [ (-bound, bound) for i in range(p0.flatten().shape[0])]
        s = scipy.optimize.differential_evolution(fun, bounds)
        saver.save2(s.message)
    except KeyboardInterrupt:
        pass
    saver.show()

def pltCtrl(p, T, name):
    plt.title(name)
    t = np.linspace(0, T, p.shape[1])
    for pc in p:
        plt.plot(t, pc)
    plt.show()

