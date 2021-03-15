
import autograd.numpy as np
import autograd
import scipy
from qutip import qeye, sigmax, sigmay

from .getUnitary import getUnitary
from .getFid import getFid

def minimize(a0, U0, Hat, T, goalFunc):
    shape = a0.shape
    x0 = a0.flatten()
    def funToDiff(x):
        a = x.reshape(shape)
        def Ht(t):
            return Hat(a, t)
        U = getUnitary(U0, Ht, T)
        goal = goalFunc(U)
        return goal
    gradFun = autograd.grad(funToDiff)
    def fun(x):
        goal = funToDiff(x)
        grad = gradFun(x)
        print('%.0E' % goal, end=' ')
        #print('[%.0E]' % grad, end=' ')
        return goal, grad
    sol = scipy.optimize.minimize(fun=fun, x0=x0, method='L-BFGS-B', jac=True)
    a = sol.x.reshape(shape)
    goal = fun(sol.x)[0]
    goal0 = fun(x0)[0]
    print('\nInitial params: goal = %.0E \n' % goal0, a0) 
    print('Final params: goal = %.0E \n' % goal, a) 
    return a

def test():
    a0 = np.array([1., 1.])
    U0 = np.array(qeye(2).full())
    sx = np.array(sigmax().full())
    sy = np.array(sigmay().full())
    def Hat(a,t):
        return a[0] * sx + a[1] * sy
    T = np.pi
    Ugoal = sx
    def goalFunc(U):
        return 1 - getFid(U, Ugoal)
    minimize(a0, U0, Hat, T, goalFunc)

if __name__ == '__main__':
    test()