
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import _tray_icon_error, _tray_icon_success

class Device:
    def __init__(self, serialNumber):
        self.name = 'Device: %d' % serialNumber
        self.data = {
            'val1': { 'hint': 'type: number, unit: Hz' },
            'val2': { 'hint': 'type: array, example: (1, 2, 3), meaning: (a, b, c)' },
        }

    def setValues(self, dic):
        print('setValues for %s: %s' % (self.name, str(dic)) )

class GUI:
    def __init__(self):
        self.devices = {}
        self.Tabs = {}

    def add(self, devices):
        for dev in devices:
            self.devices[dev.name] = dev
            self.Tabs[dev.name] = sg.Tab(dev.name, self.makeTab(dev))

    def makeTab(self, dev):
        rows = []
        for valName, spec in dev.data.items():
            inputKey = '%s##%s' % (dev.name, valName)
            setBtnKey = '%s$$%s' % ('set', inputKey)
            Label = sg.T(valName)
            Hint = sg.T('    %s' % spec['hint'])
            Input = sg.In(key = inputKey )
            SetBtn = sg.Button(button_text='set', key=setBtnKey)
            rows.append([ Label, Input, SetBtn ])
            rows.append([ Hint ])
        return rows

    def run(self):
        App = [[ sg.TabGroup([ self.Tabs.values() ]) ]]
        window = sg.Window('App', App)
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                break
            self.handle( event, values )
    
    def handle(self, event, values):
        action, inputKey = event.split('$$')
        devName, valName = inputKey.split('##')
        #print(action, devName, valName)
        val = values[inputKey]
        if not val: 
            return
        if action == 'set':
            dic = {}
            dic[valName] = eval( val )
            status, result = self.devices[devName].setValues(dic)
            statusToIcon = {
                'success': _tray_icon_success,
                'error': _tray_icon_error,
            }
            sg.SystemTray.notify(status, str(result), icon=statusToIcon[status])

if __name__ == '__main__':
    dev1 = Device( serialNumber = 1 )
    dev2 = Device( serialNumber = 2 )
    gui = GUI()
    gui.add([ dev1, dev2 ])
    gui.run()