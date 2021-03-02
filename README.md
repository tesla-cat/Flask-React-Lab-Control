
# LabTools

## LabControl

To understand this part, you need to know: `Python`, `C`, `dll`, `bat`.

This part contains various scripts to control lab equipment such as the signal generator and spectrum analyzer. This is mainly achieved by accessing the `dll` file provided by the manufacturer with Python's built in [ctypes](https://docs.python.org/3/library/ctypes.html) library.

Their application in quantum experiments such as IQ mixer tuning are given as tutorials. 

List of selected experiments:

- [tutorial-2-2-SA124B-MixerTuning.pdf](./LabControl/tutorial-2-2-SA124B-MixerTuning/tutorial-2-2-SA124B-MixerTuning.pdf), [ipynb](./LabControl/tutorial-2-2-SA124B-MixerTuning/tutorial-2-2-SA124B-MixerTuning.ipynb)

The Python library [RPyC](https://rpyc.readthedocs.io/en/latest/) has been used to achieve remote procedure calls.

A GUI to read/write register values of the equipment is written using the Python library [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/).

## LabMonitor

### [Web App Homepage](https://tesla-cat.github.io/LabTools)

### Usage

- In most cases (99.9999...% with 100 0s), you only need to modify the [`./LabMonitor/backend/getData.py`](./LabMonitor/backend/getData.py) file. One can easily see how it works.

- After modifying `getData()` function, execute

```bash
cd ./LabMonitor/backend
node nodeApp.js
```

- This was put into a simple `.bat` file in the lab computer so that users who are not familiar with command line can simply double click on the file to execute

```python
def getData():
  timeS, sensArr = sen.read()
  timeP, presArr = parse(presFile, getVarPressure)
  timeT1, tempArr1 = parse(tempFiles[0], getVarTemperature)
  timeT2, tempArr2 = parse(tempFiles[1], getVarTemperature)
  timeT3, tempArr3 = parse(tempFiles[2], getVarTemperature)
  timeT4, tempArr4 = parse(tempFiles[3], getVarTemperature)
  t = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
  return {
    'xs': [
      { 'l': 'time', 'x': timeP },
      
      { 'l': 'time', 'x': timeT1 },
      { 'l': 'time', 'x': timeT2 },
      { 'l': 'time', 'x': timeT3 },
      { 'l': 'time', 'x': timeT4 },

      { 'l': 'time', 'x': timeS },
    ],
    'ys': [
      { 'l': 'P1 [mbar] OVC', 'y': presArr[:, 0].tolist(), 'x': 0 },
      { 'l': 'P2 [mbar] still', 'y': presArr[:, 1].tolist(), 'x': 0 },
      { 'l': 'P5 [mbar] tank', 'y': presArr[:, 4].tolist(), 'x': 0 },
      
      { 'l': 'T1 [K] 50K', 'y': tempArr1.tolist(), 'x': 1 },
      { 'l': 'T2 [K] 4K', 'y': tempArr2.tolist(), 'x': 2 },
      { 'l': 'T3 [K] still', 'y': tempArr3.tolist(), 'x': 3 },
      { 'l': 'T4 [K] MXC', 'y': tempArr4.tolist(), 'x': 4 },

      # b'freq: 209, flow (L/min): 19, voltage:1.44, pressure (kPa): 384.12, temperature (\xc2\xbaC): 18.56\r'
      { 'l': 'S1 [L/min] flow', 'y': sensArr[:, 1].tolist(), 'x': 5 },
      { 'l': 'S2 [kPa] pressure', 'y': sensArr[:, 3].tolist(), 'x': 5 },
      { 'l': 'S3 [C] temperature', 'y': sensArr[:, 4].tolist(), 'x': 5 },
    ],
    'msg': 'updated: %s' % (t),
  }
```

### Details

To understand this part, you need to know: `Arduino (C++)`, `ESP32`, `Python`, `Node.js`, `yarn`, `JavaScript & TypeScript`, `React.js by Facebook`, `Firebase by Google`.

This part contains different ways of acquiring lab data, such as communication with the IoT microcontroller [ESP32](https://www.espressif.com/en/products/socs/esp32) (which in turn communicates with various sensors via different protocols) and parsing log files. It is recommended to program the `ESP32` board with [Arduino (C++)](https://www.arduino.cc/reference/en/) IDE.

These acquired data are sent to a remote server on the internet for free, specifically to [Firebase by Google](https://firebase.google.com/docs/web/setup). The `Firebase` SDK is used in the `Node.js` environment, which calls `Python` subprocess through the the built in [child_process.js](https://nodejs.org/api/child_process.html#child_process_child_process) module. This combination uses `Node.js`'s **asynchronous processing** strength and `Python`'s **data processing** strength. It is recommended to use `yarn` instead of the built-in `npm` with `Node.js`.

In principle, one only has to modify `Python` file to add/change features, as the `Node.js` part is general and robust. However, in case one needs to modify `Node.js` part, one must learn `JavaScript & TypeScript`, which are less used by physicists.

The frontend App is a Web App and it is hosted by [GitHub Pages](https://pages.github.com/) for free. It is developed with the [React.js](https://reactjs.org/docs/getting-started.html) framework by Facebook, with the help of [Expo CLI](https://docs.expo.io/versions/latest/). The fronted App listens for real time updates from the `Firebase` server, displays the data as a table and plots its history.

## RF Electronics

To understand this part, you need to know: `Altium PCB Designer`, `Gerber`.

List of PCBs:

- [ADRF5020 SPDT RF switch](./RF-Electronics/ADRF5020/ADRF5020-Gerbers.zip)

