
import autograd.numpy as np
import matplotlib.pyplot as plt

def getCtrl(a, t, T):
    a0 = a[:,:,0]; a1 = a[:,:,1]; a2 = a[:,:,2]
    c = a0 * np.sin( 2*np.pi * a1 * t + a2 )
    c = np.sum( c, axis= 1 )
    env = getEnvelope(t,T)
    return c * env

def getZero(T):
    mu = T/2; sig = T/4
    return np.exp(-0.5*( -mu/sig )**2)

def getEnvelope(t,T):
    mu = T/2; sig = T/4
    gau = np.exp(-0.5*( (t-mu)/sig )**2)
    return gau - getZero(T)

def pltCtrl(a, T):
    ctrls = []
    ts = np.linspace(0, T, 1000)
    for t in ts:
        ctrls.append(getCtrl(a, t, T))
    ctrls = np.array(ctrls).T
    for ctrl in ctrls:
        plt.plot(ts, ctrl)
    plt.show()

def test():
    a = np.array([
        [ [1, 5, 0.3*np.pi] ],
        [ [2, 4, 0.5*np.pi] ],
    ])
    T = 1
    pltCtrl(a, T)

if __name__ == '__main__':
    test()