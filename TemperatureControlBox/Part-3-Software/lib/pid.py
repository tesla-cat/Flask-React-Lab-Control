import numpy as np
import matplotlib.pyplot as plt
import time

class PID:
    def __init__(self, target, pid, outRng=[0,100]):
        self.targ = target
        self.pid = pid
        self.outRng = outRng
    def reset(self, iniVal):
        self.vals = [iniVal]
        self.outs = [0]
        self.tim0 = time.time()
        self.tims = [0]
        self.int = 0
    def step(self, val):
        tim = time.time() - self.tim0
        dt = tim - self.tims[-1]
        p = val - self.targ
        self.int += p * dt
        d = (val - self.vals[-1])/dt
        kp,ki,kd = self.pid
        out = kp*p + ki*self.int + kd*d
        out = min(out, self.outRng[1])
        out = max(out, self.outRng[0])
        self.vals.append(val)
        self.tims.append(tim)
        self.outs.append(out)
        return out
    def render(self):
        plt.title('pid: {}'.format(self.pid))
        plt.xlabel('time (s)')
        plt.plot(self.tims, np.array(self.vals)-self.targ, label="measured - target")
        plt.plot(self.tims, np.array(self.outs)/self.pid[0], label="control output / kp")
        plt.legend()
        plt.show()
    def test(self):
        self.reset(0)
        for i in range(100):
            time.sleep(0.01)
            out = self.step( np.sin(self.tims[-1] * 20) )
        self.render()

if __name__ == "__main__":
    pid = PID(0, [1,1,1])
    pid.test()

        
