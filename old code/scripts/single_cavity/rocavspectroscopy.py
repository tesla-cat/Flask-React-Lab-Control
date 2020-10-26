from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time

SPEC   = 0
POWER  = 1

def analysis(powers, freqs, ampdata, phasedata=None, plot_type=POWER, ax=None):
    if ax is None:
        ax = plt.figure().add_subplot(111)
    ax2 = ax.twinx()

    if plot_type == SPEC:
        for ipower, power in enumerate(powers):
            ax.plot(freqs/1e6, ampdata[ipower,:], label='Power %.02f dB'%power)
            ax2.plot(freqs/1e6, ampdata[ipower,:], label='Power %.02f dB'%power)

        fs = freqs
        amps = ampdata[0,:]
        f = fit.Lorentzian(fs, amps)
        h0 = np.max(amps)
        w0 = 2e6
        pos = fs[np.argmax(amps)]
        p0 = [np.min(amps), w0*h0, pos, w0]
        p = f.fit(p0)
        txt = 'Center = %.03f MHz' % (p[2]/1e6,)
        print 'Fit gave: %s' % (txt,)
#        plt.plot(fs/1e6, f.func(p, fs), label=txt)

        plt.legend()
        plt.ylabel('Intensity [AU]')
        plt.xlabel('Frequency [MHz]')

    if plot_type == POWER:
#        ax1 = f.add_subplot(2,1,1)
#        ax2 = f.add_subplot(2,1,2)
        for ifreq, freq in enumerate(freqs):
            ax.plot(powers, ampdata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
            ax2.plot(powers, phasedata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
        ax.legend()
        ax2.legend()
        ax.set_ylabel('Intensity [AU]')
        ax2.set_ylabel('Angle [deg]')
        ax.set_xlabel('Power [dB]')
        ax2.set_xlabel('Power [dB]')

class ROCavSpectroscopy(Measurement1D):

    def __init__(self, qubit_info, powers, freqs, plot_type=None, qubit_pulse=True, **kwargs):
        self.qubit_info = qubit_info
        self.freqs = freqs
        self.powers = powers
        self.qubit_pulse = qubit_pulse

        if plot_type is None:
            if len(powers) > len(freqs):
                plot_type = POWER
            else:
                plot_type = SPEC
        self.plot_type = plot_type

        super(ROCavSpectroscopy, self).__init__(1, infos=qubit_info, **kwargs)
        self.data.create_dataset('powers', data=powers)
        self.data.create_dataset('freqs', data=freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=(len(powers),len(freqs)))
        self.phasedata = self.data.create_dataset('phases', shape=(len(powers),len(freqs)))

    def generate(self):
        s = Sequence()

        if type(self.qubit_pulse) in (types.IntType, types.FloatType):
            s.append(Trigger(250))
            s.append(self.qubit_info.rotate(self.qubit_pulse, 0))
        elif self.qubit_pulse:
            s.append(Trigger(250))
            s.append(self.qubit_info.rotate(np.pi/2, 0))
        else:
            s.append(Trigger(250))
        s.append(self.get_readout_pulse())

        s = self.get_sequencer(s)
        seqs = s.render()
        self.seqs = seqs
        return seqs

    def measure(self):
        # Generate and load sequences
        alz = self.instruments['alazar']
        alz.set_interrupt(False)

        seqs = self.generate()
        self.load(seqs)
        self.start_awgs()

        for ipower, power in enumerate(self.powers):
            self.readout_info.rfsource1.set_power(power)
            print 'Power = %s' % (power, )
            time.sleep(2)

            amps = []
            phases = []

            for ifreq, freq in enumerate(self.freqs):
                self.readout_info.rfsource1.set_frequency(freq)
                self.readout_info.rfsource2.set_frequency(freq+50e6)
                time.sleep(0.05)

                alz.setup_avg_shot(alz.get_naverages())
                ret = alz.take_avg_shot(async=True)
                try:
                    while not ret.is_valid():
                        objsh.helper.backend.main_loop(100)
                except Exception, e:
                    alz.set_interrupt(True)
                    print 'Error: %s' % (str(e), )
                    return

                IQ = np.average(ret.get())
                amps.append(np.abs(IQ))
                phases.append(np.angle(IQ, deg=True))
                print 'F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True))

            self.ampdata[ipower,:] = amps
            self.phasedata[ipower,:] = phases

        self.analyze()

    def analyze(self, data=None, ax=None):
        pax = ax if (ax is not None) else plt.figure().add_subplot(111)
        ampdata = data if (data is not None) else self.ampdata
        analysis(self.powers, self.freqs, ampdata, self.phasedata, self.plot_type, ax=pax)
