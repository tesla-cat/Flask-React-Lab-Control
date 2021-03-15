from typing import Optional
from pathlib import Path
import numpy

from qm._deprecated import deprecated
from qm.pb.job_results_pb2 import PullSimulatorSamplesRequest
from qm.persistence import BinaryAsset, FileBinaryAsset
from qm._results import JobResults
from qm.results.SimulatorSamples import SimulatorSamples

from qm._logger import logger
from qm.pb.frontend_pb2 import IsJobRunningRequest, IsJobAcquiringDataRequest, IsJobAcquiringDataResponse
from qm.pb.frontend_pb2 import ResumeRequest, PausedStatusRequest
from qm.pb.job_results_pb2_grpc import JobResultsServiceStub

from enum import Enum
from io import BytesIO
import numpy.lib.format as _format
import json as _json
from google.protobuf.json_format import MessageToDict


class AcquiringStatus(Enum):
    AcquireStopped = 0
    NoDataToAcquire = 1
    HasDataToAcquire = 2


class QmJob:
    def __init__(self, qmm: 'qm.QuantumMachinesManager.QuantumMachinesManager', job_id: str, execute_response = None):
        super().__init__()
        self._id = job_id
        self._logger = logger.getChild("job")

        self._simulated_analog_outputs = {"samples": None, "waveforms": None}
        self._simulated_digital_outputs = {"samples": None, "waveforms": None}
        if execute_response is not None and execute_response.HasField("simulated"):
            if execute_response.simulated.HasField("analogOutputs"):
                self._simulated_analog_outputs = MessageToDict(execute_response.simulated.analogOutputs)
            if execute_response.simulated.HasField("digitalOutputs"):
                self._simulated_digital_outputs = MessageToDict(execute_response.simulated.digitalOutputs)
            if len(execute_response.simulated.errors) > 0:
                raise RuntimeError('\n'.join(execute_response.simulated.errors))

        self._qmm = qmm
        self._frontend = qmm._frontend

    def id(self):
        """
        :return: The id of the job
        """
        return self._id

    @property
    def manager(self) -> 'qm.QuantumMachinesManager.QuantumMachinesManager':
        """
        The QM object where this job lives
        :return:
        """
        return self._qmm

    def simulated_analog_waveforms(self):
        """
        Return the results of the simulation of quantum elements and analog outputs.

        The returned dictionary has the following keys and entries:

        ``elements``: a dictionary containing the outputs with timestamps and values arranged by quantum elements.

        ``controllers``: a dictionary containing the outputs with timestamps and values arranged by controllers.

            ``ports``: a dictionary containing the outputs with timestamps and values arranged by output ports.

                for each element or output port, the entry is a list of dictionaries with the following information:

                ``timestamp``:

                    The time, in nsec, from the start of the program to the start of the pulse.

                ``samples``:

                    Output information, with ``duration`` given in nsec and ``value`` given normalized OPX output units.


        :return: A dictionary containing output information for the analog outputs of the controller.

        """
        return self._simulated_analog_outputs["waveforms"]

    def simulated_digital_waveforms(self):
        """
        Return the results of the simulation of digital outputs.

        ``controllers``: a dictionary containing the outputs with timestamps and values arranged by controllers.

            ``ports``: a dictionary containing the outputs with timestamps and values arranged by output ports.

                for each element or output port, the entry is a list of dictionaries with the following information:

                ``timestamp``:

                    The time, in nsec, from the start of the program to the start of the pulse.

                ``samples``:

                    A list containing the sequence of outputted values, with ``duration`` given in nsec
                    and ``value`` given as a boolean value.



        :return: A dictionary containing output information for the analog outputs of the controller.
        """
        return self._simulated_digital_outputs["waveforms"]

    def halt(self):
        """
        Halts the job on the opx
        """
        self._logger.error("Currently not implemented. Will be implemented in future releases.")

    @deprecated("use job.results API", version="0.2.0", last="0.2.*")
    def get_saved_results(self, path=None) -> '_SavedResults':
        """
        **DEPRECATED** use job.results API

        Stores the data saved during a QUA program execution on a local file(s).

        :argument path: The local path where the results will be saved
        :type path: None|str

        :return: A SavedResults object
        """
        if path is None:
            self.results.save_to_store()
            asset = self.manager.store.all_job_results(self._id)
            return _SavedResults(asset)
        else:
            self.results.save_to_store(path)
            return _SavedResults(FileBinaryAsset(Path(path)))

    @deprecated("use job.results API", version="0.2.0", last="0.2.*")
    def get_results(self, path=None, ignore_data_loss=False):
        """
        **DEPRECATED** use job.results API
        Obtain the data saved during a QUA program execution from the saved results.

        Results are returned in an object with the following properties:

        ``version``:

            holds the current version of the compiler

        ``errors``:

            if there was a problem retrieving the results, this list will contain the errors that occurred

        ``variable_results``:

            holds the variables that were saved, where each tag used for saving will be a property
            of this object (e.g if the tag used was ``'f'``, the data is stored in ``variable_results.f``)
            The value of each property of ``variable_results`` is a numpy record array holding the values of the
            variables and the timestamps at which they were saved.
            The name of the timestamp column is 'ts_nsec' and the name of the values column is 'values'.
            (i.e. ``data[0]`` returns the first (timestamp, value) tuple, and ``data["values"]`` returns the
            values as a numpy array.)

        ``raw_results``:

            Holds the raw (not demodulated) data acquired by the controller during measure operations
            that were tagged with a 'stream' parameter.
            This object has the following properties:
                
                ``input1``:

                    a numpy record array holding the timestamps and samples from the first
                    input. The name of the timestamp column is 'ts_in_ns' and the name of the samples column
                    is 'values'. (i.e. ``input1[0]`` holds the first pair of timestamp and value.
                    ``input1["values"]`` holds all the samples).
                    Sample values are given in ADC codewords, and range from -2048 to 2047 in steps of 1.

                ``input2``:

                    a numpy record array holding the timestamps and samples from the second
                    input. The name of the timestamp column is 'ts_in_ns' and the name of the samples column
                    is 'values'. (i.e. ``input[0]`` holds the first pair of timestamp and value.
                    ``data["values"]`` holds all the samples).
                    Sample values are given in ADC codewords, and range from -2048 to 2047 in steps of 1.

        :argument path: The local path where the results will be saved
        
        :type path: None|str
        
        :argument ignore_data_loss: If set to ``True``, disables exception raising when possible data loss in ``variable_results`` occurred.
        
        :type ignore_data_loss: bool
        
        :raises: IOError when possible data loss in ``variable_results`` occurred.

        :return: The results of the job.
        """
        if self._sim_results_retreived != True:
            if self._sim_results_retreived == False:
                self._sim_results_retreived = True
            return self.get_saved_results(path).get_numpy_results(ignore_data_loss)
        else:
            raise RuntimeError("simulated results can only be retreived once")

    @deprecated(reason="use new get_np_simulated_samples", version="0.3.0", last="0.3.*")
    def get_saved_simulated_samples(self, path=None, include_analog=True, include_digital=True):
        """
                Stores the samples during a QUA program simulation on a local file(s).

                :argument path: The local path where the results will be saved
                :type path: None|str
                :param include_analog: Should we collect simulated analog samples
                :param include_digital: Should we collect simulated digital samples

                :return: path to npz file
                """
        pass

    def _get_np_simulated_samples(self, path=None, include_analog=True, include_digital=True):
        request = PullSimulatorSamplesRequest()
        request.jobId = self._id
        request.includeAnalog = include_analog
        request.includeDigital = include_digital

        writer = BytesIO()
        data_writer = BytesIO()

        for result in self._frontend.PullSimulatorSamples(request):
            if result.ok:
                one_of = result.WhichOneof("body")
                if one_of == "header":
                    _format.write_array_header_2_0(writer, {
                        "descr": _json.loads(result.header.simpleDType),
                        "fortran_order": False,
                        "shape": (result.header.countOfItems,)
                    })
                elif one_of == "data":
                    data_writer.write(result.data.data)

            else:
                raise RuntimeError("Error while pulling samples")

        data_writer.seek(0)
        for d in data_writer:
            writer.write(d)

        writer.seek(0)
        return numpy.load(writer)

    def get_simulated_samples(self, include_analog=True, include_digital=True):
        """
        Obtain the output samples of a QUA program simulation.

        Samples are returned in an object that holds the controllers in the current simulation,
        where each controller's name will be a property of this object.
        The value of each property of the returned value is an object with the following properties:


        ``analog``:

            holds a dictionary with analog port names as keys and numpy array of samples as values.

        ``digital``:

            holds a dictionary with digital port names as keys and numpy array of samples as values.

       Example::

            >>> samples = job.get_simulated_samples()
            >>> analog1 = samples.con1.analog["1"]  # obtain analog port 1 of controller "con1"
            >>> digital9 = samples.con1.analog["9"] # obtain digital port 9 of controller "con1"

        :param include_analog: Should we collect simulated analog samples
        :param include_digital: Should we collect simulated digital samples

        :return: The simulated samples of the job.
        """
        return SimulatorSamples.from_np_array(
            self._get_np_simulated_samples(include_analog=include_analog, include_digital=include_digital)
        )

    def resume(self):
        """
        Resumes a program that was halted using the pause statement
        """
        request = ResumeRequest()
        request.jobId = self._id
        self._frontend.Resume(request)

    @property
    def result_handles(self) -> JobResults:
        """
        :type: qm._results.JobResults
        :return: A  holding the handles that this job generated
        """
        return JobResults(
            self._id,
            JobResultsServiceStub(self.manager._channel),
            self.manager.store
        )

    def is_paused(self):
        """
        :return: Returns ``True`` if the job is in a paused state.

        see also:

            ``resume()``
        """
        request = PausedStatusRequest()
        request.jobId = self._id

        response = self._frontend.PausedStatus(request)
        return response.isPaused

    @deprecated(reason="use new job results object under job.result_handles.wait_for_all_values", version="0.2.0", last="0.2.*")
    def wait_for_all_results(self, timeout: Optional[int] = None):
        """
        Wait until the job is finished and all the results are available for retrieving

        :argument timeout: The maximum time to wait in seconds
        :type timeout: int

        """
        self.result_handles.wait_for_all_values(timeout)

    def _is_job_running(self):
        """
        :return: Returns ``True`` if the job is running
        """
        request = IsJobRunningRequest()
        request.jobId = self._id

        response = self._frontend.IsJobRunning(request)
        return response.isRunning

    def _is_data_acquiring(self):
        """
        Returns the data acquiring status.
        The possible statuses are: AcquireStopped, NoDataToAcquire,  HasDataToAcquire

        :return: An AcquiringStatus enum object
        """
        request = IsJobAcquiringDataRequest()
        request.jobId = self._id

        response = self._frontend.IsJobAcquiringData(request)
        result = response.acquiringStatus
        if result == IsJobAcquiringDataResponse.ACQUIRE_STOPPED:
            return AcquiringStatus(0)
        elif result == IsJobAcquiringDataResponse.NO_DATA_TO_ACQUIRE:
            return AcquiringStatus(1)
        elif result == IsJobAcquiringDataResponse.HAS_DATA_TO_ACQUIRE:
            return AcquiringStatus(2)


class _SavedResults:

    def __init__(self, asset: BinaryAsset) -> None:
        self._asset = asset
        super().__init__()

    def get_numpy_results(self, *args, **kwargs):
        input = self._asset.for_reading()
        try:
            return numpy.load(input)
        finally:
            input.close()
