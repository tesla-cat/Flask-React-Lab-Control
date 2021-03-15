
import autograd.numpy as np

C1 = 0
C2 = 1 / 5
A21 = 1 / 5
C3 = 3 / 10
A31 = 3 / 40
A32 = 9 / 40
C4 = 4 / 5
A41 = 44 / 45
A42 = -56 / 15
A43 = 32 / 9
C5 = 8 / 9
A51 = 19372 / 6561
A52 = -25360 / 2187
A53 = 64448 / 6561
A54 = -212 / 729
C6 = C7 = 1
A61 = 9017 / 3168
A62 = -355 / 33
A63 = 46732 / 5247
A64 = 49 / 176
A65 = -5103 / 18656
A71 = B1 = 35 / 384
A72 = B2 = 0
A73 = B3 = 500 / 1113
A74 = B4 = 125 / 192
A75 = B5 = -2187 / 6784
A76 = B6 = 11 / 84
B7 = 0
B1H = 5179 / 57600
B2H = 0
B3H = 7571 / 16695
B4H = 393 / 640
B5H = -92097 / 339200
B6H = 187 / 2100
B7H = 1 / 40

# const
P = 5
PH = 4
Q = np.minimum(P, PH)
ERROR_EXP = -1 / (Q + 1)
MAX_UPDATE_FACTOR = 10
MIN_UPDATE_FACTOR = 0.2
SAFETY_FACTOR = 0.9
ABS_TOL = 1e-12
REL_TOL = 0.

def rmsNorm(x):
    squareNorm = np.sum( x * np.conjugate(x) )
    size = np.prod(x.shape)
    return np.sqrt(squareNorm/size)

def odeInt(f, x0, y0, xT):
    # 1993 Solving Ordinary Differential Equations I, page 169 
    # initial step size
    f0 = f(x0, y0)
    d0 = rmsNorm(y0)
    d1 = rmsNorm(f0)
    if d0 < 1e-5 or d1 < 1e-5:
        h0 = 1e-6
    else:
        h0 = 1e-2 * d0 / d1
    y1 = y0 + f0 * h0
    f1 = f(x0+h0, y1)
    d2 = rmsNorm(f1 - f0) / h0
    maxD = np.maximum(d1, d2)
    if maxD <= 1e-15:
        h1 = np.maximum(1e-6, h0*1e-3)
    else:
        h1 = np.power( 1e-2/maxD, 1/(P+1) )
    step = np.minimum(1e2*h0, h1)
    # integrate
    x = x0
    y = y0
    k1 = f0
    while x < xT:
        rejected = False
        accepted = False
        while not accepted:
            ks, y1, y1h = odeIntStep(step, f, x, y, k1)
            xNew = x + step
            scale = ABS_TOL + np.maximum(np.abs(y1), np.abs(y1h)) * REL_TOL
            errNorm = rmsNorm((y1-y1h) / scale)
            if errNorm < 1:
                accepted = True
                if errNorm == 0:
                    updateFactor = MAX_UPDATE_FACTOR
                else:
                    updateFactor = np.minimum(MAX_UPDATE_FACTOR, SAFETY_FACTOR * np.power(errNorm, ERROR_EXP))
                if rejected:
                    updateFactor = np.minimum(1, updateFactor)
                step *= updateFactor
            else:
                rejected = True
                updateFactor = np.maximum(MIN_UPDATE_FACTOR, SAFETY_FACTOR * np.power(errNorm, ERROR_EXP))
                step *= updateFactor
        # interpolate
        # update
        x = xNew
        y = y1
        k1 = ks[6]
    step = xT - x
    ks, y1, y1h = odeIntStep(step, f, x, y, k1)
    return y1

def odeIntStep(h, f, x0, y0, k1):
    k2 = f(x0 + C2 * h, y0 + h *  A21 * k1)
    k3 = f(x0 + C3 * h, y0 + h * (A31 * k1 + A32 * k2))
    k4 = f(x0 + C4 * h, y0 + h * (A41 * k1 + A42 * k2 + A43 * k3))
    k5 = f(x0 + C5 * h, y0 + h * (A51 * k1 + A52 * k2 + A53 * k3 + A54 * k4))
    k6 = f(x0 + C6 * h, y0 + h * (A61 * k1 + A62 * k2 + A63 * k3 + A64 * k4 + A65 * k5))
    y1 = y0 + h * (B1 * k1 + B3 * k3 + B4 * k4 + B5 * k5 + B6 * k6)
    k7 = f(x0 + h, y1)
    y1h = y0 + h * (B1H * k1 + B3H * k3 + B4H * k4 + B5H * k5 + B6H * k6 + B7H * k7)  
    ks = (k1, k2, k3, k4, k5, k6, k7)
    return ks, y1, y1h
