import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import lmfit
from lib.math import fitter

ECHO_NONE       = 'NONE'
ECHO_HAHN       = 'HANN'
ECHO_CPMG       = 'CMPG'
ECHO_XY4        = 'XY4'
ECHO_XY8        = 'XY8'
ECHO_XY16       = 'XY16'

def get_echo_pulse(echotype, qubit_info):
    r = qubit_info.rotate

    if echotype == ECHO_NONE:
        return None

    elif echotype == ECHO_HAHN:
        return r(np.pi, X_AXIS)

    elif echotype == ECHO_CPMG:
        return r(np.pi, Y_AXIS)

    elif echotype == ECHO_XY4:
        return Sequence([
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),
        ])

    elif echotype == ECHO_XY8:
        return Sequence([
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),

            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),
        ])

    elif echo == ECHO_XY16:
        return Sequence([
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),

            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),
            r(np.pi, Y_AXIS),
            r(np.pi, X_AXIS),

            r(-np.pi, X_AXIS),
            r(-np.pi, Y_AXIS),
            r(-np.pi, X_AXIS),
            r(-np.pi, Y_AXIS),

            r(-np.pi, Y_AXIS),
            r(-np.pi, X_AXIS),
            r(-np.pi, Y_AXIS),
            r(-np.pi, X_AXIS),
        ])

def analysis(meas, data=None, fig=None, detune=None):
    xs = np.array(meas.delays, dtype=np.float) / 1e3 # us
    ys, meas_fig = meas.get_ys_fig(data, fig)
    if data is not None:
        ys = data
    if fig is None:
        fig = meas_fig
    if detune is None:
        detune = meas.detune/1e3 # in kHz and always positive?

    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    if not meas.double_freq:
        f = fitter.Fitter('exp_decay_sine')
        p = f.get_lmfit_parameters(xs, ys)
        if meas.fix_freq:
            p['f'].value = meas.detune/1e6
            p['f'].vary = not meas.fix_freq
        result = f.perform_lmfit(xs, ys, p=p, print_report=True, plot=False)
        ys_fit = f.eval_func()

        f = result.params['f'].value * 1e3
        tau = result.params['tau'].value

        txt = 'tau = %0.3f us\n' % (tau)
        txt += 'f = %0.4f kHz\n' % (f)
        txt += 'software df = %0.3f kHz\n' % (detune)
        txt += 'frequency detuning = %0.4f kHz' % (detune-f)

    else:
        f = fitter.Fitter('exp_decay_double_sine')
        result = f.perform_lmfit(xs, ys, print_report=True, plot=False)
        ys_fit = f.eval_func()

        f = result.params['f'].value
        f1 = result.params['f1'].value
        tau = result.params['tau'].value

        txt = 'tau = %0.3f us\n' % (tau)
        txt += 'f = %0.4f kHz\n' % (f)
        txt += 'f1 = %0.4f kHz\n' % (f1)
        txt += 'software df = %0.3f kHz\n' % (detune)


    fig.axes[0].plot(xs, ys_fit, label=txt)
    fig.axes[1].plot(xs, (ys_fit-ys), marker='s')

    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[1].set_ylabel('Residuals')
    fig.axes[1].set_xlabel('Time [us]')

    fig.canvas.draw()

    return result.params

class T2Measurement(Measurement1D):

    def __init__(self, qubit_info, delays, detune=0, echotype=ECHO_NONE,
                 necho=1, double_freq=False, fix_freq=None,
                 seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.delays = np.array(np.round(delays), dtype=int)
        self.xs = delays / 1e3        # For plotting purposes
        self.detune = detune
        self.echotype = echotype
        self.necho = necho
        self.double_freq=double_freq
        self.fix_freq = fix_freq
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        super(T2Measurement, self).__init__(len(delays), infos=qubit_info, **kwargs)
        self.data.create_dataset('delays', data=delays)
        self.data.set_attrs(
            detune=detune,
            echotype=echotype,
            necho=necho,
            rep_rate=self.instruments['funcgen'].get_frequency()
        )

    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate

        e = get_echo_pulse(self.echotype, self.qubit_info)
        if e:
            elen = e.get_length()
        else:
            elen = 0

        for i, dt in enumerate(self.delays):
            s.append(self.seq)

            s.append(r(np.pi/2, X_AXIS))

            # We want echos: <tau> (<echo> <2tau>)^n <tau>
            if elen != 0:
                tau = int(np.round(dt / (2 * self.necho)))
                s.append(Delay(tau))
                for i in range(self.necho - 1):
                    s.append(e)
                    s.append(Delay(2*tau))
                s.append(e)
                s.append(Delay(tau))

            # Plain T2
            elif dt > 0:
                s.append(Delay(dt))

            # Measurement pulse
            angle = dt * 1e-9 * self.detune * 2 * np.pi
            s.append(r(np.pi/2, angle))

            if self.postseq is not None:
                s.append(self.postseq)

            s.append(self.get_readout_pulse())

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params