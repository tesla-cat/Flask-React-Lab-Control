
import rpyc

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

dev = Instruments.SC5511A(serialNumber= 10002657 )
print(dev.start())
print(dev.setValues({'freq': 11e9, 'pow': 6, 'output': 0}))
print(dev.getValues())
print(dev.stop())