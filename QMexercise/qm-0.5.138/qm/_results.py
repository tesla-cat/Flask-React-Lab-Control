import time
import zipfile
from io import BufferedWriter, BytesIO
from typing import Optional, Union, Dict, Tuple, Generator
import numpy
import numpy.lib.format as _format
import json as _json
from dataclasses import dataclass
from qm._logger import logger
from qm.pb.job_results_pb2_grpc import JobResultsServiceStub
from qm.pb.job_results_pb2 import (
    GetJobNamedResultHeaderRequest,
    GetJobNamedResultRequest,
    GetJobResultSchemaRequest,
    GetJobResultSchemaResponse
)
from qm.persistence import BaseStore


def _parse_dtype(simple_dtype: str) -> dict:
    dtype = _json.loads(simple_dtype)
    return dtype


@dataclass
class JobResultItemSchema:
    name: str
    dtype: dict
    is_single: bool
    expected_count: int


@dataclass
class JobResultSchema:
    items: Dict[str, JobResultItemSchema]


@dataclass
class NamedJobResultHeader:
    count_so_far: int
    is_single: bool
    output_name: str
    job_id: str
    d_type: dict
    done: bool
    closed: bool
    has_dataloss: bool


class BaseNamedJobResult:
    def __init__(
            self,
            job_id: str,
            schema: JobResultItemSchema,
            service: JobResultsServiceStub,
            store: BaseStore,
    ) -> None:
        super().__init__()
        self._job_id = job_id
        self._schema = schema
        self._service = service
        self._store = store

    @property
    def name(self) -> str:
        """The name of result this handle is connected to"""
        return self._schema.name

    @property
    def job_id(self) -> str:
        """The job id this result came from"""
        return self._job_id

    @property
    def expected_count(self) -> int:
        return self._schema.expected_count

    @property
    def numpy_dtype(self):
        return self._schema.dtype

    def save_to_store(self, writer: Optional[Union[BufferedWriter, BytesIO, str]] = None) -> int:
        """Saving to persistent store the NPY data of this result handle

        :param writer: An optional writer to override the store defined in \
                        :class:`QuantumMachinesManager<qm.QuantumMachinesManager.QuantumMachinesManager>`
        :return: The number of items saved
        """
        own_writer = False
        if writer is None:
            own_writer = True
            writer = self._store.job_named_result(self._job_id, self._schema.name).for_writing()
        try:
            header = self._get_named_header()
            return self._save_to_file(header, writer)
        finally:
            if own_writer:
                writer.close()

    def wait_for_values(self, count: int = 1, timeout: Optional[float] = None):
        """Wait until we know at least `count` values were processed for this named result

        :param count: The number of items to wait for
        :param timeout: Timeout for waiting in seconds
        :return:
        """
        start = time.time()
        end = start + max(0.0, timeout) if timeout is not None else None
        while end is None or time.time() < end:
            if self.count_so_far() >= count:
                return
            time.sleep(0.2)

    def wait_for_all_values(self, timeout: Optional[float] = None) -> bool:
        """Wait until we know all values were processed for this named result

        :param timeout: Timeout for waiting in seconds
        :return: True if job finished successfully and False if job has closed before done
        """
        start = time.time()
        end = start + max(0.0, timeout) if timeout is not None else None
        while end is None or time.time() < end:
            header = self._get_named_header()
            if header.done or header.closed:
                return header.done
            time.sleep(0.2)
        raise TimeoutError(f"result {self.name} was not done in time")

    def is_processing(self) -> bool:
        return not (self._get_named_header().done or self._get_named_header().closed)

    def count_so_far(self) -> int:
        """
        also `len(handle)`

        :return: The number of values this result has so far
        """
        return self._get_named_header().count_so_far

    def __len__(self) -> int:
        return self.count_so_far()

    def has_dataloss(self) -> bool:
        """
        :return: if there was data loss during job execution
        """
        return self._get_named_header().has_dataloss

    def _write_header(self, writer: Union[BufferedWriter, BytesIO, str], count: int):
        d_type = self._schema.dtype
        _format.write_array_header_2_0(writer, {
            "descr": d_type,
            "fortran_order": False,
            "shape": (count,)
        })

    def _save_to_file(self, header: NamedJobResultHeader,
                      writer: Union[BufferedWriter, BytesIO, str]) -> int:
        count = 0
        request = GetJobNamedResultRequest()
        request.jobId = self._job_id
        request.outputName = self.name
        request.longOffset.value = 0
        request.limit = header.count_so_far

        owning_writer = False
        if type(writer) is str:
            writer = open(writer, "wb+")
            owning_writer = True

        try:
            self._write_header(writer, header.count_so_far)
            for result in self._service.GetJobNamedResult(request):
                count += result.countOfItems
                writer.write(result.data)

        finally:
            if owning_writer:
                writer.close()
        return count

    def _get_named_header(self) -> NamedJobResultHeader:
        request = GetJobNamedResultHeaderRequest()
        request.jobId = self._job_id
        request.outputName = self.name
        response = self._service.GetJobNamedResultHeader(request)
        dtype = _parse_dtype(response.simpleDType)
        return NamedJobResultHeader(
            count_so_far=response.countSoFar,
            is_single=response.isSingle,
            output_name=self.name,
            job_id=self.job_id,
            d_type=dtype,
            done=response.done,
            closed=response.closed,
            has_dataloss=response.hasDataloss
        )

    def fetch_all(self):
        return self.fetch(slice(0, len(self)))

    def fetch(self, item: Union[int, slice]) -> numpy.array:
        """
        Fetch the current value of the result from the server into local memory

        :return:
        """
        if type(item) is int:
            start = item
            stop = item + 1
            step = None
        elif type(item) is slice:
            start = item.start
            stop = item.stop
            step = item.step
        else:
            raise Exception("fetch supports only int or slice")

        if step != 1 and step is not None:
            raise Exception("fetch supports step=1 or None in slices")

        header = self._get_named_header()
        if stop is None:
            stop = header.count_so_far
        if start is None:
            start = 0

        d_type = self._schema.dtype

        writer = BytesIO()
        count = 0
        request = GetJobNamedResultRequest()
        request.jobId = self._job_id
        request.outputName = self._schema.name
        request.longOffset.value = start
        request.limit = stop - start

        data_writer = BytesIO()
        for result in self._service.GetJobNamedResult(request):
            count += result.countOfItems
            data_writer.write(result.data)

        _format.write_array_header_2_0(writer, {
            "descr": d_type,
            "fortran_order": False,
            "shape": (count,)
        })

        data_writer.seek(0)
        for d in data_writer:
            writer.write(d)

        writer.seek(0)

        if header.has_dataloss:
            logger.warning(f"Results variable {self.name} has data loss")

        return numpy.load(writer)


class MultipleNamedJobResult(BaseNamedJobResult):
    """
    A handle to a result of a pipeline terminating with ``save_all``
    """
    def __init__(self, job_id: str, schema: JobResultItemSchema, service: JobResultsServiceStub,
                 store: BaseStore
                 ) -> None:
        if schema.is_single:
            raise Exception("expecting a multi-result schema")
        super().__init__(job_id, schema, service, store)

    def _wait_for_any_value(self):
        self.wait_for_values(count=1, timeout=0.5)

    def fetcher(self):
        def fetcher():
            self._wait_for_any_value()
            request = GetJobNamedResultRequest()
            request.jobId = self._job_id
            request.outputName = self.name
            request.longOffset.value = 0
            request.limit = 0

            header_writer = BytesIO()
            self._write_header(header_writer, 1)
            header_value = header_writer.getvalue()

            named_result = self._service.GetJobNamedResult(request)
            for result in named_result:
                item_count = result.countOfItems
                total_bytes = len(result.data)
                bytes_per_item = total_bytes // item_count
                writer = BytesIO()
                for i in range(0, item_count):
                    item_bytes = result.data[i * bytes_per_item:(i + 1) * bytes_per_item]
                    writer.seek(0)
                    writer.write(header_value)
                    writer.write(item_bytes)
                    writer.seek(0)
                    ar = numpy.load(writer)
                    yield ar[0]

        return fetcher


class SingleNamedJobResult(BaseNamedJobResult):
    """
    A handle to a result of a pipeline terminating with ``save``
    """
    def __init__(self, job_id: str, schema: JobResultItemSchema, service: JobResultsServiceStub,
                 store: BaseStore) -> None:
        if not schema.is_single:
            raise Exception("expecting a single-result schema")
        super().__init__(job_id, schema, service, store)

    def wait_for_values(self, count: int = 1, timeout: Optional[float] = None):
        if count != 1:
            raise RuntimeError("single result can wait only for a single value")
        return super().wait_for_values(1, timeout)

    def fetch_all(self):
        return self.fetch(0)

    def fetch(self, item: Union[int, slice]):
        """
        Fetch the current value of the result from the server into local memory

        Because this is a result from a save terminal, the `item` parameter is ignored

        :return: The single stream item saved
        """
        if (isinstance(item, int) and item != 0) or isinstance(item, slice):
            logger.warning("Fetching single result will always return the single value")
        value = super().fetch(0)
        if len(value) == 0:
            return None
        elif len(value[0]) == 1:
            return value[0][0]
        else:
            return value[0]


class JobResults:
    """
    Access to the results of a QmJob

    This object is created by calling :attr:`QmJob.result_handles<qm.QmJob.QmJob.result_handles>`

    Assuming you have an instance of JobResults::

        job_results:JobResults

    This object is iterable::

        for name, handle in job_results:
            print(name)

    Can detect if a name exists::

        if "somename" in job_results:
            print("somename exists!")
            handle = job_results.get("somename")

    """

    def __init__(self, job_id: str, service: JobResultsServiceStub, store: BaseStore) -> None:
        super().__init__()
        self._job_id = job_id
        self._service = service
        self._store = store
        schema = JobResults._load_schema(job_id, service)
        self._schema = schema
        self._all_results: Dict[str, BaseNamedJobResult] = {}
        for (name, item_schema) in schema.items.items():
            if item_schema.is_single:
                result = SingleNamedJobResult(job_id, item_schema, service, store)
            else:
                result = MultipleNamedJobResult(job_id, item_schema, service, store)
            self._all_results[name] = result
            if not hasattr(self, name):
                setattr(self, name, result)

    def __iter__(self) -> Generator[Tuple[str, BaseNamedJobResult], None, None]:
        for item in self._schema.items.values():
            yield item.name, self.get(item.name)

    def is_processing(self) -> bool:
        """Check if the job is still processing results

        :return: True if results are still being processed, False otherwise
        """
        key = list(self._all_results.keys())[0]
        return self._all_results[key].is_processing()

    def save_to_store(self, writer: Optional[Union[BufferedWriter, BytesIO, str]] = None):
        """Save all results to store (file system by default) in a single NPZ file

        :param writer: An optional writer to be used instead of the pre-populated \
            store passed to :class:`qm.QuantumMachinesManager.QuantumMachinesManager`
        """
        own_writer = False
        if writer is None:
            own_writer = True
            writer = self._store.all_job_results(self._job_id).for_writing()
        zipf = None
        try:
            zipf = zipfile.ZipFile(writer, allowZip64=True, mode="w", compression=zipfile.ZIP_DEFLATED)
            for (name, result) in self:
                with zipf.open(f"{name}.npy", "w") as entry:
                    result.save_to_store(entry)
                pass
        finally:
            zipf.close()
            if own_writer:
                writer.close()

    @staticmethod
    def _load_schema(job_id: str, service: JobResultsServiceStub) -> JobResultSchema:
        request = GetJobResultSchemaRequest()
        request.jobId = job_id
        response: GetJobResultSchemaResponse = service.GetJobResultSchema(request)
        return JobResultSchema({
            item.name:
                JobResultItemSchema(
                    item.name,
                    _parse_dtype(item.simpleDType),
                    item.isSingle,
                    item.expectedCount
                )
            for item in response.items
        })

    def get(self, name: str) -> Optional[Union[MultipleNamedJobResult, SingleNamedJobResult]]:
        """Get a handle to a named result from :func:`stream_processing<qm.qua._dsl.stream_processing>`

        :param name: The named result using in :func:`stream_processing<qm.qua._dsl.stream_processing>`
        :return: A handle object to the results :class:`MultipleNamedJobResult` or :class:`SingleNamedJobResult` \
                or None if the named results in unknown

        """
        return self._all_results[name] if name in self._all_results else None

    def __contains__(self, name: str):
        return name in self._all_results

    def wait_for_all_values(self, timeout: Optional[float] = None) -> bool:
        """Wait until we know all values were processed for all named results

        :param timeout: Timeout for waiting in seconds
        :return: True if all finished successfully, False if any result was closed before done
        """
        start = time.time()
        end: Optional[int] = start + max(0.0, timeout) if timeout is not None else None
        keys = list(self._all_results.keys())
        all_done = True
        while len(keys) > 0 and (end is None or time.time() < end):
            result = self._all_results[keys[0]]
            time_remaining = None
            if end is not None:
                time_remaining = max(0.0, end - time.time())
            all_done = all_done and result.wait_for_all_values(time_remaining)
            keys = keys[1:]
        return all_done
