
import numpy as np 

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

def parse(filename, getVarFunc):
  with open(filename) as f:
    content = f.readlines()
  timeArr = []
  varArr = []
  for line in content:
    line = line.strip()
    blocks = line.split(',')
    #date = blocks[0]
    t = blocks[1]
    timeArr.append(t)
    varArr.append( getVarFunc( blocks ) )
  timeArr = np.array(timeArr)
  varArr = np.array(varArr).astype(np.float)
  return timeArr, varArr

def getVarPressure(blocks):
  return np.array( blocks[2:-1] ).reshape( [-1, 6] )[:, 3]
def getVarTemperature(blocks):
  return float(blocks[2])

def getFilenames(logPath):
  date = '21-01-30'
  presFile = r'%s\%s\maxigauge %s.log' % (logPath, date, date)
  tempFiles = [r'%s\log-data\192.168.109.188\%s\CH%d T %s.log' \
    % (logPath, date, i, date) for i in [1, 2, 5] ]
  return presFile, tempFiles

logPath = r'D:\GitHub\Flask-React-Lab-Control\LabControl\special-1-fridge sensors\log'
presFile, tempFiles = getFilenames(logPath)
print(presFile, tempFiles)

filename1 = presFile
timeArr1, varArr1 = parse(filename1, getVarPressure)
for i in range(5):
  print(timeArr1[i], varArr1[i])

filename2 = tempFiles[0]
timeArr2, varArr2 = parse(filename2, getVarTemperature)
for i in range(5):
  print(timeArr2[i], varArr2[i])