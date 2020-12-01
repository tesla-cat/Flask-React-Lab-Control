
import rpyc

conn = rpyc.classic.connect("localhost")
Instruments = conn.modules["Instruments"]

brick = Instruments.LabBrick(serialNumber = 24352)
print('\nbrick.data:\n', brick.data)
brick.setValue('freq', 6e9)
brick.setValue('pow', -11)
print('\nbrick.getValues():\n', brick.getValues())
brick.stop()