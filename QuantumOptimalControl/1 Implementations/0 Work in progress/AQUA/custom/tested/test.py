from odeIntAutograd import odeInt
from qutip import sigmax, qeye
import autograd.numpy as np

I = np.array(qeye(2).full())
sx = np.array(sigmax().full())

def f(t, y):
    return -1j * np.dot( sx, y )
x0 = 0
y0 = I
xT = np.pi
y = odeInt(f, x0, y0, xT)
print(y)