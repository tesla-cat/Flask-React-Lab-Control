
import autograd.numpy as np

def getFid(A, B):
    def prod(C,D): return np.abs(np.sum( np.conjugate(C) * D ))
    return prod(A, B) / prod(A, A)
