
import rpyc

# ========== connect to the Instruments Server ==========
Instruments = rpyc.classic.connect("localhost").modules["Instruments"]

dev = Instruments.SC5503B(serialNumber= 10002656 )
print(dev.start())
print(dev.setValues({'freq': 3e9, 'pow': 3, 'output': 0}))
print(dev.getValues())
print(dev.stop())
