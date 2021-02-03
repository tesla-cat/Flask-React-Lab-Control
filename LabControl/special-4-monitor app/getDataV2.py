
import sys, json
import time
from datetime import datetime

def sendJsonData(data):
    print( json.dumps(data) )
    sys.stdout.flush()

while 1:
    now = datetime.now().strftime("%H:%M:%S")
    data = { 'time': now }
    sendJsonData(data)
    time.sleep(3)