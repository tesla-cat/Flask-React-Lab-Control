
import scipy
from scipy.sparse.linalg import expm
from scipy.special import factorial
import numpy as np
import functools
import matplotlib.pyplot as plt
import h5py, datetime

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

def com(C, D): return np.matmul(C, D) - np.matmul(D, C)
def dag(C): return np.conjugate(C).T

class Saver:
    def __init__(self, T, name):
        self.T = T; self.name = name
        self.goal0 = 10.
    def save(self, goal0, goal1, grad1, p):
        print('%.0e[%.0e]' % (goal0, goal1), end=' ')
        self.goal0 = goal0; self.goal1 = goal1; self.grad1 = grad1; self.p = p
    def save2(self, msg):
        print(msg)
        self.msg = msg
    def show(self):
        pltCtrl(self.p, self.T, 'optimized pulse infidelity = %.1e' % self.goal0)
        pltCtrl(self.grad1, self.T, 'gradient of cost function')
        f = h5py.File("pulse-%s.hdf5" % self.name, "w")
        f.create_dataset("p", data=self.p)
        f.create_dataset("goal", data=self.goal0)
        f.create_dataset("T", data=self.T)
        f.close()

def costf(p):
    dp = p - np.roll(p, -1, axis=1)
    goal1 = np.sum( dp**2 )
    grad1 = 2 * ( dp - np.roll(dp, 1, axis=1) )
    return goal1, grad1

def grape(H0, Hcs, T, nT, psi0, psig, name, costWeight=1e-4):
    saver = Saver(T,name)
    p0 = np.ones([len(Hcs), nT])
    env = envf(nT)
    pltCtrl(p0*env, T, 'initial pulse')
    dt = T / nT
    H0, Hcs, psi0, psig = toNp(H0, Hcs, psi0, psig)
    print('old shapes: p0 {}\t\t H0 {}\t Hcs {}\t\t psi0 {}'.format(p0.shape, H0.shape, Hcs.shape, psi0.shape))
    p0new = p0[:,:,None,None]; Hcs = Hcs[:,None,:,:]
    print('new shapes: p0 {}\t H0 {}\t Hcs {}\t psi0 {}'.format(p0new.shape, H0.shape, Hcs.shape, psi0.shape))
    # fun
    def fun(x):
        p = x.reshape(p0.shape) * env
        goal1, grad1 = costf(p) 
        pNew = p[:,:,None,None]
        H = np.sum(H0 + pNew * Hcs, axis=0)
        U = np.array([expm(-1j * Ht * dt) for Ht in H])
        goal0, grad0 = gradFun(H, U)
        goal1 *= costWeight; grad1 *= costWeight
        if goal0 / saver.goal0 < 0.5: saver.save(goal0, goal1, grad1, p)
        goal, grad = goal0 + goal1, ( (grad0+grad1) * env ).flatten()
        return goal, grad
    # gradFun
    M = 4; coefs = []
    for m in range(M): coefs.append( (1j*dt)**(m+1)/factorial(m+1) )
    def pcUt(Ht, Hci):
        coms = [Hci]; pcUt = coefs[0] * coms[0]
        for m in range(1, M):
            coms.append( com(Ht, coms[m-1]) )
            pcUt += coefs[m]*coms[m]
        return pcUt
    psigDag = dag(psig)
    psig2 = np.abs(np.sum( np.matmul( psigDag, psig ) ))
    def gradFun(H, U):
        future = [ np.matmul(psigDag, U[-1]) ]; past = [ np.matmul(U[0], psi0) ]; grad = []
        for t in range(1, nT):
            future.append( np.matmul( future[t-1], U[nT-1-t] ) )  
            past.append( np.matmul( U[t], past[t-1] ) )
            # when t = nT-1, future[-1] = ...U[0], past[-1] = U[nT-1]...
        # goal
        fidC = np.sum( np.matmul(future[0], past[nT-2]) ) / psig2
        fid = np.abs(fidC) 
        for t in range(nT):
            F = future[nT-1-t]
            P = past[t-1] if t > 0 else psi0
            grad.append([ np.matmul(F, np.matmul( pcUt( H[t], Hci[0] ), P )) for Hci in Hcs])
        grad = np.sum(np.array(grad), axis=(2,3)) / psig2
        grad = (fidC.real * grad.real + fidC.imag * grad.imag) / fid
        return 1-fid, grad.T  # .T because of the for loop: [nT, lenHcs], should be [lenHcs, nT]
    # minimize
    try:
        s = scipy.optimize.minimize(fun, x0=p0.flatten(), method='L-BFGS-B', jac=True, options={
            'ftol': 1e-15, 'gtol': 1e-15,
        })
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

