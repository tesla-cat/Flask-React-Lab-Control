
import autograd.numpy as np
import autograd
import scipy
from qutip import qeye, sigmax, sigmay
from autograd.misc.optimizers import adam

from .getUnitary import getUnitary
from .getFid import getFid

def minimize(a0, U0, Hat, T, goalFunc, callback):
    shape = a0.shape
    x0 = a0.flatten()
    def funToDiff(x, *args):
        a = x.reshape(shape)
        def Ht(t):
            return Hat(a, t)
        U = getUnitary(U0, Ht, T)
        goal = goalFunc(U)
        return goal
    gradFun = autograd.grad(funToDiff)
    def respond(x):
        a = x.reshape(shape)
        goal = funToDiff(x)
        goal0 = funToDiff(x0)
        print('\nInitial params: goal = %.0E \n' % goal0, a0) 
        print('Final params: goal = %.0E \n' % goal, a)
        callback(a) 
    def fun(x):
        try:
            goal = funToDiff(x)
            grad = gradFun(x)
            print('%.0E' % goal, end=' ')
        except KeyboardInterrupt:
            respond(x)
        return goal, grad
    sol = scipy.optimize.minimize(fun=fun, x0=x0, method='L-BFGS-B', jac=True)
    respond(sol.x)
    def log(params, iter, gradient):
        print(gradient[0], end=' ')
    #x = adam(gradFun, x0, callback=log, step_size=1e-2)
    #respond(x)

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
    def callback(a):
        pass
    minimize(a0, U0, Hat, T, goalFunc, callback)

if __name__ == '__main__':
    test()