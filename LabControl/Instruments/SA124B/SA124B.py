
from .sadevice.sa_api import *
import numpy as np

SA124Bdoc = """
    saConfigAcquisition() – Configuring the detector and linear/log scaling
    saConfigCenterSpan() – Configuring the sweep frequency range
    saConfigLevel() – Configuring reference level for automatic gain and attenuation
    saConfigGainAtten() – Configuring internal amplifiers and attenuators
    saConfigSweepCoupling() – Configuring RBW and VBW
    saConfigProcUnits() – Configure VBW processing
    saInitiate() using the SA_SWEEPING flag
    saQuerySweepInfo(). This function returns the length of the sweep, the frequency of the first bin, and the bin size. 
    saGetSweep() functions. The length of the sweep is determined by a combination of resolution bandwidth, video bandwidth, and span.
    𝐹𝑟𝑒𝑞𝑢𝑒𝑛𝑐𝑦 𝑜𝑓 𝑛′𝑡ℎ 𝑠𝑎𝑚𝑝𝑙𝑒 𝑝𝑜𝑖𝑛𝑡 𝑖𝑛 𝑟𝑒𝑡𝑢𝑟𝑛𝑒𝑑 𝑠𝑤𝑒𝑒𝑝 = 𝑠𝑡𝑎𝑟𝑡𝐹𝑟𝑒𝑞 + 𝑛 ∗ 𝑏𝑖𝑛𝑆𝑖𝑧

## saConfigCenterSpan

- "device" Device handle.
- "center" Center frequency in hertz.
- "span" Span in hertz.

This function configures the operating frequency band of the device. Start and stop frequencies can be
determined from the center and span.
- start = center – (span / 2)
- stop = center + (span / 2)
The values provided are used by the device during initialization and a more precise start frequency is
returned after initiation. Refer to saQueryTraceInfo() for more information.

Each device has a specified operational frequency range between some minimum and maximum
frequency. The limits are defined in sa_api.h. The center and span provided cannot specify a sweep
outside of this range.

Certain modes of operation have specific frequency range limits. Those mode dependent limits are
tested against during saInitiate() and not here.

## saConfigLevel

- "device" Device handle.
- "ref" Reference level in dBm.

This function is best utilized when the device attenuation and gain is set to automatic(default). When
both attenuation and gain are set to AUTO, the API uses the reference level to best choose the gain and
attenuation for maximum dynamic range. The API chooses attenuation and gain values best for
analyzing signal at or below the reference level. For this reason, to achieve the best results, ensure gain
and attenuation are set to AUTO and your reference level is set at or slightly about your expected input
power for best sensitivity. Reference level is specified in dBm units.

## saConfigSweepCoupling:

- "device" Handle to the device being configured.
- "rbw" Resolution bandwidth in Hz. RBW can be arbitrary.
- "vbw" Video bandwidth in Hz. VBW must be less than or equal to RBW. VBW can be arbitrary. For best performance use RBW as the VBW.
- "reject" Indicates whether to enable image rejection. 

The resolution bandwidth, or RBW, represents the bandwidth of spectral energy represented in each
frequency bin. For example, with an RBW of 10 kHz, the amplitude value for each bin would represent
the total energy from 5 kHz below to 5 kHz above the bin’s center.

The video bandwidth, or VBW, is applied after the signal has been converted to frequency domain as
power, voltage, or log units. It is implemented as a simple rectangular window, averaging the amplitude
readings for each frequency bin over several overlapping FFTs. A signal whose amplitude is modulated at
a much higher frequency than the VBW will be shown as an average, whereas amplitude modulation at
a lower frequency will be shown as a minimum and maximum value.

Available RBWs are [0.1Hz – 100kHz] and 250kHz. For the SA124 devices, a 6MHz RBW is available as
well. Not all RBWs will be available depending on span, for example the API may restrict RBW when a
sweep size exceeds a certain amount. Also there are many hardware limitations that restrict certain
RBWs, for a full list of these restrictions, see the Appendix: Setting RBW and VBW.

    Setting RBW and VBW
    The SA44 and SA124 models have many device restrictions which prevent the user from selecting all
    possible combinations of RBW and VBW for any given sweep. Many restrictions are not known until
    saInitiate() is called and all parameters of the sweep are considered. The API clamps RBW/VBW
    when saInitiate() is called if they break the restrictions which are listed below. Concern yourself with
    these restrictions only when it is imperative the API use exactly the RBW and VBW you requested.
    
    SA44A/B, SA124A/B limitations:
        - Available RBWs in the standard sweep mode
            o 0.1Hz to 100kHz, and 250kHz.
        - Available RBWs in real-time
            o 100Hz to 10kHz
        - For the SA44A, RBW/VBW must be greater than or equal to 6.5kHz when
            o span is greater than 200kHz
        - For the SA44B, SA124A, SA124B, RBW/VBW must be greater than or equal to 6.5kHz when
            o span is greater than or equal to 100MHz
            o span is greater than 200kHz AND start frequency < 16MHz
        - For SA124A/B 6MHz RBW available when
            o Start frequency >= 200MHz AND Span >= 200MHz

The parameter reject determines whether software image reject will be performed. The SA-series
spectrum analyzers do not have hardware-based image rejection, instead relying on a software
algorithm to reject image responses. See the USB-SA44B or USB-SA124B manuals for additional details.
Generally, set reject to true for continuous signals, and false to catch short duration signals at a known
frequency. To capture short duration signals with an unknown frequency, consider the Signal Hound
BB60C.

## saConfigAcquisition

- "device" Device handle.
- "detector" Specifies the video detector. The two possible values for detector are SA_MIN_MAX and SA_AVERAGE.
- "scale" Specifies the scale in which sweep results are returned int. The four possible values for scale are SA_LOG_SCALE, SA_LIN_SCALE, SA_LOG_FULL_SCALE, and SA_LIN_FULL_SCALE.

detector specifies how to produce the results of the signal processing for the final sweep. Depending on
settings, potentially many overlapping FFTs will be performed on the input time domain data to retrieve
a more consistent and accurate final result. When the results overlap detector chooses whether to
average the results together, or maintain the minimum and maximum values. If averaging is chosen, the
min and max sweep arrays will contain the same averaged data.

The scale parameter will change the units of returned sweeps. If SA_LOG_SCALE is provided sweeps will
be returned in amplitude unit dBm. If SA_LIN_SCALE is return, the returned units will be in millivolts. If
the full scale units are specified, no corrections are applied to the data and amplitudes are taken directly
from the full scale input.
"""

class SA124B:
    SA124Bdoc
    def __init__(self, serialNumber, mode, name=None):
        handle = self.handle = sa_open_device_by_serial(serialNumber)["handle"]
        self.mode = mode

        self.name = name or 'SA124B: %d' % serialNumber
        self.data = {
            'level': {'actions': ['set', 'get'], 'hint': 'type: number, example: -10.0' },
            'center_span': {'actions': ['set', 'get'], 'hint': 'type: array, example: (1e9, 100e6), meaning: (center, span)' },
            'IQ_config': {'actions': ['set', 'get'], 'hint': 'type: array, example: (1, 250e3), meaning: (decimation, bandwidth)' },
            'sweep_coupling': {'actions': ['set', 'get'], 'hint': 'type: array, example: (10e3, 10e3, 0), meaning: (rbw, vbw, reject)' },
            'acquisition': {'actions': ['set', 'get'], 'hint': 'type: array, example: (0, 0), meaning: (detector, scale)' },
        }
        if mode =='IQ':
            self.data = { **self.data, 'IQ': {'actions': ['get'], 'hint': 'type: array' } }
        if mode =='sweep':
            self.data = { **self.data, 'sweep': {'actions': ['get'], 'hint': 'type: array' } }

        # extra
        sa_set_timebase(handle, 2)
    
    def start(self):
        modes = {'IQ': SA_IQ, 'sweep': SA_SWEEPING}
        sa_initiate(self.handle, modes[self.mode], 0)
        return 'success', 0

    def setValues(self, dic):
        handle = self.handle
        if 'level' in dic:
            sa_config_level(handle, dic['level'])
        if 'center_span' in dic:
            sa_config_center_span(handle, *dic['center_span'])
        if 'IQ_config' in dic:
            sa_config_IQ(handle, *dic['IQ_config'])
        if 'sweep_coupling' in dic:
            sa_config_sweep_coupling(handle, *dic['sweep_coupling'])
        if 'acquisition' in dic:
            sa_config_acquisition(handle, *dic['acquisition'])
        for key in dic:
            self.data[key]['value'] = dic[key]
        return 'success', 0
    
    def getValues(self, keys = None):
        if keys == None: keys = self.data.keys()
        handle = self.handle
        res = {}
        for key in keys:
            if 'value' in self.data[key]:
                res[key] = self.data[key]['value']
        if 'IQ' in keys:
            res = sa_get_IQ_32f(handle)
            IQ = res["iq"]
            res['IQ'] = IQ
        if 'sweep' in keys:
            sweep_info = sa_query_sweep_info(handle)
            sweep = sa_get_sweep_32f(handle)
            res['sweep_info'] = sweep_info; res['sweep'] = sweep
        return 'success', res

    def stop(self):
        handle = self.handle
        sa_close_device(handle)
        return 'success', 0

    #=====================================
    # device specific 
    #=====================================
    def getFreqsAndAmps(self, val):
        info = val['sweep_info']
        freqs = np.array([info["start_freq"] + i * info["bin_size"] for i in range(info["sweep_length"])])
        amps = np.array(val['sweep']['max'])
        return freqs, amps

    def sweep(self, center, span, N, power):
        res = span / N
        assert (res >= 0.1 and res <= 100e3) or (res in [250e3, 6e6]), "res = %.1e\n Available RBWs are [0.1Hz – 100kHz] and 250kHz, 6MHz." % res
        self.setValues({
            'center_span': [center, span], 
            'level': power, 
            'sweep_coupling': [ res, res, 0], 
            'acquisition': [SA_MIN_MAX, SA_LOG_SCALE],
        })
        self.start()
        freqs, amps = self.getFreqsAndAmps(self.getValues()[1])
        return freqs, amps

    def sweepSingle(self, center, power):
        freqs, amps = self.sweep(center, 1, 1, power)
        return np.mean(amps)

if __name__ == '__main__':
    sa124B_IQ = SA124B(serialNumber = 19184645, mode = 'IQ')
    sa124B_IQ.setValues({
        'center_span': [869.0e6, 1.0e3], 'level': -10.0, 'IQ_config': [1, 250.0e3]
    })
    sa124B_IQ.start()
    print(sa124B_IQ.getValues())
    sa124B_IQ.stop()

    sa124B_sweep = SA124B(serialNumber = 19184645, mode = 'sweep')
    sa124B_sweep.setValues({
        'center_span': [1e9, 100e6], 'level': -30.0, 
        'sweep_coupling': [10e3, 10e3, 0], 'acquisition': [0, 0],
    })
    sa124B_sweep.start()
    print(sa124B_sweep.getValues())
    sa124B_sweep.stop()