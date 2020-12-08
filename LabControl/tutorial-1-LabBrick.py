
import rpyc

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

brick = Instruments.LabBrick(serialNumber = 24352)
brick.setValues({'freq': 7e9, 'pow': -10})
print(brick.getValues())
brick.stop()
