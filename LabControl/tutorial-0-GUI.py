import rpyc
from GUI.GUI import GUI 

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

#brick = Instruments.LabBrick(serialNumber = 24352, name = 'brick')
sa124B_IQ = Instruments.SA124B(serialNumber = 19184645, mode = 'IQ', name = 'sa124B_IQ')
#sc5511A = Instruments.SC5511A(serialNumber= 10002657, name = 'sc5511A' )
#sc5503B = Instruments.SC5503B(serialNumber= 10002656, name = 'SC5503B' )

gui = GUI()
gui.add([ 
    #brick, 
    sa124B_IQ, 
    #sc5511A, 
    #sc5503B 
])
gui.run()