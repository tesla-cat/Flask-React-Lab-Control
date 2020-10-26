from setuptools import setup

setup(
    name='instrumentserver',
    version='1.0',
    packages=['instrument_plugins'],
    py_modules=['instrument', 'instrument_gui', 'instrument_server', 'instruments_server', 'pythonprocess'],
)
