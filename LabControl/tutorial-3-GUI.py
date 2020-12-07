import rpyc
from GUI.GUI import GUI 

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

brick = Instruments.LabBrick(serialNumber = 24352, name='brick')
sa124B_IQ = Instruments.SA124B(serialNumber = 19184645, mode = 'IQ', name='sa124B_IQ')

gui = GUI()
gui.add([ brick, sa124B_IQ ])
gui.run()