
import serial, time
import numpy as np
from datetime import datetime

class Sensor:
  def __init__(self):
    try:
      self.ser = serial.Serial('COM6', 115200)
    except:
      self.ser = None
    self.times = []
    self.vals = [ [0]*4 ]
    self.limit = 100

  def read(self):
    if self.ser:
      buf = self.ser.read(self.ser.inWaiting())
      lines = buf.split(b'\n')
      if len(lines) > 1:
        last = lines[-2]
        # b'flow:3.91,water_pres:388.28,temp:18.62,air_pres:0.35,'
        val = [ float(block.split(b':')[1]) for block in last.split(b',')[:-1] ]
        t = datetime.now().strftime('%H:%M:%S')
        self.vals = self.vals[-self.limit+1 : ] + [ val ]
        self.times = self.times[-self.limit+1 : ] + [ t ]
    return self.times, np.array(self.vals)

if __name__ == '__main__':
  sen = Sensor()
  while(1):
    timeS, sensArr = sen.read()
    print(timeS, sensArr)
    time.sleep(2)