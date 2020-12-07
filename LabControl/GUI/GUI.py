
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import _tray_icon_error, _tray_icon_success

class Device:
    def __init__(self, serialNumber):
        self.name = 'Device: %d' % serialNumber
        self.data = {
            'val1': { 'hint': 'type: number, unit: Hz', 'actions': ['set', 'get'] },
            'val2': { 'hint': 'type: array, example: (1, 2, 3), meaning: (a, b, c)', 'actions': ['get'] },
        }
        
    def start(self):
        return 'success', 'start'
    def setValues(self, dic):
        return 'success', 'setValues'
    def getValues(self, keys):
        res = {}
        for key in keys:
            res[key] = 'some value'
        return 'success', res
    def stop(self):
        return 'success', 'stop'

statusToIcon = {
    'success': _tray_icon_success,
    'error': _tray_icon_error,
}

def Txt(text='', key=None, color='blue', bgc='white', size=(None, None), font=None):
    return sg.T(text, key=key, text_color=color, background_color=bgc, size=size, font=font)

class GUI:
    def __init__(self):
        self.devices = {}
        self.Tabs = {}

    def add(self, devices):
        for dev in devices:
            self.devices[dev.name] = dev
            self.Tabs[dev.name] = sg.Tab(dev.name, self.makeTab(dev), background_color='white')
        
    def makeTab(self, dev):
        rows = []
        Btns = [ sg.Button(button_text=action, key= '%s~~%s!!%s' % (dev.name, 'self', action)) for action in ['start', 'stop']]
        rows.append(Btns)
        for valName, spec in dev.data.items():
            valKey = '%s~~%s' % (dev.name, valName)
            Input = sg.In(key = '%s!!%s' % (valKey, 'Input'))
            Text = Txt('click get !', key= '%s!!%s' % (valKey, 'Text'), size=(40,1))
            Btns = [ sg.Button(button_text=action, key= '%s!!%s' % (valKey, action)) for action in spec['actions']]
            rows.append([ Txt(valName, font=20), Txt(spec['hint'], color='grey') ])
            if 'set' in spec['actions']: 
                rows.append([ Txt('set', color='grey'), Input ])
            rows.append([ Txt('get', color='grey'), Text ])
            rows.append([ Txt( size=(35,1) ), *Btns ])
        return rows

    def run(self):
        sg.theme('LightBlue')
        App = [[ sg.TabGroup([ self.Tabs.values() ]) ]]
        self.window = sg.Window('App', App)
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            try:
                status, result = self.handle( event, values )
            except Exception as e:
                status, result = 'error', str(e)
            sg.SystemTray.notify(status, str(result), icon=statusToIcon[status], display_duration_in_ms=1000, fade_in_duration=0)

    def handle(self, event, values):
        valKey, action = event.split('!!')
        devName, valName = valKey.split('~~')
        print(action, devName, valName)
        if action == 'set':
            val = values['%s!!%s' % (valKey, 'Input')]
            if not val: return
            dic = {}
            dic[valName] = eval( val )
            status, result = self.devices[devName].setValues(dic)
        elif action == 'get':
            status, result = self.devices[devName].getValues([valName])
            self.window['%s!!%s' % (valKey, 'Text')].update(str(result[valName]))
        elif action == 'start': 
            status, result = self.devices[devName].start()
        elif action == 'stop':
            status, result = self.devices[devName].stop()
        return status, result

if __name__ == '__main__':
    dev1 = Device( serialNumber = 1 )
    dev2 = Device( serialNumber = 2 )
    gui = GUI()
    gui.add([ dev1, dev2 ])
    gui.run()