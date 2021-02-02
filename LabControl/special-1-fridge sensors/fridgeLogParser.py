
import numpy as np

"""
Bluefors user manual.pdf page 48

The ValveControl software offers the possibility to log all measured data for later reference. 
Three different data files can be logged:

- Pressure (csv). 
    Logging options can be set in the ‘Settings’ tab which is located inside the ‘Maxigauge’ tab. 
    To enable logging, define a log path and make the ‘Enable logging’ tick box active. 
    The log saving frequency can be set in the ‘Logging interval’ box. 
    Higher resolution (short-term) data is stored in the computer memory and displayed in graphs under the ‘Channel’ tabs. 
    The reading frequency and number of points stored in these graphs can be set from the ‘Reading interval’ 
    and ‘Number of samples to show in graph’ boxes. 
    All above mentioned setting can be saved for next time the ValveControl software is run by clicking ‘Save settings’.
- Flow (csv). 
    Logging options can be set in the ‘Flowmeter’ tab. 
    To enable logging, define a log path and make the ‘Enable logging’ tick box active. 
    The log saving frequency can be set in the ‘Logging interval’ box. 
    Higher resolution (short-term) data is stored in the computer memory and displayed in the graph located within the same tab. 
    The reading frequency and number of points stored in this graph can be set from the ‘Reading interval’ 
    and ‘Number of samples to show in graph’ boxes. 
    All above mentioned setting can be saved for next time the ValveControl software is run by clicking ‘Save settings’.
- System status. 
    This will log the status of all valves, pumps etc. on the front panel. 
    Every time a change occurs the new state is saved to the log file together with a time stamp. 
    To enable logging, navigate to the ‘Setup’ tab, define a log path and make the ‘Enable logging’ tick box active. 
    The settings can be saved for next time the ValveControl software is run by clicking ‘Save settings’.
Note: 
    The ValveControl software automatically generates a directory structure month-day-year in the log path directory 
    into which the log files are saved. 
    For easy viewing and retrieving of the data afterwards, we recommend using the same log path for all files.
"""

def parseChannels():
    filename = r'C:\Users\e0134117\Desktop\fridge\log\21-01-26\Channels 21-01-26.log'
    with open(filename) as f:
        content = f.readlines()
    for line in content[0:1]:
        line = line.strip()
        blocks = line.split(',')
        date = blocks[0]
        time = blocks[1]
        unknown1 = blocks[2]
        variables = np.array( blocks[3:] ).reshape( [-1, 2] ).tolist()
        print('date', date)
        print('time', time)
        print('unknown1', unknown1)
        print('variables')
        for v in variables:
            print(v)

def parseFlowmeter():
    filename = r'C:\Users\e0134117\Desktop\fridge\log\21-01-26\Flowmeter 21-01-26.log'
    with open(filename) as f:
        content = f.readlines()
    for line in content[0:1]:
        line = line.strip()
        blocks = line.split(',')
        date = blocks[0]
        time = blocks[1]
        unknown1 = blocks[2]
        print('date', date)
        print('time', time)
        print('unknown1', unknown1)

def parseMaxigauge():
    filename = r'C:\Users\e0134117\Desktop\fridge\log\21-01-26\maxigauge 21-01-26.log'
    with open(filename) as f:
        content = f.readlines()
    for line in content[0:1]:
        line = line.strip()
        blocks = line.split(',')
        date = blocks[0]
        time = blocks[1]
        variables = np.array( blocks[2:-1] ).reshape( [-1, 6] ).tolist()
        print('date', date)
        print('time', time)
        print('variables')
        for v in variables:
            print(v)

def parseStatus():
    filename = r'C:\Users\e0134117\Desktop\fridge\log\21-01-26\Status_21-01-26.log'
    with open(filename) as f:
        content = f.readlines()
    for line in content[0:1]:
        line = line.strip()
        blocks = line.split(',')
        date = blocks[0]
        time = blocks[1]
        variables = np.array( blocks[2:] ).reshape( [-1, 2] ).tolist()
        print('date', date)
        print('time', time)
        print('variables')
        for v in variables:
            print(v)
        
if __name__ == '__main__':
    #parseChannels()
    #parseFlowmeter()
    #parseMaxigauge()
    parseStatus()

