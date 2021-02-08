
import numpy as np 
from datetime import datetime

"""
here are the main pressures and temperatures we want
- MaxiGauge pressure measurement 
  p1 - OVC pressure
  p2 - still pressure
  p5 - tank pressure
- temperatures
  c1 - 50K stage temp
  c2 - 4K stage temp
  c3 - still temp
  c4 - MXC temp
"""

def parse(filename, getVarFunc, limit=100):
  with open(filename) as f:
    content = f.readlines()
  timeArr = []
  varArr = []
  for line in content[-limit:]:
    line = line.strip()
    blocks = line.split(',')
    #date = blocks[0]
    t = blocks[1]
    timeArr.append(t)
    varArr.append( getVarFunc( blocks ) )
  timeArr = np.array(timeArr).tolist()
  varArr = np.array(varArr).astype(np.float)
  return timeArr, varArr

def getVarPressure(blocks):
  return np.array( blocks[2:-1] ).reshape( [-1, 6] )[:, 3]
def getVarTemperature(blocks):
  return float(blocks[2])

def getFilenames(logPath, tempCHs = [1, 2, 5, 6]):
  date = datetime.today().strftime('%y-%m-%d')
  presFile = r'%s\%s\maxigauge %s.log' % (logPath, date, date)
  tempFiles = [r'%s\log-data\192.168.109.188\%s\CH%d T %s.log' \
    % (logPath, date, i, date) for i in  tempCHs]
  return presFile, tempFiles