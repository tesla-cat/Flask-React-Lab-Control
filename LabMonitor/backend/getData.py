
import sys, json, time
import numpy as np 
from datetime import datetime

from getSensor import Sensor
from getLog import parse, getFilenames, getVarPressure, getVarTemperature

#================================================

logPath = r'C:\Users\qcrew\Desktop\installed fridge software\log'
presFile, tempFiles = getFilenames(logPath, date='21-02-01')
sen = Sensor()

def getData():
  timeS, sensArr = sen.read()
  timeP, presArr = parse(presFile, getVarPressure)
  timeT1, tempArr1 = parse(tempFiles[0], getVarTemperature)
  timeT2, tempArr2 = parse(tempFiles[1], getVarTemperature)
  timeT3, tempArr3 = parse(tempFiles[2], getVarTemperature)
  timeT4, tempArr4 = parse(tempFiles[3], getVarTemperature)
  t = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
  return {
    'xs': [
      { 'l': 'time', 'x': timeP },
      
      { 'l': 'time', 'x': timeT1 },
      { 'l': 'time', 'x': timeT2 },
      { 'l': 'time', 'x': timeT3 },
      { 'l': 'time', 'x': timeT4 },

      { 'l': 'time', 'x': timeS },
    ],
    'ys': [
      { 'l': 'P1 [mbar] OVC', 'y': presArr[:, 0].tolist(), 'x': 0 },
      { 'l': 'P2 [mbar] still', 'y': presArr[:, 1].tolist(), 'x': 0 },
      { 'l': 'P5 [mbar] tank', 'y': presArr[:, 4].tolist(), 'x': 0 },
      
      { 'l': 'T1 [K] 50K', 'y': tempArr1.tolist(), 'x': 1 },
      { 'l': 'T2 [K] 4K', 'y': tempArr2.tolist(), 'x': 2 },
      { 'l': 'T3 [K] still', 'y': tempArr3.tolist(), 'x': 3 },
      { 'l': 'T4 [K] MXC', 'y': tempArr4.tolist(), 'x': 4 },

      # b'flow:3.91,water_pres:388.28,temp:18.62,air_pres:0.35,'
      { 'l': 'S1 [L/min] flow', 'y': sensArr[:, 0].tolist(), 'x': 5 },
      { 'l': 'S2 [kPa] water_pres', 'y': sensArr[:, 1].tolist(), 'x': 5 },
      { 'l': 'S3 [C] temp', 'y': sensArr[:, 2].tolist(), 'x': 5 },
      { 'l': 'S4 [kPa] air_pres', 'y': sensArr[:, 3].tolist(), 'x': 5 },
    ],
    'msg': 'updated: %s' % (t),
  }

def sendJsonData(data):
  print( json.dumps(data) )
  sys.stdout.flush()

while 1:
  sendJsonData(getData())
  time.sleep(30)
