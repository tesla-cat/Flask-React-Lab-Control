from dataclasses import dataclass


class SimulationConfig(object):
    """
    create a configuration object to pass to ``QuantumMachine.simulate``

    :param int duration: The duration to run the simulation for, in clock cycles
    :param bool include_analog_waveforms: Should we collect simulated analog waveform names
    :param bool include_digital_waveforms: Should we collect simulated digital waveform names
    :param SimulatorInterface simulation_interface:

        interface to simulator. Currently supported interfaces:

            ``None`` - zero inputs

            ``LoopbackInterface`` - Loopback output to input (see API)
    :param List[ControllerConnection] controller_connections: A list of connections between the controllers in the config
    """
    duration = 0
    simulate_analog_outputs = False

    def __init__(self, duration=0,
                 include_analog_waveforms=False, include_digital_waveforms=False,
                 simulation_interface=None,
                 controller_connections=[]):
        super(SimulationConfig, self).__init__()
        self.duration = duration
        self.include_analog_waveforms = include_analog_waveforms is True
        self.include_digital_waveforms = include_digital_waveforms is True
        self.simulation_interface = simulation_interface
        self.controller_connections = controller_connections


class SimulatorInterface(object):
    pass


class LoopbackInterface(SimulatorInterface):
    """
    create a loopback interface for simulation

    :param list connections:

        list of tuples with loopback connections. Each tuple can be:

            1. Physical connection between ports:

                ``(fromController: str, fromPort: int, toController: str, toPort: int)``

            2. Virtual connection between quantum elements:

                ``(fromQE: str, toQE: str, toQEInput: int)``

    example::

    >>> job = qm.simulate(prog2, SimulationConfig(
    >>>                   duration=20000,
    >>>                   # loopback from output 1 to input 1:
    >>>                   simulation_interface=LoopbackInterface([("con1", 1, "con1", 1)])
    """

    def __init__(self, connections, latency=24, noisePower=0.0):
        if type(latency) is not int or latency < 0:
            raise Exception("latency must be a positive integer")

        self.latency = latency

        if (type(noisePower) is not float and type(noisePower) is not int) or noisePower < 0:
            raise Exception("noisePower must be a positive number")

        self.noisePower = noisePower

        if type(connections) is not list:
            raise Exception("connections argument must be of type list")

        self.connections = list()
        for connection in connections:
            if type(connection) is not tuple:
                raise Exception("each connection must be of type tuple")
            if len(connection) == 4:
                if type(connection[0]) is not str or type(connection[1]) is not int or \
                        type(connection[2]) is not str or type(connection[3]) is not int:
                    raise Exception("connection should be (fromController, fromPort, toController, toPort)")
                self.connections.append(connection)
            elif len(connection) == 3:
                if type(connection[0]) is not str or type(connection[1]) is not str or type(connection[2]) is not int:
                    raise Exception("connection should be (fromQE, toQE, toQEInput)")
                self.connections.append((connection[0], -1, connection[1], connection[2]))
            else:
                raise Exception("connection should be tuple of length 3 or 4")


class QSimInterface(SimulatorInterface):

    def __init__(self, target, jobId, analogOutConnections=None, digitalOutConnections=None,
                 analogInConnections=None):

        if analogOutConnections is None:
            analogOutConnections = []

        if digitalOutConnections is None:
            digitalOutConnections = []

        if analogInConnections is None:
            analogInConnections = []

        if type(analogOutConnections) is not list or type(digitalOutConnections) is not list or \
                type(analogInConnections) is not list:
            raise Exception("connections arguments must be of type list")

        self._verify_connections(analogOutConnections)
        self._verify_connections(digitalOutConnections)
        self._verify_connections(analogInConnections)

        if type(target) is not str:
            raise Exception("target argument must be of type str")

        if type(jobId) is not str:
            raise Exception("jobId argument must be of type str")

        self.target = target
        self.jobId = jobId
        self.analogOutConnections = analogOutConnections
        self.digitalOutConnections = digitalOutConnections
        self.analogInConnections = analogInConnections

    @staticmethod
    def _verify_connections(connections):
        for connection in connections:
            if type(connection) is not tuple:
                raise Exception("each connection must be of type tuple")
            elif len(connection) == 3:
                if type(connection[0]) is not str or type(connection[1]) is not int or type(connection[2]) is not str:
                    raise Exception("connection should be (fromController, fromPort, toQSimInput)")
            else:
                raise Exception("connection should be tuple of length 3")


@dataclass
class InterOpxAddress:
    """
    :param str controller: The name of the controller
    :param bool is_left_connection:
    """
    controller: str
    is_left_connection: bool


class ControllerConnection(object):
    """

    """
    def __init__(self, source: InterOpxAddress, target: InterOpxAddress):
        self.source = source
        self.target = target
