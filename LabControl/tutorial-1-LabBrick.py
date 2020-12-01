
import rpyc

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

brick = Instruments.LabBrick(serialNumber = 24352)
print('\nbrick.data:\n', brick.data)
brick.setValues({'freq': 7e9, 'pow': -12})
print('\nbrick.getValues():\n', brick.getValues())
brick.stop()

