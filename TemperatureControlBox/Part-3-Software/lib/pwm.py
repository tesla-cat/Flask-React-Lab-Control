
import RPi.GPIO as IO

IO.setmode(IO.BCM)
IO.setwarnings(False)

class PWM:
    def __init__(self,pin=18,frequency=50):
        IO.setup(pin,IO.OUT)
        self.pwm = IO.PWM(pin,frequency)
        self.pwm.start(0)
    def set(self,duty):
        self.pwm.ChangeDutyCycle(min(duty, 100))