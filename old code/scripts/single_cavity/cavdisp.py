# -*- coding: utf-8 -*-
"""
Cavity displacement and projection measurement, useful to calibrate
displacements.

by Brian Vlastakis, Reinier Heeres
"""

import numpy as np
from math import factorial
import matplotlib.pyplot as plt
from matplotlib import gridspec
from lib.math import fitter
import copy
import mclient
from measurement import Measurement1D_bgcor
from pulseseq.sequencer import *
from pulseseq.pulselib import *

def analysis(xs, ys, fig, proj_num=0, vary_ofs=False, fit_type='poisson'):
    f = fitter.Fitter(fit_type)
    p = f.get_lmfit_parameters(xs, ys)
    if fit_type=='poisson':
        p['n'].value = proj_num
        p['n'].vary = False
        p['ofs'].value = 0.0
        p['ofs'].vary = vary_ofs
        result = f.perform_lmfit(xs, ys, p=p, plot=False)
        p = result.params
        ys_fit = f.eval_func()

        txt = 'one photon disp amplitude: %0.3f' % p['xscale'].value
    else:
        result = f.perform_lmfit(xs, ys, p=p, plot=False)
        p = result.params
        ys_fit = f.eval_func()

        pi_amp = 1.0 / (2.0 * p['f'].value)
        txt = 'Amp = %0.3f +/- %0.4f\n' % (p['A'].value, p['A'].stderr)
        txt += 'f = %0.4f +/- %0.5f\n' % (p['f'].value, p['A'].stderr)
        txt += 'phase = %0.3f +/- %0.4f\n' % (p['dphi'].value, p['dphi'].stderr)
        txt += 'period = %0.4f\n' % (1.0 / p['f'].value)
        txt += 'pi amp = %0.4f; pi/2 amp = %0.4f' % (pi_amp, pi_amp/2.0)
    fig.axes[1].plot(xs, ys_fit, 'g-', label=txt)
    fig.axes[1].legend()

    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[1].set_ylabel('Intensity [AU]')
    fig.axes[2].set_xlabel('Displacement [alpha]')

    fig.axes[2].plot(xs, ys_fit-ys, 'ks-')
    fig.canvas.draw()
    return p

class CavDisp(Measurement1D_bgcor):

    def __init__(self, qubit_info, cav_info, disps, proj_num,
                 seq=None, delay=0, bgcor=False, update=False, fit_type='poisson',
                 **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.proj_num = proj_num
        self.delay = delay
        self.bgcor = bgcor

        self.update_ins = update
        self.fit_type = fit_type
        self.displacements = disps
        if len(disps) == 1:
            self.displacements = np.array([dmax])
        self.xs = np.abs(self.displacements) # we're plotting amplitude

        npoints = len(self.displacements)
        if self.bgcor:
            npoints *= 2

        super(CavDisp, self).__init__(npoints, infos=(qubit_info, cav_info), bgcor=bgcor, **kwargs)
        self.data.create_dataset('displacements', data=self.displacements, dtype=np.complex)
        self.data.set_attrs(
            delay=delay,
            bgcor=bgcor
        )

    def generate(self):
        '''
        If bg = True generate background measurement, i.e. no qubit pi pulse
        '''

        s = Sequence()

        r = self.qubit_info.rotate
        c = self.cav_info.rotate
        for i, alpha in enumerate(self.displacements):
            for bg in [1, 0]:
                if i_bg == 1 and not self.bgcor:
                    continue

                s.append(self.seq)
                s.append(c(0, np.angle(alpha), amp=np.abs(alpha)))

                s.append(Delay(50))
                s.append(r(np.pi*i_bg, X_AXIS))

                if self.delay:
                    s.append(Delay(self.delay))

                s.append(self.get_readout_pulse())

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):

        if self.fit_type=='poisson':
            self.fit_params = analysis(self.xs, data, fig, proj_num=self.proj_num)
            new_amp = self.fit_params['xscale'].value
            cav = mclient.instruments.get(self.cav_info.insname)
        elif self.fit_type=='sine':
            self.fit_params = analysis(self.xs, data, fig, fit_type=self.fit_type)
            new_amp = 1.0/(2.0 * self.fit_params['f'].value)

        if self.update_ins:
            print 'new one photon displacement amp %.03f' % new_amp
            cav.set_pi_amp(new_amp)
        else:
            print 'one photon displacement amp: %.03f (not setting)' % new_amp

        return new_amp
