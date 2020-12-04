
from .sadevice.sa_api import *

class SA124B:
    def __init__(self, serialNumber, mode):
        handle = self.handle = sa_open_device_by_serial(serialNumber)["handle"]
        self.mode = mode

        self.name = 'SA124B: %d' % serialNumber
        self.settables = {
            'level': { 'hint': 'type: number, example: -10.0' },
            'center_span': { 'hint': 'type: array, example: (1e9, 100e6), meaning: (center, span)' },
            'IQ': { 'hint': 'type: array, example: (1, 250e3), meaning: (decimation, bandwidth)' },
            'sweep_coupling': { 'hint': 'type: array, example: (10e3, 10e3, 0), meaning: (rbw, vbw, reject)' },
            'acquisition': { 'hint': 'type: array, example: (0, 0), meaning: (detector, scale)' },
        }
        if mode =='IQ':
            self.gettables = {
                'IQ': { 'hint': 'type: array' },
            }
        if mode =='sweep':
            self.gettables = {
                'sweep': { 'hint': 'type: array' }, 
            }
    
    def start(self):
        try:
            modes = {'IQ': SA_IQ, 'sweep': SA_SWEEPING}
            sa_initiate(self.handle, modes[self.mode], 0)
            return 'success', 0
        except Exception as e:
            return 'error', str(e)

    def setValues(self, dic):
        try:
            handle = self.handle
            if 'center_span' in dic:
                sa_config_center_span(handle, *dic['center_span'])
            if 'level' in dic:
                sa_config_level(handle, dic['level'])
            if 'IQ' in dic:
                sa_config_IQ(handle, *dic['IQ'])
            if 'sweep_coupling' in dic:
                sa_config_sweep_coupling(handle, *dic['sweep_coupling'])
            if 'acquisition' in dic:
                sa_config_acquisition(handle, *dic['acquisition'])
            return 'success', 0
        except Exception as e:
            return 'error', str(e)
    
    def getValues(self, keys = None):
        try:
            if keys == None: keys = self.mode 
            handle = self.handle
            res = {}
            if 'IQ' in keys:
                IQ = sa_get_IQ_32f(handle)["iq"]
                res['IQ'] = IQ
            if 'sweep' in keys:
                sweep_info = sa_query_sweep_info(handle)
                sweep = sa_get_sweep_32f(handle)
                res['sweep_info'] = sweep_info; res['sweep'] = sweep
            return 'success', res
        except Exception as e:
            return 'error', str(e)

    def stop(self):
        try:
            handle = self.handle
            sa_close_device(handle)
            return 'success', 0
        except Exception as e:
            return 'error', str(e)

if __name__ == '__main__':
    sa124B_IQ = SA124B(serialNumber = 19184645, mode = 'IQ')
    sa124B_IQ.setValues({
        'center_span': [869.0e6, 1.0e3], 'level': -10.0, 'IQ': [1, 250.0e3]
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