
import sys, json, time
from datetime import datetime
import numpy as np

def sendJsonData(data):
    print( json.dumps(data) )
    sys.stdout.flush()

def getData():
    x1 = np.linspace(0, 1, 100)
    y1 = np.random.rand(*x1.shape)
    y2 = np.sin( x1 + time.time() )
    def round(x): return x.round(2).tolist()
    return {
        'xs': [
            { 'l': 'time (s)', 'x': round(x1) },
        ],
        'ys': [
            { 'l': 'random (V)', 'y': round(y1), 'x': 0 },
            { 'l': 'sin (A)', 'y': round(y2), 'x': 0 },
        ],
    }

while 1:
    sendJsonData(getData())
    time.sleep(3)