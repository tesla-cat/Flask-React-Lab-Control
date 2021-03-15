import json

import numpy

from qm.QmJob import QmJob
from qm.utils import fix_object_data_type as _fix_object_data_type, _level_map
from qm._errors import FailedToExecuteJobException
from qm._logger import logger
from qm._python_to_pb import python_to_pb
from qm.pb.frontend_pb2 import ExecutionRequest, QmDataRequest
from qm.pb.frontend_pb2 import PeekRequest
from qm.pb.frontend_pb2 import PokeRequest
from qm.pb.inc_qm_api_pb2 import HighQmApiRequest
from qm.pb.qm_manager_pb2 import CloseQuantumMachineRequest
from qm.program import _Program
from qm._SimulationConfig import SimulationConfig, LoopbackInterface, QSimInterface
import os
from grpc._channel import _InactiveRpcError


class QuantumMachine(object):
    def __init__(self, machine_id, pb_config, config, manager):
        super(QuantumMachine, self).__init__()
        self._id = machine_id
        self.id = machine_id
        self._pb_config = pb_config
        self._config = config
        self._manager = manager
        self._frontend = manager._frontend
        self._logger = logger.getChild("job")

    @property
    def manager(self) -> 'qm.QuantumMachinesManager.QuantumMachinesManager':
        return self._manager

    def close(self):
        """
        Closes the quantum machine.

        :return: ``True`` if the close request succeeded, Raises an exception otherwise.
        """
        request = CloseQuantumMachineRequest()
        request.machineID = self._id

        result = self._frontend.CloseQuantumMachine(request)
        if not result.success:
            error_str = ""
            for err in result.errors:
                error_str = error_str + err.message + "\n"
            exception = Exception(error_str)
            exception.errors = [(it.code, it.message) for it in result.errors]
            raise exception

        return result.success

    def simulate(self, program, simulate, **kwargs):
        """
        simulate the outputs of a deterministic QUA program.

        Equivalent to ``execute()`` with ``dry_run=True`` and ``simulate=SimulationConfig`` (see example).

        .. note::
            A simulated job does not support calling QuantumMachine API functions.

        The following example shows a simple execution of the simulator, where the associated config object is
        omitted for brevity.

        Example::

            >>> from qm.QuantumMachinesManager import QuantumMachinesManager
            >>> from qm.qua import *
            >>> from qm import SimulationConfig
            >>>
            >>> qmManager = QuantumMachinesManager()
            >>> qm1 = qmManager.open_qm(config)
            >>>
            >>> with program() as prog:
            >>>     play('pulse1', 'qe1')
            >>>
            >>> job = qm1.simulate(prog, SimulationConfig(duration=100))

        :param program: A QUA ``program()`` object to execute
        :param simulate: A ``SimulationConfig`` configuration object
        :param kwargs: additional parameteres to pass to execute
        :return: a ``QmJob`` object (see QM Job API).
        """
        kwargs["dry_run"] = True
        kwargs["simulate"] = simulate
        try:
            job = self.execute(program, **kwargs)
        except _InactiveRpcError as e:
            raise RuntimeError("Error encountered while compiling") from e
        return job

    def execute(self, program,
                duration_limit=1000,
                data_limit=20000,
                force_execution=False,
                dry_run=False,
                **kwargs):
        """
        Executes a program and returns an job object to keep track of execution and get results.

        :param program: A QUA ``program()`` object to execute
        :param duration_limit:

            Maximal time (in msec) for which results will be collected. If set to 0, limit will be disabled.

        :type duration_limit: int
               
        :param data_limit:

            Maximal amount of data sends for which results will be collected. If set to 0, If set to 0, limit will be disabled.

        Here *data sends* is either:

            1. 4 ADC samples, in case raw data is transferred
            2. a single save operation

        .. note::
        
            Disabling data acquisition limit can lead to a very large amount of data stored in the server and/or user PC.

        :type data_limit: int
        :param force_execution: Execute program even if another program is currently running
        :type force_execution: bool
        :param dry_run: compile program but do not run it
        :type dry_run: bool

        No new results will be available to the returned job object When
        ``duration_limit`` is reached, or when ``data_limit`` is reached,
        whichever occurs sooner.

        :return: A ``QmJob`` object (see QM Job API).

        """

        if type(program) not in (_Program, str):
            raise Exception("program argument must be of type qm.program.Program")

        request = ExecutionRequest()
        request.quantumMachineId = self._id

        simulation = kwargs.get("simulate", None)
        if type(simulation) is SimulationConfig:
            request.simulate.SetInParent()
            request.simulate.duration = simulation.duration
            request.simulate.includeAnalogWaveforms = simulation.include_analog_waveforms
            request.simulate.includeDigitalWaveforms = simulation.include_digital_waveforms
            if type(simulation.simulation_interface) is LoopbackInterface:
                request.simulate.simulationInterface.loopback.SetInParent()
                request.simulate.simulationInterface.loopback.latency = simulation.simulation_interface.latency
                request.simulate.simulationInterface.loopback.noisePower = simulation.simulation_interface.noisePower
                for connection in simulation.simulation_interface.connections:
                    con = request.simulate.simulationInterface.loopback.connections.add()
                    con.fromController = connection[0]
                    con.fromPort = connection[1]
                    con.toController = connection[2]
                    con.toPort = connection[3]
            elif type(simulation.simulation_interface) is QSimInterface:
                request.simulate.simulationInterface.qsim.SetInParent()
                request.simulate.simulationInterface.qsim.target = simulation.simulation_interface.target
                request.simulate.simulationInterface.qsim.jobId = simulation.simulation_interface.jobId
                for connection in simulation.simulation_interface.analogOutConnections:
                    con = request.simulate.simulationInterface.qsim.analogOutConnections.add()
                    con.fromController = connection[0]
                    con.fromPort = connection[1]
                    con.toQSim = connection[2]
                for connection in simulation.simulation_interface.digitalOutConnections:
                    con = request.simulate.simulationInterface.qsim.digitalOutConnections.add()
                    con.fromController = connection[0]
                    con.fromPort = connection[1]
                    con.toQSim = connection[2]
                for connection in simulation.simulation_interface.analogInConnections:
                    con = request.simulate.simulationInterface.qsim.analogInConnections.add()
                    con.fromController = connection[0]
                    con.fromPort = connection[1]
                    con.toQSim = connection[2]
            else:
                request.simulate.simulationInterface.none.SetInParent()

        if type(program) is _Program:
            request.highLevelProgram.CopyFrom(program.build(self._pb_config))
            request.highLevelProgram.compilerOptions.optimizeMergeCodeExecution = \
                kwargs.get("optimize_merge_code_execution") is not False
            request.highLevelProgram.compilerOptions.optimizeWriteReadCommands = \
                kwargs.get("optimize_read_write_commands") is True
            request.highLevelProgram.compilerOptions.strict = \
                kwargs.get("strict", False) is True

            # handle deprecated skip_optimizations (backwards compatible for future flags)
            skip_optimizations = kwargs.get("skip_optimizations", None)
            if skip_optimizations is None:
                pass
            elif type(skip_optimizations) is tuple:
                optimization_to_skip = []
                for opt in skip_optimizations:
                    if type(opt) is str:
                        request.highLevelProgram.compilerOptions.skipOptimizations.append(opt)
                        optimization_to_skip.append(opt)
                logger.info("Skipping optimizations: " + ",".join(optimization_to_skip))
            else:
                logger.warn("skip_optimizations must be a tuple of strings")

            # handle deprecated extra_optimizations (backwards compatible for future flags)
            extra_optimizations = kwargs.get("extra_optimizations", None)
            if extra_optimizations is None:
                pass
            elif type(extra_optimizations) is tuple:
                optimization_to_add = []
                for opt in extra_optimizations:
                    if type(opt) is str:
                        request.highLevelProgram.compilerOptions.skipOptimizations.append("!" + opt)
                        optimization_to_add.append(opt)
                logger.info("extra optimizations: " + ",".join(optimization_to_add))
            else:
                logger.warn("extra_optimizations must be a tuple of strings")

            try:
                flags_arg = kwargs.get("flags", [])
                flags = (opt for opt in flags_arg if type(opt) is str)
            except TypeError:
                flags = []
            for opt in flags:
                request.highLevelProgram.compilerOptions.flags.append(opt)
            logger.info("Flags: " + ",".join(flags))

            logger.info("Executing high level program")
        else:
            if os.path.isfile(program):
                with open(program, mode='rb') as file:
                    request.lowLevelProgram = file.read()
            else:
                raise Exception("could not find low level program file: " + program)
            logger.info("Executing low level program")

        request.streamDurationLimit = duration_limit
        request.streamDataLimit = data_limit
        request.forceExecution = force_execution
        request.dryRun = dry_run
        response = self._frontend.Execute(request)
        # outputs = program.result_analysis().get_outputs()

        messages = [
            (_level_map[msg.level], msg.message) for msg in response.messages
        ]

        job_id = response.jobId

        for lvl, msg in messages:
            self._logger.log(lvl, msg)

        if not response.ok:
            self._logger.error("Job " + job_id + " failed. Failed to execute program.")
            raise FailedToExecuteJobException(job_id)

        return QmJob(self.manager, job_id, response)

    def list_controllers(self):
        """
        Gives a list with the defined controllers in this qm

        :return: The names of the controllers configured in this qm
        """
        return tuple(self.get_config()["controllers"].keys())

    def set_mixer_correction(self, mixer, intermediate_frequency, lo_frequency, values):
        """
        Sets the correction matrix for correcting gain and phase imbalances
        of an IQ mixer for the supplied intermediate frequency and LO frequency.

        :param mixer: the name of the mixer, as defined in the configuration
        :type mixer: str
        :param intermediate_frequency: the intermediate frequency for which to apply the correction matrix
        :type intermediate_frequency: long
        :param lo_frequency: the LO frequency for which to apply the correction matrix
        :type lo_frequency: long
        :param values:

            tuple is of the form (v00, v01, v10, v11) where
            the matrix is
            | v00 v01 |
            | v10 v11 |

        :type values: tuple
        """
        if (type(values) is not tuple and type(values) is not list) or len(values) != 4:
            raise Exception("correction values must be a tuple of 4 items")

        values = [_fix_object_data_type(x) for x in values]

        request = self._init_qm_request()

        request.setCorrection.mixer.mixer = mixer
        request.setCorrection.mixer.intermediateFrequency = abs(intermediate_frequency)
        request.setCorrection.mixer.frequencyNegative = intermediate_frequency < 0
        request.setCorrection.mixer.loFrequency = lo_frequency

        request.setCorrection.correction.v00 = values[0]
        request.setCorrection.correction.v01 = values[1]
        request.setCorrection.correction.v10 = values[2]
        request.setCorrection.correction.v11 = values[3]
        response = self._frontend.PerformQmRequest(request)
        self._handle_qm_api_response(response)

    def set_correction(self, qe, values):
        """
        **DEPRECATED** This method is deprecated. Using this method will update the correction for ALL elements that use the same mixer config
        as the supplied element. Use set_mixer_correction(..) instead.

        Sets the correction matrix for correcting gain and phase imbalances
        of an IQ mixer associated with a quantum element.

        :param qe: the name of the element to update the correction for
        :type qe: str
        :param values:

            tuple is of the form (v00, v01, v10, v11) where
            the matrix is
            | v00 v01 |
            | v10 v11 |

        :type values: tuple
        :type values: tuple
        """
        logger.warning("set_correction(..) is deprecated. use set_mixer_correction(..) instead")
        if type(qe) is not str:
            raise Exception("qe must be a string")
        if (type(values) is not tuple and type(values) is not list) or len(values) != 4:
            raise Exception("correction values must be a tuple of 4 items")

        values = [_fix_object_data_type(x) for x in values]

        request = self._init_qm_request()
        request.setCorrection.qe = qe
        # request.setCorrection.correction
        request.setCorrection.correction.v00 = values[0]
        request.setCorrection.correction.v01 = values[1]
        request.setCorrection.correction.v10 = values[2]
        request.setCorrection.correction.v11 = values[3]
        response = self._frontend.PerformQmRequest(request)
        self._handle_qm_api_response(response)

    def set_frequency(self, qe, freq):
        """
        **DEPRECATED** This method is deprecated. Use set_intermediate_frequency(..) instead

         Sets the frequency of an element, at the output of the mixer, taking LO frequency into account.

        :param qe: the name of the element to update the correction for
        :param freq: the frequency to set to the given element
        :type qe: str
        :type freq: float

        .. note::

            if an intermediate_frequency entry corresponding to ``freq`` does not exist in the mixer correction list
            of the mixer corresponding to the quantum element, an entry will be created.
            The entry will be populated with the values of the current correction matrix.

        """
        logger.warning("set_frequency(..) is deprecated. use set_intermediate_frequency(..) instead")
        if type(qe) is not str:
            raise Exception("qe must be a string")
        if not isinstance(freq, (numpy.floating, float)):
            raise Exception("freq must be a float")

        config = self.get_config()
        if qe not in config['elements']:
            raise Exception("qe does not exist")

        element = config['elements'][qe]

        if 'singleInput' in element:
            self.set_intermediate_frequency(qe, freq)
        else:
            intermediate_frequency = freq - element['mixInputs']['lo_frequency']
            self.set_intermediate_frequency(qe, intermediate_frequency)

    def set_intermediate_frequency(self, element, freq):
        """
        Sets the intermediate frequency of the the quantum element

        :param element: the name of the element whose intermediate frequency will be updated
        :type element: str
        :param freq: the intermediate frequency to set to the given element
        :type freq: float

        .. note::

            if an intermediate_frequency entry corresponding to ``freq`` does not exist in the mixer correction list
            of the mixer corresponding to the quantum element, an entry will be created.
            The entry will be populated with the values of the current correction matrix.

        """
        logger.debug("Setting element '%s' intermediate frequency to '%s'", element, freq)
        if type(element) is not str:
            raise TypeError("element must be a string")
        if not isinstance(freq, (numpy.floating, float)):
            raise TypeError("freq must be a float")

        freq = _fix_object_data_type(freq)

        request = self._init_qm_request()
        request.setFrequency.qe = element
        request.setFrequency.value = freq
        response = self._frontend.PerformQmRequest(request)
        self._handle_qm_api_response(response)

    def get_dc_offset_by_qe(self, qe, input):
        """
        **DEPRECATED** This method is deprecated. Use get_output_dc_offset_by_element(..) instead

        get the current DC offset of the OPX analog output channel associated with a quantum element.

        :param qe: the name of the element to get the correction for
        :param input: the input name as appears in the element's config **be more specific here**
        :return: the offset, in normalized output units
        """
        logger.warning("get_dc_offset_by_qe(..) is deprecated. use get_output_dc_offset_by_element(..) instead")
        self.get_output_dc_offset_by_element(qe, input)

    def get_output_dc_offset_by_element(self, element, input):
        """
        get the current DC offset of the OPX analog output channel associated with a quantum element.

        :param element: the name of the element to get the correction for
        :param input: the input name as appears in the element's config **be more specific here**
        :return: the offset, in normalized output units
        """
        config = self.get_config()

        if element in config["elements"]:
            element_obj = config["elements"][element]
        else:
            raise Exception("Element not found")

        if "singleInput" in element_obj:
            port = element_obj["singleInput"]["port"]
        elif "mixInputs" in element_obj:
            port = element_obj["mixInputs"][input]
        else:
            raise Exception("Port not found")

        if port[0] in config["controllers"]:
            controller = config["controllers"][port[0]]
        else:
            raise Exception("Controller does not exist")

        if port[1] in controller["analog_outputs"]:
            return controller["analog_outputs"][port[1]]["offset"]
        else:
            raise Exception("Port not found")

    def set_dc_offset_by_qe(self, qe, input, offset):
        """
        ***DEPRECATED***  "This method is deprecated. Use set_output_dc_offset_by_element(..) instead." *****
        set the current DC offset of the OPX analog output channel associated with a quantum element.

        :param qe: the name of the element to update the correction for
        :type qe: str
        :param input:
            the input name as appears in the element config. Options:

            `'single'`
                for an element with single input

            `'I'` or `'Q'`
                for an element with mixer inputs

        :type input: str
        :param offset: the dc value to set to, in normalized output units. Ranges from -0.5 to 0.5 - 2^-16 in steps of 2^-16.
        :type offset: float

        .. warning::

            if the sum of the DC offset and the largest waveform data-point exceed the normalized unit range specified
            above, DAC output overflow will occur and the output will be corrupted.
        """
        logger.debug("This method is deprecated. Use set_output_dc_offset_by_qe(..) instead.")
        return self.set_output_dc_offset_by_element(qe, input, offset)

    def set_output_dc_offset_by_element(self, element, input, offset):
        """
        set the current DC offset of the OPX analog output channel associated with a quantum element.

        :param element: the name of the element to update the correction for
        :type element: str
        :param input:
            the input name as appears in the element config. Options:

            `'single'`
                for an element with single input

            `'I'` or `'Q'`
                for an element with mixer inputs

        :type input: str
        :param offset: the dc value to set to, in normalized output units. Ranges from -0.5 to 0.5 - 2^-16 in steps of 2^-16.
        :type offset: float

        .. warning::

            if the sum of the DC offset and the largest waveform data-point exceed the normalized unit range specified
            above, DAC output overflow will occur and the output will be corrupted.
        """
        logger.debug("Setting DC offset of port '%s' on element '%s' to '%s'", input, element, offset)
        if type(element) is not str:
            raise TypeError("element must be a string")
        if type(input) is not str:
            raise TypeError("port must be a string")
        if not isinstance(offset, (numpy.floating, float)):
            raise TypeError("I must be a float")

        offset = _fix_object_data_type(offset)

        request = self._init_qm_request()
        request.setOutputDcOffset.qe.qe = element
        request.setOutputDcOffset.qe.port = input
        request.setOutputDcOffset.I = offset
        request.setOutputDcOffset.Q = offset
        response = self._frontend.PerformQmRequest(request)
        return self._handle_qm_api_response(response)

    def set_input_dc_offset_by_element(self, element, output, offset):
        """
        set the current DC offset of the OPX analog input channel associated with a quantum element.

        :param element: the name of the element to update the correction for
        :type element: str
        :param output:
            the output key name as appears in the element config under 'outputs'.
        :type output: str
        :param offset: the dc value to set to, in normalized input units. Ranges from -0.5 to 0.5 - 2^-16 in steps of 2^-16.
        :type offset: float

        .. warning::
            if the sum of the DC offset and the largest waveform data-point exceed the normalized unit range specified
            above, DAC output overflow will occur and the output will be corrupted.
        """
        logger.debug("Setting DC offset of port '%s' on element '%s' to '%s'", output, element, offset)
        if type(element) is not str:
            raise TypeError("element must be a string")
        if type(output) is not str:
            raise TypeError("port must be a string")
        if not isinstance(offset, (numpy.floating, float)):
            raise TypeError("offset must be a float")

        offset = _fix_object_data_type(offset)

        request = self._init_qm_request()
        request.setInputDcOffset.qe.qe = element
        request.setInputDcOffset.qe.port = output
        request.setInputDcOffset.offset = offset
        response = self._frontend.PerformQmRequest(request)
        return self._handle_qm_api_response(response)

    def get_input_dc_offset_by_element(self, element, output):
        """
        get the current DC offset of the OPX analog input channel associated with a quantum element.

        :param element: the name of the element to get the correction for
        :param output: the output name as appears in the element's config **be more specific here**
        :return: the offset, in normalized output units
        """
        config = self.get_config()

        if element in config["elements"]:
            element_obj = config["elements"][element]
        else:
            raise Exception("Element not found")

        if "outputs" in element_obj:
            outputs = element_obj["outputs"]
        else:
            raise Exception("Element has not outputs")

        if output in outputs:
            port = outputs[output]
        else:
            raise Exception("Output does not exist")

        if port[0] in config["controllers"]:
            controller = config["controllers"][port[0]]
        else:
            raise Exception("Controller does not exist")

        if "analog_inputs" not in controller:
            raise Exception("Controller has not analog inputs defined")

        if port[1] in controller["analog_inputs"]:
            return controller["analog_inputs"][port[1]]["offset"]
        else:
            raise Exception("Port not found")

    def get_digital_delay(self, element, digital_input):
        """
        :param element: the name of the element to get the delay for
        :param digital_input: the digital input name as appears in the element's config
        :return: the delay
        """
        element_object = None
        for e in self.get_config()["elements"]:
            if e.name == element:
                element_object = e
                break

        if element_object is None:
            raise Exception("element not found")

        for di in element_object["digitalInputs"]:
            if di.name == digital_input:
                return di.delay

        raise Exception("digital input not found")

    def set_digital_delay(self, element, digital_input, delay):
        """
        Sets the delay of the digital waveform of the quantum element

        :param element: the name of the element to update delay for
        :type element: str
        :param digital_input: the digital input name as appears in the element's config
        :type digital_input: str
        :param delay: the delay value to set to, in nsec. Range: 0 to 255 - 2 * buffer, in steps of 1
        :type delay: int
        """
        logger.debug("Setting delay of digital port '%s' on element '%s' to '%s'", digital_input, element, delay)
        if type(element) is not str:
            raise Exception("element must be a string")
        if type(digital_input) is not str:
            raise Exception("port must be a string")
        if type(delay) is not int:
            raise Exception("delay must be an int")

        request = self._init_qm_request()
        request.setDigitalRoute.delay.qe = element
        request.setDigitalRoute.delay.port = digital_input
        request.setDigitalRoute.value = delay

        response = self._frontend.PerformQmRequest(request)
        return self._handle_qm_api_response(response)

    def get_digital_buffer(self, element, digital_input):
        """
        get the buffer for digital waveforms of the quantum element

        :param element: the name of the element to get the buffer for
        :type element: str
        :param digital_input: the digital input name as appears in the element's config
        :type digital_input: str
        :return: the buffer
        """
        element_object = None
        for e in self.get_config()["elements"]:
            if e.name == element:
                element_object = e
                break

        if element_object is None:
            raise Exception("element not found")

        for di in element_object["digitalInputs"]:
            if di.name == digital_input:
                return di.buffer

        raise Exception("digital input not found")

    def set_digital_buffer(self, element, digital_input, buffer):
        """
        set the buffer for digital waveforms of the quantum element

        :param element: the name of the element to update buffer for
        :type element: str
        :param digital_input: the digital input name as appears in the element's config
        :type digital_input: str
        :param buffer: the buffer value to set to, in nsec. Range: 0 to (255 - delay) / 2, in steps of 1
        :type buffer: int
        """
        logger.debug("Setting buffer of digital port '%s' on element '%s' to '%s'", digital_input, element, buffer)
        if type(element) is not str:
            raise Exception("element must be a string")
        if type(digital_input) is not str:
            raise Exception("port must be a string")
        if type(buffer) is not int:
            raise Exception("buffer must be an int")

        request = self._init_qm_request()
        request.setDigitalRoute.buffer.qe = element
        request.setDigitalRoute.buffer.port = digital_input
        request.setDigitalRoute.value = buffer

        response = self._frontend.PerformQmRequest(request)
        return self._handle_qm_api_response(response)

    def get_time_of_flight(self, element):
        """
        get the *time of flight*, associated with a measurement quantum element.

        This is the amount of time between the beginning of a measurement pulse applied to quantum element
        and the time that the data is available to the controller for demodulation or streaming.

        :param element: the name of the element to get time of flight for
        :type element: str
        :return: the time of flight, in nsec
        """
        element_object = None
        for e in self.get_config()["elements"]:
            if e.name == element:
                return e["time_of_flight"]

        if element_object is None:
            raise Exception("element not found")

    def get_smearing(self, element):
        """
        get the *smearing* associated with a measurement quantum element.

        This is a broadening of the raw results acquisition window, to account for dispersive broadening
        in the measurement elements (readout resonators etc.) The acquisition window will be broadened
        by this amount on both sides.

        :param element: the name of the element to get smearing for
        :type element: str
        :return: the smearing, in nesc.
        """
        element_object = None
        for e in self.get_config()["elements"]:
            if e.name == element:
                return e["smearing"]

        if element_object is None:
            raise Exception("element not found")

    def set_io1_value(self, value_1):
        """
        Sets the value of ``IO1``.

        This can be used later inside a QUA program as a QUA variable ``IO1`` without declaration.
        The type of QUA variable is inferred from the python type passed to ``value_1``, according to the following rule:

        int -> int
        float -> fixed
        bool -> bool

        :param value_1: the value to be placed in ``IO1``
        :type value_1: float | bool | int
        """
        self.set_io_values(value_1, None)

    def set_io2_value(self, value_2):
        """
        Sets the value of ``IO1``.

        This can be used later inside a QUA program as a QUA variable ``IO2`` without declaration.
        The type of QUA variable is inferred from the python type passed to ``value_2``, according to the following rule:

        int -> int
        float -> fixed
        bool -> bool

        :param value_1: the value to be placed in ``IO1``
        :type value_1: float | bool | int
        """
        self.set_io_values(None, value_2)

    def set_io_values(self, value_1, value_2):
        """
        Sets the value of ``IO1`` and ``IO2``

        This can be used later inside a QUA program as a QUA variable ``IO1``, ``IO2`` without declaration.
        The type of QUA variable is inferred from the python type passed to ``value_1``, ``value_2``,
        according to the following rule:

        int -> int
        float -> fixed
        bool -> bool

        :param value_1: the value to be placed in ``IO1``
        :param value_2: the value to be placed in ``IO2``
        :type value_1: float | bool | int
        :type value_2: float | bool | int
        """

        if value_1 is None and value_2 is None:
            return

        if value_1 is not None:
            logger.debug("Setting value '%s' to IO1", value_1)
        if value_2 is not None:
            logger.debug("Setting value '%s' to IO2", value_2)

        request = self._init_qm_request()
        request.setIOValues.all = True

        value_1 = _fix_object_data_type(value_1)
        value_2 = _fix_object_data_type(value_2)

        if type(value_1) is int:
            request.setIOValues.ioValueSetData.add(io_number=1, intValue=value_1)
        elif type(value_1) is float:
            request.setIOValues.ioValueSetData.add(io_number=1, doubleValue=value_1)
        elif type(value_1) is bool:
            request.setIOValues.ioValueSetData.add(io_number=1, booleanValue=value_1)
        elif value_1 is None:
            pass
        else:
            raise Exception("Invalid value_1 type (The possible types are: int, bool or float)")

        if type(value_2) is int:
            request.setIOValues.ioValueSetData.add(io_number=2, intValue=value_2)
        elif type(value_2) is float:
            request.setIOValues.ioValueSetData.add(io_number=2, doubleValue=value_2)
        elif type(value_2) is bool:
            request.setIOValues.ioValueSetData.add(io_number=2, booleanValue=value_2)
        elif value_2 is None:
            pass
        else:
            raise Exception("Invalid value_2 type (The possible types are: int, bool or float)")

        response = self._frontend.PerformQmRequest(request)
        return self._handle_qm_api_response(response)

    def _init_qm_request(self):
        request = HighQmApiRequest()
        self.get_config()
        request.config.root.CopyFrom(python_to_pb(self._config).struct_value)
        request.config.version = self._config["version"] if "version" in self._config else 1
        request.strongConfig.CopyFrom(self._pb_config)
        request.quantumMachineId = self._id
        return request

    @staticmethod
    def _handle_qm_api_response(response):
        if not response.ok:
            msg = "\n\t" + "\n\t".join([it.message for it in response.errors])
            logger.error("Failed: %s", msg)
            raise RuntimeError("\n".join([it.message for it in response.errors]))

    def get_io1_value(self):
        """
        Gives the data stored in ``IO1``

        No inference is made on type.

        :return:
            A dictionary with data stored in ``IO1``.
            (Data is in all three format: ``int``, ``float`` and ``bool``)
        """
        return self.get_io_values()[0]

    def get_io2_value(self):
        """
        Gives the data stored in ``IO2``

        No inference is made on type.

        :return:
            A dictionary with data from the second IO register.
            (Data is in all three format: ``int``, ``float`` and ``bool``)
        """
        return self.get_io_values()[1]

    def get_io_values(self):
        """
        Gives the data stored in both ``IO1`` and ``IO2``

        No inference is made on type.

        :return:
            A list that contains dictionaries with data from the IO registers.
            (Data is in all three format: ``int``, ``float`` and ``bool``)
        """
        request = QmDataRequest()
        request.io_value_Request.add(io_number=1, quantumMachineId=self._id)
        request.io_value_Request.add(io_number=2, quantumMachineId=self._id)
        response = self._frontend.RequestData(request)

        resp1 = response.io_value_response[0]
        resp2 = response.io_value_response[1]

        return [{"io_number": 1, "int_value": resp1.values.int_value, "fixed_value": resp1.values.double_value,
                 "boolean_value": resp1.values.boolean_value},
                {"io_number": 2, "int_value": resp2.values.int_value, "fixed_value": resp2.values.double_value,
                 "boolean_value": resp2.values.boolean_value}]

    def peek(self, address):
        raise NotImplementedError()
        # if you must use this, code below will work for a specific controller
        #request = PeekRequest()
        #request.controllerId = list(self._config["controllers"].keys())[0]
        #request.address = address

        #return self._frontend.Peek(request)

    def poke(self, address, value):

        request = PokeRequest()
        request.address = address
        request.value = value

        return self._frontend.Poke(request)

    def get_config(self):
        """
        Gives the current config of the qm

        :return: A dictionary with the qm's config
        """
        configs = self._manager._get_qm_config(self._id)
        self._pb_config = configs["pb_config"]
        self._config = configs["config"]
        return self._config

    def save_config_to_file(self, filename):
        """
        Saves the qm current config to a file

        :param: filename: The name of the file where the config will be saved
        """
        json_str = json.dumps(self.get_config())
        with open(filename, 'w') as writer:
            writer.write(json_str)
