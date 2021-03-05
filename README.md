
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

- You only need to modify the [`./LabMonitor/backend/getData.py`](./LabMonitor/backend/getData.py) file. One can easily see how it works.

- After modifying `getData()` function, execute

```bash
cd ./LabMonitor/backend
node nodeApp.js
```

- This was put into a simple `.bat` file in the lab computer so that users who are not familiar with command line can simply double click on the file to execute

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

## QubitEBLdesign

To understand this part, you need to know: `Transmon Quantum Circuit`, `Electron-beam lithography (EBL)`, `GDSII file`.

This is a python program that automatically generates an array of Transmon quantum circuits with varying parameters for Electron-beam lithography manufacturing. 

## TemperatureControlBox

To understand this part, you need to know: `Raspberry Pi`, `PID controller`, `Pulse-width modulation (PWM)`.

This is a temperature control box to host RF electronic devices, to reduce the device noises caused by temperature fluctuation. [Read more here](./TemperatureControlBox/README.md).
