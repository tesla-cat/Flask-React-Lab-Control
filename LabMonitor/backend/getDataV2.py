
import sys, json, time
from datetime import datetime
import numpy as np

def sendJsonData(data):
    print( json.dumps(data) )
    sys.stdout.flush()

def getData():
    x1 = np.linspace(0, 1, 100)
    y1 = np.random.rand(*x1.shape)
    x2 = np.linspace(-1, 0, 100)
    y2 = x2**2
    def round(x): return x.round(2).tolist()
    return {
        'xs': [
            { 'l': 'x1 (t)', 'x': round(x1) },
            { 'l': 'x2 (t)', 'x': round(x2) },
        ],
        'ys': [
            { 'l': 'y1 (V)', 'y': round(y1), 'x': 0 },
            { 'l': 'y2 (A)', 'y': round(y2), 'x': 1 },
        ],
    }

while 1:
    sendJsonData(getData())
    time.sleep(3)