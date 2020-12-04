
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import _tray_icon_error, _tray_icon_success

class Device:
    def __init__(self, serialNumber):
        self.name = 'Device: %d' % serialNumber
        self.settables = {
            'val1': { 'hint': 'type: number, unit: Hz' },
            'val2': { 'hint': 'type: array, example: (1, 2, 3), meaning: (a, b, c)' },
        }
        self.gettables = self.settables

    def start(self):
        return 'success', 0
    def setValues(self, dic):
        print('setValues for %s: %s' % (self.name, str(dic)) )
        return 'success', 0
    def getValues(self, keys):
        res = {}
        for key in keys:
            res[key] = 'some value'
        return 'success', res
    def stop(self):
        return 'success', 0

statusToIcon = {
    'success': _tray_icon_success,
    'error': _tray_icon_error,
}

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
        groups = { 'set': dev.settables, 'get': dev.gettables }
        for action, group  in groups.items():
            for valName, spec in group.items():
                valKey = '%s!!%s@@%s' % (action, dev.name, valName)
                btnKey = 'btn##%s' % valKey
                Label = sg.T(valName)
                Hint = sg.T('    %s' % spec['hint'])
                Btn = sg.Button(button_text=action, key=btnKey)
                Val = sg.In(key = valKey) if action =='set' else sg.T(size=(40,1), key = valKey)
                rows.append([ Label, Val, Btn ])
                rows.append([ Hint ])
        acts = ['start', 'stop']
        row = [ sg.Button(button_text=act, key='btn##%s' % ('%s!!%s@@null' % (act, dev.name))) for act in acts ]
        rows.append(row)
        return rows

    def run(self):
        App = [[ sg.TabGroup([ self.Tabs.values() ]) ]]
        self.window = sg.Window('App', App)
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            self.handle( event, values )
    
    def handle(self, event, values):
        _, valKey = event.split('##')
        action, devVal = valKey.split('!!')
        devName, valName = devVal.split('@@')
        print(action, devName, valName)
        if action == 'set':
            val = values[valKey]
            if not val: return
            dic = {}
            dic[valName] = eval( val )
            status, result = self.devices[devName].setValues(dic)
        if action == 'get':
            status, result = self.devices[devName].getValues([valName])
            self.window[valKey].update(str(result[valName]))
        if action == 'start': 
            status, result = self.devices[devName].start()
        if action == 'stop':
            status, result = self.devices[devName].stop()
        sg.SystemTray.notify(status, str(result), icon=statusToIcon[status])

if __name__ == '__main__':
    dev1 = Device( serialNumber = 1 )
    dev2 = Device( serialNumber = 2 )
    gui = GUI()
    gui.add([ dev1, dev2 ])
    gui.run()