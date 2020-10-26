import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import copy
import mclient
import lmfit
from lib.math import fitter
from matplotlib import gridspec

FIT_AMP         = 'AMP'         # Fit simple sine wave
FIT_AMPFUNC     = 'AMPFUNC'     # Try to fit amplitude curve based on pi/2 and pi amp
FIT_PARABOLA    = 'PARABOLA'    # Fit a parabola (to determine min/max pos)

def analysis(xs, ys, fig=None, repeat_pulse=1, fit_type=FIT_AMP, txt=''):
#    ys, fig = meas.get_ys_fig(data, fig)
#    xs = meas.amps

    if fig is None:
        fig = plt.figure()
        gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
        fig.add_subplot(gs[0])
        fig.add_subplot(gs[1])

    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    if fit_type == FIT_AMPFUNC:
        pass
    else:
        f = fitter.Fitter('sine')
        result = f.perform_lmfit(xs, ys, print_report=False, plot=False)
        p = result.params
        ys_fit = f.eval_func()

        pi_amp = repeat_pulse / (2.0 * p['f'].value)

        txt += 'Amp = %0.3f +/- %0.4f\n' % (p['A'].value, p['A'].stderr)
        txt += 'f = %0.4f +/- %0.5f\n' % (p['f'].value, p['A'].stderr)
        txt += 'phase = %0.3f +/- %0.4f\n' % (p['dphi'].value, p['dphi'].stderr)
        txt += 'period = %0.4f\n' % (1.0 / p['f'].value)
        txt += 'pi amp = %0.4f; pi/2 amp = %0.4f' % (pi_amp, pi_amp/2.0)
        fig.axes[0].plot(xs, ys_fit, label=txt)
        fig.axes[1].plot(xs, ys-ys_fit, marker='s')

    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Pulse amplitude')
    fig.axes[0].legend(loc=0)

    fig.canvas.draw()
    return result.params

class Rabi(Measurement1D):

    def __init__(self, qubit_info, amps, update=False,
                 seq=None, r_axis=0, fix_phase=False,
                 fix_period=None, repeat_pulse=1, postseq=None,
                 fit_type=FIT_AMP,
                 **kwargs):

        self.qubit_info = qubit_info
        self.amps = amps
        self.xs = amps
        self.update_ins = update
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.fit_type = fit_type

        super(Rabi, self).__init__(len(amps), infos=(qubit_info,), **kwargs)
        self.data.create_dataset('amps', data=amps)

    def generate(self):
        s = Sequence()

        for i, amp in enumerate(self.amps):
            s.append(self.seq)
            s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(self.get_readout_pulse())

        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):

        data = self.get_ys(data)
        if self.fit_type == FIT_PARABOLA:
            return self.analyze_parabola(data=data, fig=fig, xlabel='Amplitude', ylabel='Signal')

        txt = '%s: %d ns\n' % (self.qubit_info.rotation, self.qubit_info.w)
        self.fit_params = analysis(self.xs, data, fig,
               repeat_pulse=self.repeat_pulse, fit_type=self.fit_type, txt=txt)

        if self.fit_type == FIT_AMPFUNC:
            pi_amp = self.repeat_pulse/(2.0 * self.fit_params['f'].value)
            pi2_amp = pi_amp * 0.5
            if self.update_ins:
                print 'Setting qubit pi-rotation amplitude to %.06f, pi/2 to %.06f' % (pi_amp, pi2_amp)
                mclient.instruments[self.qubit_info.insname].set_pi_amp(pi_amp)
                mclient.instruments[self.qubit_info.insname].set_pi2_amp(pi2_amp)
        else:
            pi_amp = self.repeat_pulse / (2.0 * self.fit_params['f'].value)
            if self.update_ins:
                print 'Setting qubit pi-rotation ampltiude to %.06f' % pi_amp
                mclient.instruments[self.qubit_info.insname].set_pi_amp(pi_amp)
                mclient.instruments[self.qubit_info.insname].set_pi2_amp(pi_amp/2.0)

        return pi_amp

