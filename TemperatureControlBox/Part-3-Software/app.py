
from lib.temperature import Temperature
from lib.pid import PID
from lib.pwm import PWM
import time

tem = Temperature()
pid = PID(target=25.5, pid=[100,10,1])
pid.reset(tem.get())
pwm = PWM()

while True:
    try:
        curTem = tem.get()
        duty = pid.step(curTem) 
        pwm.set(duty)
        print("tem: %.2f \t duty: %.2f" % (curTem,duty))
    except KeyboardInterrupt:
        pid.render()