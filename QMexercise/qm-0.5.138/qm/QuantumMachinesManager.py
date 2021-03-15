import json
import grpc

from qm.QmJob import QmJob
from qm._errors import FailedToExecuteJobException
from qm.utils import _level_map
from qm import _Program
from qm._logger import logger

from qm.QuantumMachine import QuantumMachine
from qm.pb import frontend_pb2_grpc
from google.protobuf import empty_pb2

from qm.pb.frontend_pb2 import ResetDataProcessingRequest, SimulationRequest
from qm.pb.qm_manager_pb2 import OpenQuantumMachineRequest, GetQuantumMachineRequest
from qm._controller import Controller
from qm.persistence import SimpleFileStore, BaseStore
from qm.program import load_config
from qm._user_config import load_user_config
from qm.program.ConfigBuilder import convert_msg_to_config
from qm._SimulationConfig import SimulationConfig, LoopbackInterface


class QuantumMachinesManager(object):
    def __init__(self, host=None, port=None, **kargs):
        """
        :param string host: Host where to find the QM orchestrator. If ``None``, local settings are used
        :param port: Port where to find the QM orchestrator. If None, local settings are used
        """
        super(QuantumMachinesManager, self).__init__()

        config = load_user_config()
        if host is None:
            host = config.manager_host
        if port is None:
            port = config.manager_port

        store: BaseStore = kargs.get("store")
        if not isinstance(store, BaseStore):
            root = kargs.get("file_store_root", ".")
            store = SimpleFileStore(root)
        self._store = store

        self._log = logger
        max_message_size = 1024 * 1024 * 100  # 100 mb in bytes
        self._channel = channel = grpc.insecure_channel(host + ":" + str(port),
                                                        options=[
                                                            ("grpc.max_receive_message_length", max_message_size),
                                                        ],
                                                        compression=grpc.Compression.Gzip
                                                        )
        self._frontend = frontend_pb2_grpc.FrontendStub(channel)
        raise_on_error = config.strict_healthcheck is not False
        if "log_level" in kargs:
            new_level = kargs.get("log_level")
            try:
                logger.setLevel(new_level)
            except ValueError:
                logger.warning("Failed to set log level. level '%s' is not recognized", new_level)
        self.perform_healthcheck(raise_on_error)

        self.validate_version(host)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        return False

    @property
    def store(self) -> BaseStore:
        return self._store

    def perform_healthcheck(self, strict=True):
        """
        Perform a health check against the QM server.

        :param strict: Will raise an exception if health check failed
        """
        with _grpc_context():
            self._log.info("Performing health check")
            req = empty_pb2.Empty()
            res = self._frontend.HealthCheck(req)
            if res.ok:
                self._log.info("Health check passed")
            else:
                self._log.error("Health check FAILED!")
                for msg in res.message:
                    self._log.error("  HC Error: " + msg)
                if strict:
                    raise Exception("Health check failed")

    def version(self):
        """
        :return: The QM server version
        """
        with _grpc_context():
            req = empty_pb2.Empty()
            res = self._frontend.GetVersion(req)
            from qm.version import __version__
            return {
                "client": __version__,
                "server": str(res.value)
            }

    def reset_data_processing(self):
        """
        Stops current data processing for ALL running jobs
        :return:
        """
        with _grpc_context():
            req = ResetDataProcessingRequest()
            self._frontend.ResetDataProcessing(req)

    def close(self):
        self._close()

    def _close(self):
        self._channel.close()

    def open_qm(self, config, close_other_machines=False):
        """
        Opens a new quantum machine

        :param config: The config that will be used by the name machine
        :param close_other_machines: Flag whether to close all other running machines
        :return: A quantum machine obj that can be used to execute programs
        """

        with _grpc_context():
            request = OpenQuantumMachineRequest()

            if close_other_machines:
                request.always = True
            else:
                request.ifNeeded = True

            request.config.CopyFrom(load_config(config))

            result = self._frontend.OpenQuantumMachine(request)
            if not result.success:
                exception = Exception("Can not open QM. Please see previous errors")
                for err in result.configValidationErrors:
                    self._log.error('CONFIG ERROR in key "%s" [%s] : %s', err.path, err.group, err.message)

                for err in result.physicalValidationErrors:
                    self._log.error('PHYSICAL CONFIG ERROR in key "%s" [%s] : %s', err.path, err.group, err.message)

                exception.errors = [(it.group, it.path, it.message) for it in result.configValidationErrors]
                exception.errors += [(it.group, it.path, it.message) for it in result.physicalValidationErrors]

                raise exception

            parsed_config = convert_msg_to_config(request.config)
            return QuantumMachine(result.machineID, request.config, parsed_config, self)

    def open_qm_from_file(self, filename, close_other_machines=True):
        """
        Opens a new quantum machine with config taken from a file on the local file system

        :param filename: The path to the file that contains the config
        :param close_other_machines: Flag whether to close all other running machines
        :return: A quantum machine obj that can be used to execute programs
        """
        with open(filename) as json_file:
            json1_str = json_file.read()

            def remove_nulls(d):
                return {k: v for k, v in d.items() if v is not None}

            config = json.loads(json1_str, object_hook=remove_nulls)
        return self.open_qm(config, close_other_machines)

    def simulate(self, config, program, simulate, **kwargs):
        """
        :param config: A QM config
        :param program: A QUA ``program()`` object to execute
        :param simulate: A ``SimulationConfig`` configuration object
        :param kwargs: additional parameters to pass to execute
        :return: a ``QmJob`` object (see QM Job API).
        """

        if type(program) is not _Program:
            raise Exception("program argument must be of type qm.program.Program")

        with _grpc_context():
            request = SimulationRequest()
            msg_config = load_config(config)
            request.config.CopyFrom(msg_config)

            if type(simulate) is SimulationConfig:
                request.simulate.SetInParent()
                request.simulate.duration = simulate.duration
                request.simulate.includeAnalogWaveforms = simulate.include_analog_waveforms
                request.simulate.includeDigitalWaveforms = simulate.include_digital_waveforms
                if type(simulate.simulation_interface) is LoopbackInterface:
                    request.simulate.simulationInterface.loopback.SetInParent()
                    for connection in simulate.simulation_interface.connections:
                        con = request.simulate.simulationInterface.loopback.connections.add()
                        con.fromController = connection[0]
                        con.fromPort = connection[1]
                        con.toController = connection[2]
                        con.toPort = connection[3]
                else:
                    request.simulate.simulationInterface.none.SetInParent()

                for connection in simulate.controller_connections:
                    con = request.controllerConnections.add()
                    con.source.SetInParent()
                    con.source.controller = connection.source.controller
                    con.source.left = connection.source.is_left_connection
                    con.target.SetInParent()
                    con.target.direct.SetInParent()
                    con.target.direct.controller = connection.target.controller
                    con.target.direct.left = connection.target.is_left_connection

            request.highLevelProgram.CopyFrom(program.build(msg_config))
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

            logger.info("Simulating Qua program")

            response = self._frontend.Simulate(request)

            messages = [
                (_level_map[msg.level], msg.message) for msg in response.messages
            ]

            job_id = response.jobId

            for lvl, msg in messages:
                logger.log(lvl, msg)

            if not response.success:
                logger.error("Job " + job_id + " failed. Failed to execute program.")
                raise FailedToExecuteJobException(job_id)

            return QmJob(self, job_id, response)

    def list_open_quantum_machines(self):
        """
        Return a list of open quantum machines. (Returns only the ids, use ``get_qm(...)`` to get the machine object)

        :return: The ids list
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            open_qms = []
            for qm_id in self._frontend.ListOpenQuantumMachines(request).machineIDs:
                open_qms.append(qm_id)
            return open_qms

    def get_qm(self, machine_id):
        """
        Gets an open quantum machine object with the given machine id

        :param machine_id: The id of the open quantum machine to get
        :return: A quantum machine obj that can be used to execute programs
        """
        with _grpc_context():
            request = GetQuantumMachineRequest()
            request.machineID = machine_id
            result = self._frontend.GetQuantumMachine(request)
            if not result.success:
                self._raise_get_qm_errors(result)
            parsed_config = convert_msg_to_config(result.config)
            return QuantumMachine(result.machineID, result.config, parsed_config, self)

    def _get_qm_config(self, machine_id):
        with _grpc_context():
            request = GetQuantumMachineRequest()
            request.machineID = machine_id
            result = self._frontend.GetQuantumMachine(request)
            if not result.success:
                self._raise_get_qm_errors(result)
            return {"pb_config": result.config, "config": convert_msg_to_config(result.config)}

    def _raise_get_qm_errors(self, result):
        error_str = ""
        for err in result.errors:
            error_str = error_str + err.message + "\n"
        exception = Exception(error_str)
        exception.errors = [(it.code, it.message) for it in result.errors]
        raise exception

    def close_all_quantum_machines(self):
        """
        Closes ALL open quantum machines
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            result = self._frontend.CloseAllQuantumMachines(request)
            if not result.success:
                exception = Exception("Can not close all quantum machines. Please see previous errors")
                for err in result.errors:
                    self._log.error(err.message)

                exception.errors = [(it.code, it.message) for it in result.errors]
                raise exception

    def get_controllers(self):
        """
        Returns a list of all the controllers that are available
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            result = self._frontend.GetControllers(request)
            controllers_list = []
            for controller in result.controllers:
                controllers_list.append(Controller.build_from_message(controller))
            return controllers_list

    def validate_version(self, host):
        version = self.version()
        if version["client"] != version["server"]:
            logger.warning(
                f"Client's version ({version['client']}) does not match the server version ({version['server']}).")

    def clear_all_job_results(self):
        """
        Deletes all data from all previous jobs
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            self._frontend.ClearAllJobResults(request)


class _grpc_context(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, grpc.RpcError):
            # raise RuntimeError("Failed to contact QM manager")
            try:
                details = ": " + exc_val.details()
            except:
                details = ""
            raise RuntimeError("Failed to contact QM manager" + details)
        pass
