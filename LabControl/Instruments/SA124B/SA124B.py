
from .sadevice.sa_api import *

class SA124B:
    def __init__(self, serialNumber, mode):
        handle = self.handle = sa_open_device_by_serial(serialNumber)["handle"]
        self.mode = mode
        self.data = {
            'IQ':{'range': [0, 0], 'unit': 'unknown'},
            'sweep':{'range': [0, 0], 'unit': 'unknown'},
        }
    
    def start(self):
        modes = {'IQ': SA_IQ, 'sweep': SA_SWEEPING}
        sa_initiate(self.handle, modes[self.mode], 0)

    def setValues(self, dic):
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
    
    def getValues(self, keys = None):
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

    def stop(self):
        handle = self.handle
        sa_close_device(handle)

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