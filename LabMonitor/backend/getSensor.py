
import serial, time
import numpy as np
from datetime import datetime

class Sensor:
  def __init__(self):
    self.ser = serial.Serial('COM6', 115200)
    self.times = [0]
    self.vals = [ [0]*5 ]
    self.limit = 100

  def read(self):
    buf = self.ser.read(self.ser.inWaiting())
    lines = buf.split(b'\r\n')
    if len(lines) > 1:
      last = lines[-2]
      # b'freq: 209, flow (L/min): 19, voltage:1.44, pressure (kPa): 384.12, temperature (\xc2\xbaC): 18.56\r'
      val = [block.split(b':')[1] for block in last.split(b',')]
      val = np.array(val).astype(np.float32)
      t = datetime.now().strftime('%H:%M:%S')
      self.vals = self.vals[-self.limit+1 : ] + [ val ]
      self.times = self.times[-self.limit+1 : ] + [ t ]
    return self.times, np.round( np.array(self.vals), 2 )
