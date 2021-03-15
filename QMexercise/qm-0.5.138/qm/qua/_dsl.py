import inspect
import math as _math
from collections import Iterable
from typing import Optional as _Optional
from enum import Enum as _Enum
import qm.program.expressions as _exp
from qm import _Program
from qm.utils import fix_object_data_type as _fix_object_data_type
from qm.pb.inc_qua_pb2 import QuaProgram as _Q
from qm.program.StatementsCollection import StatementsCollection as _StatementsCollection
from qm.program._ResultAnalysis import _ResultAnalysis, _ResultSymbol
from qm.qua import AnalogMeasureProcess
from qm.qua._measure_process_dsl import demod
from qm._deprecated import deprecated as _deprecated

_block_stack = []


def program():
    """
    Create a QUA program.

    Used within a context manager, the program is defined in the code block
    below ``with`` statement.

    Statements in the code block below are played as soon as possible, meaning that an instruction
    will be played immediately unless it is dependent on a previous instruction.
    Additionally, commands output to the same quantum elements will be played sequentially,
    and to different quantum elements will be played in parallel.
    An exception is that pulses will be implicitly aligned at the end of each :func:`for_` loop iteration.

    The generated ``program_name`` object is used as an input to the execute function of a
    :class:`QuantumMachine<qm.QuantumMachine>` object.

    Example of creating a QUA program::

        with program() as program_name:
            play('pulse1', 'element1')
            wait('element1')

    Example of executing the program on a quantum machine::

        my_qm.execute(program_name)

    where ``my_qm`` is an instance of a :class:`QuantumMachine<qm.QuantumMachine>`
    """
    return _ProgramScope(_Program())


def play(pulse, element, duration=None, condition=None, **kwargs):
    """
    Play a `pulse` to an `element`.

    The pulse will be modified according to the properties of the element
    (see detailed explanation about pulse modifications below),
    and then played to the OPX output(s) defined to be connected
    to the input(s) of the element in the configuration.

    :param pulse: name of the pulse, as defined in the quantum machine configuration.
    :type pulse: str
    :param element: name of the quantum element, as defined in the quantum machine configuration.
    :type element: str
    :param duration: the time to play this pulse, compress or expand the pulse. If not provided, the default
                     pulse duration will be used. It is possible to dynamically change the duration of
                     constant pulses.
    :param condition: will play only if the condition's value is true

    .. note::
        It is possible to scale the pulse's amplitude dynamically by using the following syntax:

        ``play('pulse_name' * amp(v), 'element')``

        where ``v`` is QUA variable of type fixed. Range of v: -2 to 2 - 2\ :sup:`-16` in steps of 2\ :sup:`-16`.

        Moreover, if the pulse is intended to a mixedInputs element and thus is defined with two waveforms,
        the two waveforms, described as a column vector, can be multiplied by a matrix:

        ``play('pulse_name' * amp([v_00, v_01, v_10, v_11]), 'element'),``

        where ``v_ij``, i,j={0,1}, are QUA variables of type fixed.
        Note that ``v_ij`` should satisfy -2 <= ``v_ij`` <= 2 - 2\ :sup:`-16`.

    Example::

    >>> with program() as prog:
    >>>     v1 = declare(fixed)
    >>>     assign(v1, 0.3)
    >>>     play('pulse1', 'element1')
    >>>     play('pulse1' * amp(0.5), 'element1')
    >>>     play('pulse1' * amp(v1), 'element1')
    >>>     play('pulse1' * amp([0.9, v1, -v1, 0.9]), 'element_iq_pair')
    """
    body = _get_scope_as_blocks_body()
    if duration is not None:
        duration = _unwrap_exp(exp(duration))
    if condition is not None:
        condition = _unwrap_exp(exp(condition))
    target = ""
    if "target" in kwargs:
        target = kwargs["target"]
    body.play(pulse, element, duration=duration, condition=condition, target=target)


def pause():
    """
    Pause the execution of the job until :func:`qm.QmJob.QmJob.resume` is called.

    The quantum machines freezes on its current output state.
    """
    body = _get_scope_as_blocks_body()
    body.pause()


def update_frequency(element, new_frequency):
    """
    Dynamically update the frequency of the oscillator associated with a given `element`.

    This changes the frequency from the value defined in the quantum machine configuration.

    :param element: The quantum element associated with the oscillator whose frequency will be changed
    :type element: str
    :param new_frequency: The new frequency value to set in units of Hz. Range: (0 to 5000000) in steps of 1.
    :type new_frequency: int

    .. Note::

        Granularity of frequency updated using this statement is lower than the statically defined frequency in the
        quantum machine configuration.

    Example::

    >>> with program() as prog:
    >>>     update_frequency("q1", 4000000)

    """
    body = _get_scope_as_blocks_body()
    body.update_frequency(element, _unwrap_exp(exp(new_frequency)))


def update_correction(element, c00, c01, c10, c11):
    """
    Updates the correction matrix used to overcome IQ imbalances of the IQ mixer for the next pulses
    played on the element

    .. note:

        Make sure to update the correction after you called :func:`update_frequency`

    :param element: The quantum element associated with the oscillator whose correction matrix will change
    :param c00:
    :param c01:
    :param c10:
    :param c11:

    :type element: str
    :type c00: float | QUA variable of type real
    :type c01: float | QUA variable of type real
    :type c10: float | QUA variable of type real
    :type c11: float | QUA variable of type real

    Example::

    >>> with program() as prog:
    >>>     update_correction("q1", 1.0, 0.5, 0.5, 1.0)

    """
    body = _get_scope_as_blocks_body()
    body.update_correction(element, _unwrap_exp(exp(c00)), _unwrap_exp(exp(c01)), _unwrap_exp(exp(c10)),
                           _unwrap_exp(exp(c11)))


def measure(pulse, element, stream=None, *outputs):
    """
    Perform a measurement of `element` using `pulse`.

    An element for which a measurement is applied must have outputs defined in the configuration.

    A measurement consists of:

    1. playing a pulse to the element (identical to a :func:`play` statement)

    2. waiting for a duration of time defined as the ``time_of_flight``
       in the configuration of the element, and then sampling
       the returning pulse.
       The OPX input to be sampled is defined in the configuration of the element.

    3. demodulating and the acquired data from the indicated element's output
       at the ``intermediate_frequency`` defined in the configuration of the element,
       using integration weights defined in the configuration of the pulse,
       and storing the result in the provided variables.

    For a more detailed description of the measurement operation, see :ref:`Measure statement features`.

    :param pulse:
        name of the pulse, as defined in the quantum machine configuration.
        Pulse must have a ``measurement`` operation.

    :param element: name of the element, as defined in the quantum machine configuration. The element must have outputs.

    :param stream:
        the stream variable which the raw ADC data will be saved and will appear in result analysis scope.
        You can receive the results with :func:`QmJob.result_handles.get("name")`.
        A string name can also be used. In this case, the name of the result handle should be suffixed by ``_input1``
        for data from analog input 1 and ``_input2`` for data from analog input 2.

        If ``stream`` is set to ``None``, raw results will not be saved
        (note: must be explicitly set to ``None``).
        The raw results will be saved as long as the digital pulse that is played with pulse is high.

    :param outputs:

        A parameter specifying the source of the demodulation data, the target variable and the demodulation method.

        By calling either `demod` or `integration` with the member functions `full`, `sliced`, `accumulated` and
        `moving_window`. These functions are documented in the API for :class:`AccumulationMethod` below.



    Multiple output tuples may be defined, for determining the demodulation result with multiple integration weights.

    :type pulse: str
    :type element: str
    :type stream: str or stream object or None
    :type outputs: tuple or sequence of tuples

    Example::

    >>> with program() as prog:
    >>>     I = declare(fixed)
    >>>     Q = declare(fixed)
    >>>     I_stream = declare_stream()
    >>>
    >>>     # measure by playing 'meas_pulse1' to element 'rr1', do not save raw results.
    >>>     # demodulate using 'cos_weights' and store result in I, and also
    >>>     # demodulate using 'sin_weights' and store result in Q
    >>>     measure('meas_pulse1', 'rr1', None, ('cos_weights', I), ('sin_weights', Q))
    >>>
    >>>     # measure by playing 'meas_pulse2' to element 'rr1', save raw results to tag 'samples'.
    >>>     # demodulate data from 'out1' port of 'rr1' using 'optimized_weights' as integration weights
    >>>     # store result in I
    >>>     measure('meas_pulse2', 'rr1', 'samples', ('optimized_weights', 'out1', I))
    >>>
    >>>     # measure by playing 'meas_pulse2' to element 'rr1', save raw results to object 'I_Stream'. Get raw data of
    >>>     # analog input 1.
    >>>     measure('meas_pulse2', 'rr1', I_Stream)
    >>>     with stream_processing():
    >>>         I_stream.input1().save_all("raw_I_stream")
    >>>
    >>> from qm.QuantumMachinesManager import QuantumMachinesManager
    >>> qm = QuantumMachinesManager().open_qm({}) # note: config missing here
    >>> job = qm.execute(prog)
    >>> # ... we wait for the results to be ready...
    >>> # raw results can be retreived as follows (here job is a QmJob object:
    >>> raw_I_handle = job.result_handles.get("raw_I_stream")
    >>> # raw results can be retrieved as follows (here job is a QmJob object and qe was defined with analog 1):
    >>> samples_result_handle = job.result_handles.get("samples_input1")
    """
    body = _get_scope_as_blocks_body()

    analog_processes = []
    for i, output in enumerate(outputs):
        if issubclass(type(output), AnalogMeasureProcess.AnalogMeasureProcess):
            analog_processes.append(output)
        elif type(output) == tuple:
            if len(output) == 2:
                analog_processes.append(demod.full(output[0], output[1], ""))
            elif len(output) == 3:
                analog_processes.append(demod.full(output[0], output[2], output[1]))
            else:
                raise RuntimeError(
                    "Each output must be a tuple of (integration weight, output name, variable name), but output " + str(
                        i + 1) + " is invalid")

    if stream is not None and isinstance(stream, str):
        result_obj = _get_root_program_scope().declare_legacy_adc(stream)
    else:
        if stream is not None and (not isinstance(stream, _ResultSource)):
            raise RuntimeError("stream object is not of the right type")
        result_obj = stream
    body.measure(pulse, element, result_obj, *[_unwrap_analog_process(x) for x in analog_processes])


def align(*elements):
    """
    Align several quantum elements together.

    All of the quantum elements referenced in `\*elements` will wait for all the others to finish their currently
    running statement.

    :param \*elements: a single quantum element, or list of quantum elements
    :type \*elements: str | sequence of str
    """
    body = _get_scope_as_blocks_body()
    body.align(*elements)


def reset_phase(element):
    """
    Resets the phase of the oscillator associated with `element`

    :param element: a quantum element
    """
    body = _get_scope_as_blocks_body()
    body.reset_phase(element)


def ramp_to_zero(element, duration=None):
    """
    Starting from the last DC value, gradually lowers the DC to zero for `duration` \*4nsec

    If `duration` is None, the duration is taken from the element's config

    .. warning::
        This feature does not protect from voltage jumps. Those can still occur, i.e when the data sent to the
        analog output is outside the range -0.5 to 0.5 - 2\ :sup:`16` and thus will have an overflow.

    :param element: element for ramp to zero
    :param duration: time , `in multiples of 4nsec`. Range: [4, 2\ :sup:`24`] in steps of 1, or `None` to take value from config
    :type element: str
    :type duration: int | None
    """
    body = _get_scope_as_blocks_body()
    body.ramp_to_zero(element, duration)


def wait(duration, *elements):
    """
    Wait for the given duration on all provided elements.

    During the wait command the OPX will output 0.0 to the elements.

    :param duration: time to wait, `in multiples of 4nsec`. Range: [4, 2\ :sup:`24`] in steps of 1.
    :param \*elements: elements to wait on
    :type duration: int | QUA variable of type int
    :type \*elements: str | sequence of str

    .. warning::

        In case the value of this is outside the range above, unexpected results may occur.

    .. note::

        The purpose of the `wait` operation is to add latency. In simple cases, the latency added will be exactly
        the same as that specified by the QUA variable or literal used. However, in other cases an additional
        computational latency may be added. If the actual wait time has significance, such as in characterization
        experiments, the actual wait time should always be verified with a simulator.

    """
    body = _get_scope_as_blocks_body()
    body.wait(_unwrap_exp(exp(duration)), *elements)


def wait_for_trigger(element, pulse_to_play=None):
    """
    Wait for an external trigger on the provided element.

    During the command the OPX will play the pulse supplied by the :pulse_to_play parameter

    .. warning::
        The maximum allowed voltage value for the digital trigger is 1.8V. A voltage higher than this can damage the
        controller.

    :param pulse_to_play: the name of the pulse to play on the element while waiting for the external trigger. Must \
                          be a constant pulse. Can be None to play nothing while waiting.
    :type pulse_to_play: str
    :param element: element to wait on
    :type element: str

    """
    body = _get_scope_as_blocks_body()
    body.wait_for_trigger(pulse_to_play, element)


def save(var, stream_or_tag):
    """
    Stream a QUA variable, or a QUA array cell.
    the variable is streamed and not immediately saved (see :ref:`Stream Processing`).
    In case ``result_or_tag`` is a string, the data will be immediately saved to a result handle under the same name.

    If result variable is used, it can be used in results analysis scope see :func:`stream_processing`
    if string tag is used, it will let you receive result with :attr:`qm.QmJob.QmJob.result_handles`.
    The type of the variable determines the stream datatype, according to the following rule:

    - int -> int64
    - fixed -> float64
    - bool -> bool

    .. note::

        Saving arrays as arrays is not currently supported. Please use a QUA for loop to save an array.

    .. warning::

        A variable updated as a result of a measure statement will return with a signed 16.16 bit format,
        and must be manually right-shifted by 12 bits when loaded with ``QmJob.result_handles.get("tag").fetch_all()``.

    Example::

    >>>     # basic save
    >>>     a = declare(int, value=2)
    >>>     save(a, "a")
    >>>
    >>>     # fetching the results from python (job is a QmJob object):
    >>>     a_handle = job.result_handles.get("a")
    >>>     a_data = a_handle.fetch_all()
    >>>
    >>>     # save the third array cell
    >>>     vec = declare(fixed, value=[0.2, 0.3, 0.4, 0.5])
    >>>     save(vec[2], "ArrayCellSave")
    >>>
    >>>     # array iteration
    >>>     i = declare(int)
    >>>     array = declare(fixed, value=[x / 10 for x in range(1, 30)])
    >>>     with for_(i, 0, i < array.length(), i + 1):
    >>>         save(array[i], "array")

    :param var: A QUA variable or a QUA array cell to save
    :param stream_or_tag: A stream variable or string tag name to save the value under
    :type var: QUA variable or a QUA array cell
    :type stream_or_tag: str | stream variable
    """
    if stream_or_tag is not None and type(stream_or_tag) is str:
        result_obj = _get_root_program_scope().declare_legacy_save(stream_or_tag)
    else:
        result_obj = stream_or_tag

    if result_obj._is_adc_trace:
        raise Exception("adc_trace can't be used in save")

    body = _get_scope_as_blocks_body()
    body.save(_unwrap_save_source(var), result_obj)


@_deprecated("use frame_rotation instead", "0.3", "0.4")
def z_rot(angle, *elements):
    """
    Shift the phase of the oscillator associated with a quantum element by the given angle.

    This is typically used for virtual z-rotations. Equivalent to ``z_rotation()``

    :param angle: The angle to to add to the current phase (in radians)
    :param \*elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be shifted

    :type angle: float
    :type \*elements: str | sequence of str

    """
    return frame_rotation(angle, *elements)


@_deprecated("use frame_rotation instead", "0.3", "0.4")
def z_rotation(angle, *elements):
    """
    Shift the phase of the oscillator associated with a quantum element by the given angle.

    This is typically used for virtual z-rotations. Equivalent to ``z_rot()``

    :param angle: The angle to to add to the current phase (in radians)
    :param \*elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be shifted

    :type angle: float | QUA variable of type real
    :type \*elements: str | sequence of str

    """
    return frame_rotation(angle, *elements)


def frame_rotation(angle, *elements):
    """
    Shift the phase of the oscillator associated with a quantum element by the given angle.

    This is typically used for virtual z-rotations.

    .. note::
        The fixed point format of QUA variables of type fixed is 4.28, meaning the phase
        must be between -8 and 8 - 2\ :sup:`28`. Otherwise the phase value will be invalid.

    :param angle: The angle to to add to the current phase (in radians)
    :param \*elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be shifted

    :type angle: float | QUA variable of type fixed
    :type \*elements: str | sequence of str

    """
    body = _get_scope_as_blocks_body()
    body.z_rotation(_unwrap_exp(exp(angle)), *elements)


def reset_frame(*elements):
    """
    Shift the frame of the oscillator associated with a quantum element by the given angle.

    Used to reset all of the frame updated made up to this statement.

    :param \*elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be shifted

    :type \*elements: str | sequence of str
    """
    body = _get_scope_as_blocks_body()
    body.reset_frame(*elements)


def assign(var, _exp):
    """
    Set the value of a given QUA variable, or of a QUA array cell

    :param var:  A QUA variable or a QUA array cell for which to assign
    :param _exp: An expression for which to set the variable
    :type var: QUA variable
    :type _exp: QUA expression

    Example::

    >>> with program() as prog:
    >>>     v1 = declare(fixed)
    >>>     assign(v1, 1.3)
    >>>     play('pulse1' * amp(v1), 'element1')
    """
    body = _get_scope_as_blocks_body()
    _exp = exp(_exp)
    _var = exp(var)
    body.assign(_unwrap_assign_target(_var), _unwrap_exp(_exp))


def if_(expression):
    """
    If flow control statement in QUA.

    To be used with a context manager.

    The QUA code block following the statement will be
    executed only if expression evaluates to true.

    :param expression: A boolean expression to evaluate

    Example::

    >>> x=declare(int)
    >>> with if_(x>0):
    >>>     play('pulse', 'element')
    """
    if type(expression) == bool:
        expression = exp(expression)
    body = _get_scope_as_blocks_body()
    if_body = body.if_block(_unwrap_exp(expression))
    return _BodyScope(if_body)


def else_():
    """
    Else flow control statement in QUA.

    To be used with a context manager.

    Must appear after an ``if_()`` statement.

    The QUA code block following the statement will be executed only if expression in preceding ``if_()`` statement
    evaluates to false.

    Example::

    >>> x=declare(int)
    >>> with if_(x>0):
    >>>     play('pulse', 'element')
    >>> with else_():
    >>>     play('other_pulse', 'element')
    """
    body = _get_scope_as_blocks_body()
    last_statement = body.get_last_statement()
    if last_statement is None or \
            last_statement.HasField("if") is False:
        raise Exception("'else' statement must directly follow 'if' statement")
    ifstatement = getattr(last_statement, "if")
    if ifstatement.HasField("else") is True:
        raise Exception("only a single 'else' statement can follow an 'if' statement")
    elsestatement = getattr(ifstatement, "else")
    elsestatement.SetInParent()
    return _BodyScope(_StatementsCollection(elsestatement))


def _is_iter(x):
    try:
        iterator = iter(x)
    except TypeError:
        return False
    else:
        return True


def for_each_(var, values):
    """
    Flow control: Iterate over array elements in QUA.

    It is possible to either loop over one variable, or over a tuple of variables, similar to the `zip` style
    iteration in python.

    To be used with a context manager.

    :param var: The iteration variable
    :type var: QUA variable | tuple of QUA variables
    :param values: A list of values to iterate over or a QUA array.
    :type values: list of literals | list of tuples of literals | Qua array | tuple of Qua arrays

    Example::

    >>> x=declare(fixed)
    >>> y=declare(fixed)
    >>> with for_each_(x, [0.1, 0.4, 0.6]):
    >>>     play('pulse' * amp(x), 'element')
    >>> with for_each_((x, y), ([0.1, 0.4, 0.6], [0.3, -0.2, 0.1])):
    >>>     play('pulse1' * amp(x), 'element')
    >>>     play('pulse2' * amp(y), 'element')

    .. warning::

        This behaviour is changed and is no longer consistent with python `zip`.
        Instead of sending a list of tuple as values, you now need to send a tuple of lists
        The first list containning the values for the first variable, and so on. The prvious behavior expected the first
        value to be a tuple of first values for all variable, the second value is the second value tuple for all variables
        etc.
    """
    body = _get_scope_as_blocks_body()
    # normalize the var argument
    if not _is_iter(var) or type(var) is _Expression:
        var = (var,)

    for (i, v) in enumerate(var):
        if type(v) is not _Expression:
            raise Exception("for_each_ var " + i + " must be a variable")

    # normalize the values argument
    if isinstance(values, _Expression) or not _is_iter(values) or not _is_iter(values[0]):
        values = (values,)

    if _is_iter(values) and len(values) < 1:
        raise Exception("values cannot be empty")

    arrays = []
    for value in values:
        if isinstance(value, _Expression):
            arrays.append(value)
        elif _is_iter(value):
            if type(value[0]) == int:
                arrays.append(declare(int, value=value))
            elif type(value[0]) == bool:
                arrays.append(declare(bool, value=value))
            elif type(value[0]) == float:
                arrays.append(declare(fixed, value=value))
        else:
            raise Exception("value is not a Qua array neither iterable")

    var = [_unwrap_var(exp(v)) for v in var]
    arrays = [a.unwrap() for a in arrays]

    if len(var) != len(arrays):
        raise Exception("number of variables does not match number of array values")

    iterators = [(var[i], ar) for (i, ar) in enumerate(arrays)]

    foreach = body.for_each(iterators)
    return _BodyScope(foreach)


def while_(cond=None):
    """
        While loop flow control statement in QUA.

        To be used with a context manager.

        :param cond: an expression which evaluates to a boolean variable, determines if to continue to next loop iteration
        :type cond: QUA expression

        Example::

        >>> x = declare(fixed)
        >>> assign(x, 0)
        >>> with while_(x<=30):
        >>>     play('pulse', 'element')
        >>>     assign(x, x+1)
        """
    return for_(None, None, cond, None)


def for_(var=None, init=None, cond=None, update=None):
    """
    For loop flow control statement in QUA.

    To be used with a context manager.

    :param var: QUA variable used as iteration variable
    :type var: QUA variable
    :param init: an expression which sets the initial value of the iteration variable
    :type init: QUA expression
    :param cond: an expression which evaluates to a boolean variable, determines if to continue to next loop iteration
    :type cond: QUA expression
    :param update: an expression to add to ``var`` with each loop iteration
    :type update: QUA expression

    Example::

    >>> x = declare(fixed)
    >>> with for_(var=x, init=0, cond=x<=1, update=x+0.1):
    >>>     play('pulse', 'element')
    """
    if var is None and init is None and cond is None and update is None:
        body = _get_scope_as_blocks_body()
        for_statement = body.for_block()
        return _ForScope(for_statement)
    else:
        body = _get_scope_as_blocks_body()
        for_statement = body.for_block()
        if var is not None and init is not None:
            _StatementsCollection(for_statement.init).assign(_unwrap_assign_target(exp(var)), _unwrap_exp(exp(init)))
        if var is not None and update is not None:
            _StatementsCollection(for_statement.update).assign(_unwrap_assign_target(exp(var)),
                                                               _unwrap_exp(exp(update)))
        if cond is not None:
            for_statement.condition.CopyFrom(_unwrap_exp(exp(cond)))
        return _BodyScope(_StatementsCollection(for_statement.body))


def infinite_loop_():
    """
    Infinite loop flow control statement in QUA.

    To be used with a context manager.

    Optimized for zero latency between iterations,
    provided that no more than a single quantum element appears in the loop.

    .. note::
        In case multiple quantum elements need to be used in an infinite loop, it is possible to add several loops
        in parallel (see example).

    Example::

    >>> with infinite_loop_():
    >>>     play('pulse1', 'element1')
    >>> with infinite_loop_():
    >>>     play('pulse2', 'element2')
    """
    body = _get_scope_as_blocks_body()
    for_statement = body.for_block()
    for_statement.condition.CopyFrom(_unwrap_exp(exp(True)))
    return _BodyScope(_StatementsCollection(for_statement.body))


def for_init_():
    for_statement = _get_scope_as_for()
    return _BodyScope(_StatementsCollection(for_statement.init))


def for_update_():
    for_statement = _get_scope_as_for()
    return _BodyScope(_StatementsCollection(for_statement.update))


def for_body_():
    for_statement = _get_scope_as_for()
    return _BodyScope(_StatementsCollection(for_statement.body))


def for_cond(_exp):
    for_statement = _get_scope_as_for()
    for_statement.condition.CopyFrom(_unwrap_exp(exp(_exp)))


IO1 = object()
IO2 = object()


def L(value):
    """
    Creates an expression with a literal value

    :param value: int, float or bool to wrap in a literal expression
    """
    if type(value) is bool:
        return _exp.literal_bool(value)
    elif type(value) is int:
        return _exp.literal_int(value)
    elif type(value) is float:
        return _exp.literal_real(value)
    else:
        raise Exception("literal can be bool, int or float")


class fixed(object):
    pass


class DeclarationType(_Enum):
    EmptyScalar = 0
    InitScalar = 1
    EmptyArray = 2
    InitArray = 3


def declare(t, **kwargs):
    """
    Declare a single QUA variable or QUA vector to be used in subsequent expressions and assignments.

    Declaration is performed by declaring a python variable with the return value of this function.

    :param t:
        The type of QUA variable. Possible values: ``int``, ``fixed``, ``bool``, where:

        ``int``
            a signed 32-bit number
        ``fixed``
            a signed 4.28 fixed point number
        ``bool``
            either ``True`` or ``False``
    :key value: An initial value for the variable or a list of initial values for a vector
    :key size:
        If declaring a vector without explicitly specifying a value, this parameter is used to specify the length
        of the array

    :return: The variable or vector

    .. warning::

        some QUA statements accept a variable with a valid range smaller than the full size of the generic
        QUA variable. For example, ``wait()`` accepts numbers between 4 and 2\ :sup:`24`.
        In case the value stored in the variable is larger than the valid input range, unexpected results
        may occur.

    Example::

    >>> a = declare(fixed, value=0.3)
    >>> play('pulse' * amp(a), 'element')
    >>>
    >>> array1 = declare(int, value=[1, 2, 3])
    >>> array2 = declare(fixed, size=5)

    """
    size = kwargs.get("size", None)
    value = kwargs.get("value", None)
    if size is not None:
        if not (isinstance(size, int) and size > 0):
            raise ValueError("size must be a positive integer")
        if value is not None:
            raise ValueError("size declaration cannot be made if value is declared")
        dec_type = DeclarationType.EmptyArray
    else:
        if value is None:
            dec_type = DeclarationType.EmptyScalar
        elif isinstance(value, Iterable):
            dec_type = DeclarationType.InitArray
        else:
            dec_type = DeclarationType.InitScalar

    if dec_type == DeclarationType.InitArray:
        memsize = len(value)
        new_value = []
        for val in value:
            new_value.append(_to_expression(val).literal)
        value = new_value
    elif dec_type == DeclarationType.InitScalar:
        memsize = 1
        value = _to_expression(value).literal
    elif dec_type == DeclarationType.EmptyArray:
        memsize = size
    else:
        memsize = 1

    scope = _get_root_program_scope()

    if dec_type == DeclarationType.EmptyArray or dec_type == DeclarationType.InitArray:
        scope.array_index += 1
        var = "a" + str(scope.array_index)
        result = _Q.ArrayVarRefExpression()
        result.name = var
    else:
        scope.var_index += 1
        var = "v" + str(scope.var_index)
        result = _Q.AnyScalarExpression()
        result.variable.name = var

    prog = scope.program()
    if t == int:
        prog.declare_int(var, memsize, value)
    elif t == bool:
        prog.declare_bool(var, memsize, value)
    elif t == float:
        prog.declare_real(var, memsize, value)
    elif t == fixed:
        prog.declare_real(var, memsize, value)
    else:
        raise Exception("only int, float or bool variables are supported")

    return _Expression(result)


def declare_stream(**kwargs):
    """
        Declare a QUA output stream to be used in subsequent statements
        To retrieve the result - it must be saved in the stream processing block.

        Declaration is performed by declaring a python variable with the return value of this function.

        .. note::
            if the stream is an ADC trace, decalring it with the syntax ``declare_strean(adc_trace=True)``
            will add a buffer of length corresponding to the pulse length.

        :return: A :class:`_ResultSource` object to be used in :func:`stream_processing`

        Example::

        >>> a = declare_stream()
        >>> measure('pulse', 'element', a)
        >>>
        >>> with stream_processing():
        >>>     a.save("tag")
        >>>     a.save_all("another tag")
        """
    is_adc_trace = kwargs.get("adc_trace", False)

    scope = _get_root_program_scope()
    scope.result_index += 1
    var = "r" + str(scope.result_index)
    if is_adc_trace:
        var = "adc_trace_variable_buffered_" + var

    return _ResultSource(var, is_adc_trace, False, None)


def _to_expression(other, index_exp=None):
    other = _fix_object_data_type(other)
    if index_exp is not None and type(index_exp) is not _Q.AnyScalarExpression:
        index_exp = _to_expression(index_exp, None)

    if index_exp is not None and type(other) is not _Q.ArrayVarRefExpression:
        raise Exception(str(other) + " is not an array")

    if type(other) is _Expression:
        return other.unwrap()
    if type(other) is _Q.VarRefExpression:
        return other
    if type(other) is _Q.ArrayVarRefExpression:
        return _exp.array(other, index_exp)
    elif type(other) is int:
        return _exp.literal_int(other)
    elif type(other) is bool:
        return _exp.literal_bool(other)
    elif type(other) is float:
        return _exp.literal_real(other)
    elif other == IO1:
        return _exp.io1()
    elif other == IO2:
        return _exp.io2()
    else:
        raise Exception("Can't handle " + str(other))


class _Expression(object):
    def __init__(self, exp):
        self._exp = exp

    def __getitem__(self, item):
        return _Expression(_to_expression(self._exp, item))

    def unwrap(self):
        return self._exp

    def empty(self):
        return self._exp is None

    def length(self):
        unwrapped_element = self.unwrap()
        if type(unwrapped_element) is _Q.ArrayVarRefExpression:
            array_exp = _Q.ArrayLengthExpression()
            array_exp.array.CopyFrom(unwrapped_element)
            result = _Q.AnyScalarExpression()
            result.arrayLength.CopyFrom(array_exp)
            return _Expression(result)
        else:
            raise Exception(str(unwrapped_element) + " is not an array")

    def __add__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "+", other))

    def __radd__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "+", self._exp))

    def __sub__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "-", other))

    def __rsub__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "-", self._exp))

    def __neg__(self):
        other = _to_expression(0)
        return _Expression(_exp.binary(other, "-", self._exp))

    def __gt__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, ">", other))

    def __ge__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, ">=", other))

    def __lt__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "<", other))

    def __le__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "<=", other))

    def __eq__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "==", other))

    def __mul__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "*", other))

    def __rmul__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "*", self._exp))

    def __truediv__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "/", other))

    def __rtruediv__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "/", self._exp))

    def __lshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "<<", other))

    def __rlshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "<<", self._exp))

    def __rshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, ">>", other))

    def __rrshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, ">>", self._exp))

    def __and__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "&", other))

    def __rand__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "&", self._exp))

    def __or__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "|", other))

    def __ror__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "|", self._exp))

    def __xor__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "^", other))

    def __rxor__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "^", self._exp))

    def __invert__(self):
        other = _to_expression(True)
        return _Expression(_exp.binary(self._exp, "^", other))


class _PulseAmp(object):
    def __init__(self, v1, v2, v3, v4):
        super(_PulseAmp, self).__init__()
        if v1 is None:
            raise Exception("amp can be one value or a matrix of 4")
        if v2 is None and v3 is None and v4 is None:
            pass
        elif v2 is not None and v3 is not None and v4 is not None:
            pass
        else:
            raise Exception("amp can be one value or a matrix of 4")

        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def value(self):
        return self.v1, self.v2, self.v3, self.v4

    def __rmul__(self, other):
        if type(other) is not str:
            raise Exception("you can multiply only a pulse")
        return other, self.value()

    def __mul__(self, other):
        if type(other) is not str:
            raise Exception("you can multiply only a pulse")
        return other, self.value()


def amp(v1, v2=None, v3=None, v4=None):
    vars = [_unwrap_exp(exp(v)) if v is not None else None
            for v in [v1, v2, v3, v4]
            ]
    return _PulseAmp(*vars)


def ramp(v):
    result = _Q.RampPulse()
    value = _unwrap_exp(exp(v))
    if type(value) is not _Q.AnyScalarExpression:
        raise Exception("invalid expression: " + str(exp))
    else:
        result.value.CopyFrom(value)
    return result


def exp(value):
    return _Expression(_to_expression(value))


def _exp_or_none(value):
    if value is None:
        return None
    return exp(value)


class _BaseScope(object):
    def __init__(self):
        super(_BaseScope, self).__init__()

    def __enter__(self):
        global _block_stack
        _block_stack.append(self)
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _block_stack
        if _block_stack[-1] != self:
            raise Exception("Unexpected stack structure")
        _block_stack.remove(self)
        return False


class _BodyScope(_BaseScope):
    def __init__(self, body):
        super(_BodyScope, self).__init__()
        self._body = body

    def body(self):
        return self._body


class _ProgramScope(_BodyScope):
    def __init__(self, program: _Program):
        super().__init__(program.body)
        self._program = program
        self.var_index = 0
        self.array_index = 0
        self.result_index = 0
        self._declared_streams = {}

    def __enter__(self):
        super().__enter__()
        return self._program

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._program.result_analysis.generate_proto()
        return super().__exit__(exc_type, exc_val, exc_tb)

    def program(self):
        return self._program

    def declare_legacy_adc(self, tag: str) -> '_ResultSource':
        result_object = self._declared_streams.get(tag, None)
        if result_object is None:
            result_object = declare_stream()
            self._declared_streams[tag] = result_object

        ra = _get_scope_as_result_analysis()
        ra.auto_save_all(tag + "_input1", result_object.input1().with_timestamps())
        ra.auto_save_all(tag + "_input2", result_object.input2().with_timestamps())

        return result_object

    def declare_legacy_save(self, tag: str) -> '_ResultSource':
        result_object = self._declared_streams.get(tag, None)
        if result_object is None:
            result_object = declare_stream()
            self._declared_streams[tag] = result_object
        result_object.with_timestamps().save_all(tag)
        return result_object


class _ForScope(_BodyScope):
    def __init__(self, forst):
        super(_ForScope, self).__init__(None)
        self._forst = forst

    def body(self):
        raise Exception("for must be used with for_init, for_update, for_body and for_cond")

    def for_statement(self):
        return self._forst


class _RAScope(_BaseScope):
    def __init__(self, ra: _ResultAnalysis):
        super().__init__()
        self._ra = ra

    def __enter__(self):
        super().__enter__()
        return self._ra

    def result_analysis(self):
        return self._ra


def _get_root_program_scope() -> _ProgramScope:
    global _block_stack
    if type(_block_stack[0]) != _ProgramScope:
        raise Exception("Expecting program scope")
    return _block_stack[0]


def _get_scope_as_program() -> _Program:
    global _block_stack
    if type(_block_stack[-1]) != _ProgramScope:
        raise Exception("Expecting program scope")
    return _block_stack[-1].program()


def _get_scope_as_for() -> _ForScope:
    global _block_stack
    if type(_block_stack[-1]) != _ForScope:
        raise Exception("Expecting for scope")
    return _block_stack[-1].for_statement()


def _get_scope_as_blocks_body():
    global _block_stack
    if not issubclass(type(_block_stack[-1]), _BodyScope):
        raise Exception("Expecting scope with body.")
    return _block_stack[-1].body()


def _get_scope_as_result_analysis() -> _ResultAnalysis:
    global _block_stack
    return _get_root_program_scope().program().result_analysis


def _unwrap_exp(exp):
    if type(exp) is not _Expression:
        raise Exception("invalid expression: " + exp)
    return exp.unwrap()


def _unwrap_var(exp):
    var = _unwrap_exp(exp)
    if type(var) is not _Q.AnyScalarExpression:
        raise Exception("invalid expression: " + str(exp))
    return var.variable


def _unwrap_array_cell(exp):
    var = _unwrap_exp(exp)
    if type(var) is not _Q.AnyScalarExpression:
        raise Exception("invalid expression: " + str(exp))
    return var.arrayCell


def _unwrap_assign_target(exp):
    result = _Q.AssignmentStatement.Target()

    target = _unwrap_exp(exp)
    if type(target) is _Q.AnyScalarExpression:
        one_of = target.WhichOneof("expression_oneof")
        if one_of == "arrayCell":
            result.arrayCell.CopyFrom(target.arrayCell)
        elif one_of == "variable":
            result.variable.CopyFrom(target.variable)
        else:
            raise Exception("invalid target expression: " + str(exp))
    # We don't support whole array assignment for now
    # elif type(target) is _Q.ArrayVarRefExpression:
    #     result.arrayVar.CopyFrom(target.arrayVar)
    else:
        raise Exception("invalid target expression: " + str(exp))

    return result


def _unwrap_save_source(exp):
    result = _Q.SaveStatement.Source()

    source = _unwrap_exp(exp)
    if type(source) is not _Q.AnyScalarExpression:
        raise Exception("invalid source expression: " + str(exp))
    else:
        one_of = source.WhichOneof("expression_oneof")
        if one_of == "arrayCell":
            result.arrayCell.CopyFrom(source.arrayCell)
        elif one_of == "variable":
            result.variable.CopyFrom(source.variable)
        else:
            raise Exception("invalid source expression: " + str(exp))

    return result


def _unwrap_outer_target(analog_process_target):
    outer_target = _Q.AnalogProcessTarget()
    if type(analog_process_target) == AnalogMeasureProcess.ScalarProcessTarget:
        target = _Q.AnalogProcessTarget.ScalarProcessTarget()
        target_exp = _unwrap_exp(analog_process_target.target)
        if type(target_exp) is not _Q.AnyScalarExpression:
            raise Exception()
        target_type = target_exp.WhichOneof("expression_oneof")
        if target_type == "variable":
            target.variable.CopyFrom(target_exp.variable)
        elif target_type == "arrayCell":
            target.arrayCell.CopyFrom(target_exp.arrayCell)
        else:
            raise Exception()
        outer_target.scalarProcess.CopyFrom(target)
    elif type(analog_process_target) == AnalogMeasureProcess.VectorProcessTarget:
        target = _Q.AnalogProcessTarget.VectorProcessTarget()
        target.array.CopyFrom(_unwrap_exp(analog_process_target.target))
        target.timeDivision.CopyFrom(_unwrap_time_division(analog_process_target.time_division))
        outer_target.vectorProcess.CopyFrom(target)
    else:
        raise Exception()
    return outer_target


def _unwrap_analog_process(analog_process):
    result = _Q.AnalogMeasureProcess()
    result.loc = analog_process.loc
    result.elementOutput = analog_process.element_output

    if type(analog_process) == AnalogMeasureProcess.BareIntegration:
        result.bareIntegration.integration.name = analog_process.iw
        result.bareIntegration.target.CopyFrom(_unwrap_outer_target(analog_process.target))
    elif type(analog_process) == AnalogMeasureProcess.DemodIntegration:
        result.demodIntegration.integration.name = analog_process.iw
        result.demodIntegration.target.CopyFrom(_unwrap_outer_target(analog_process.target))
    elif type(analog_process) == AnalogMeasureProcess.RawTimeTagging:
        result.rawTimeTagging.target.CopyFrom(_unwrap_exp(analog_process.target))
        if analog_process.targetLen is not None:
            result.rawTimeTagging.targetLen.CopyFrom(_unwrap_exp(analog_process.targetLen).variable)
        result.rawTimeTagging.maxTime = int(analog_process.max_time)

    return result


def _unwrap_time_division(time_division):
    result = _Q.AnalogProcessTarget.TimeDivision()

    if type(time_division) == AnalogMeasureProcess.SlicedAnalogTimeDivision:
        result.sliced.samplesPerChunk = time_division.samples_per_chunk
    elif type(time_division) == AnalogMeasureProcess.AccumulatedAnalogTimeDivision:
        result.accumulated.samplesPerChunk = time_division.samples_per_chunk
    elif type(time_division) == AnalogMeasureProcess.MovingWindowAnalogTimeDivision:
        result.movingWindow.samplesPerChunk = time_division.samples_per_chunk
        result.movingWindow.chunksPerWindow = time_division.chunks_per_window

    return result


class AccumulationMethod:
    """
    A base class for specifying accumulation method in ``measure`` statement. Not to be instantiated.
    """

    def __init__(self):
        self.loc = ""
        self.return_func = None

    def __new__(cls):
        if cls is AccumulationMethod:
            raise TypeError("base class may not be instantiated")
        return object.__new__(cls)

    def full(self, iw, target, element_output=""):
        """
        Perform an ordinary demodulation/integration. See :ref:`Full demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target:
        :type target: QUA variable
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        analog_target = AnalogMeasureProcess.ScalarProcessTarget(self.loc, target)
        return self.return_func(self.loc, element_output, iw, analog_target)

    def sliced(self, iw, target, samples_per_chunk: int, element_output=""):
        """
        Perform a demouldation/integration in which the demodulation/integration process is split into chunks
        and the value of each chunk is saved in an array cell. See :ref:`Sliced demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target:
        :type target: QUA array
        :param samples_per_chunk:
            The number of ADC samples to be used for each chunk is this number times 4.
            Minimal value: 7
        :type samples_per_chunk: int
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        analog_time_division = AnalogMeasureProcess.SlicedAnalogTimeDivision(self.loc, samples_per_chunk)
        analog_target = AnalogMeasureProcess.VectorProcessTarget(self.loc, target, analog_time_division)
        return self.return_func(self.loc, element_output, iw, analog_target)

    def accumulated(self, iw, target, samples_per_chunk: int, element_output=""):
        """
        Same as ``sliced()``, however the accumulated result of the demodulation/integration
        is saved in each array cell. See :ref:`Accumulated demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target:
        :type target: QUA array
        :param samples_per_chunk:
            The number of ADC samples to be used for each chunk is this number times 4.
            Minimal value: 7
        :type samples_per_chunk: int
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        analog_time_division = AnalogMeasureProcess.AccumulatedAnalogTimeDivision(self.loc, samples_per_chunk)
        analog_target = AnalogMeasureProcess.VectorProcessTarget(self.loc, target, analog_time_division)
        return self.return_func(self.loc, element_output, iw, analog_target)

    def moving_window(self, iw, target, samples_per_chunk: int, chunks_per_window: int, element_output=""):
        """
        Same as ``sliced()``, however the several chunks are accumulated and saved to each array cell.
        See :ref:`Accumulated demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target:
        :type target: QUA array
        :param samples_per_chunk:
            The number of ADC samples to be used for each chunk is this number times 4.
            Minimal value: 7
        :type samples_per_chunk: int
        :param chunks_per_window: The number of chunks to use in the moving window
        :type chunks_per_window: int
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        analog_time_division = AnalogMeasureProcess.MovingWindowAnalogTimeDivision(self.loc,
                                                                                   samples_per_chunk,
                                                                                   chunks_per_window)
        analog_target = AnalogMeasureProcess.VectorProcessTarget(self.loc, target, analog_time_division)
        return self.return_func(self.loc, element_output, iw, analog_target)


class _Demod(AccumulationMethod):
    def __init__(self):
        super().__init__()
        self.loc = ""
        self.return_func = AnalogMeasureProcess.DemodIntegration


class _BareIntegration(AccumulationMethod):
    def __init__(self):
        super().__init__()
        self.loc = ""
        self.return_func = AnalogMeasureProcess.BareIntegration


class _TimeTagging:
    def __init__(self):
        self.loc = ""

    def raw(self, target, max_time, targetLen=None, element_output=""):
        return AnalogMeasureProcess.RawTimeTagging(self.loc, element_output, target, targetLen, max_time)


demod = _Demod()
integration = _BareIntegration()
time_tagging = _TimeTagging()


def stream_processing():
    """
        A context manager for the creation of :ref:`Stream Processing <stream processing>` pipelines.

        Each pipeline defines an analysis process that is applied to every stream item.
        A pipeline must be terminated with a save/save_all terminal, and then can be retrieved with
        :attr:`QmJob.result_handles<qm.QmJob.QmJob.result_handles>`.

        There are two save options: ``save_all`` will save every stream item, ``save`` will save only last item.

        A pipeline can be assigned to python variable, and then reused on other pipelines. It is ensured that the
        common part of the pipeline is processed only once.

        Example of creating a results analysis::

            with stream_processing():
                a.save("tag")
                a.save_all("another tag")

        Example of retrieving saved result::

            QmJob.result_handles.get("tag")

        """
    prog = _get_scope_as_program()
    return _RAScope(prog.result_analysis)


class _Functions(object):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def average():
        """
        Perform a running average on a stream item. The Output of this operation is the running average
        of the values in the stream starting from the beginning of the QUA program.
        :return: stream object
        """
        return ["average"]

    @staticmethod
    def dot_product(vector):
        """
        Computes dot product of the given vector and an item of the input stream
        :param vector: constant vector of numbers
        :return: stream object
        """
        return ["dot", ["@array"] + [str(item) for item in list(vector)]]

    @staticmethod
    def tuple_dot_product():
        """
        Computes dot product of the given item of the input stream - that should include two vectors
        :return: stream object
        """
        return ["dot"]

    @staticmethod
    def multiply_by(scalar_or_vector):
        """
        Multiply the input stream item by a constant scalar or vector.
        the input item can be either scalar or vector.
        :param scalar_or_vector: either a scalar number, or a vector of scalars.
        :return: stream object
        """
        if hasattr(scalar_or_vector, "__len__"):
            # vector
            return ["vmult", ["@array"] + [str(item) for item in list(scalar_or_vector)]]
        else:
            # scalar
            return ["smult", str(scalar_or_vector)]

    @staticmethod
    def tuple_multiply():
        """
        Computes multiplication of the given iten of the input stream - that can be any combination of scalar and vectors
        :return: stream object
        """
        return ["tmult"]

    @staticmethod
    def convolution(constant_vector, mode=None):
        """
        Computes discrete, linear convolution of one-dimensional constant vector and one-dimensional vector item of the input stream.
        :param constant_vector: vector of numbers
        :param mode: "full", "same" or "valid"
        :return: stream object
        """
        if mode is None:
            mode = ""
        return ["conv", str(mode), ["@array"] + [str(item) for item in list(constant_vector)]]

    @staticmethod
    def tuple_convolution(mode=None):
        """
        Computes discrete, linear convolution of two one-dimensional vectors that received as the one item from the input stream
        :param mode: "full", "same" or "valid"
        :return: stream object
        """
        if mode is None:
            mode = ""
        return ["conv", str(mode)]

    @staticmethod
    def fft():
        """
        Computes one-dimensional discrete fourier transform for every item in the stream.
        item can be a vector of numbers, in this case fft will assume all imaginary numbers are 0.
        item can also be a vector of number pairs - in this case for each pair- the first will be real and second imaginary
        :return: stream object
        """
        return ["fft"]

    @staticmethod
    def boolean_to_int():
        """
        converts boolean to integer number - 1 for true and 0 for false
        :return: stream object
        """
        return ["booleancast"]


FUNCTIONS = _Functions()


class _ResultStream:
    def __init__(self, input_stream, operator_array):
        super().__init__()
        self._input_stream = input_stream
        self._operator_array = operator_array

    def average(self) -> '_ResultStream':
        """
        Perform a running average on a stream item. The Output of this operation is the running average
        of the values in the stream starting from the beginning of the QUA program.
        """
        return _ResultStream(self, ["average"])

    def buffer(self, *args) -> '_ResultStream':
        """
        Gather items into vectors - creates an array of input stream items and outputs the array as one item.
        only outputs full buffers.

        :param length: number of items to gather
        :param skip: number of items to skip for each buffer. starts with the first item of each buffer.
        """
        int_args = [str(int(arg)) for arg in args]
        return _ResultStream(self, ["buffer"] + int_args)

    def buffer_and_skip(self, length, skip) -> '_ResultStream':
        """
        Gather items into vectors - creates an array of input stream items and outputs the array as one item.
        only outputs full buffers.

        :param length: number of items to gather
        :param skip: number of items to skip for each buffer. starts with the first item of each buffer.
        """
        return _ResultStream(self, ["bufferAndSkip", str(int(length)), str(int(skip))])

    def map(self, function) -> '_ResultStream':
        """
        transform the item by applying a function to it

        :param function: function to transform each item to a different item. predefined functions are defined
                        in "FUNCTIONS" object. for example, to compute fft on each item you should write "stream.map(FUNCTIONS.fft())"
        """
        return _ResultStream(self, ["map", function])

    def flatten(self) -> '_ResultStream':
        """
        deconstruct an array item - and send its elements one by one as items
        """
        return _ResultStream(self, ["flatten"])

    def skip(self, length) -> '_ResultStream':
        """
        suppress the first n items of the stream

        :param length: number of items to skip
        """
        return _ResultStream(self, ["skip", str(int(length))])

    def skip_last(self, length) -> '_ResultStream':
        """
        suppress the last n items of the stream

        :param length: number of items to skip
        """
        return _ResultStream(self, ["skipLast", str(int(length))])

    def take(self, length) -> '_ResultStream':
        """
        outputs only the first n items of the stream

        :param length: number of items to take
        """
        return _ResultStream(self, ["take", str(int(length))])

    def histogram(self, bins) -> '_ResultStream':
        """
        Compute the histogram of all items in stream

        :param bins: vector or pairs. each pair indicates the edge of each bin.
            example: [[1,10],[11,20]] - two bins, one between 1 and 10, second between 11 and 20
        """
        converted_bins = []
        for sub_list in list(bins):
            converted_bins = converted_bins + [["@array"] + [str(item) for item in list(sub_list)]]
        return _ResultStream(self, ["histogram", ["@array"] + converted_bins])

    def zip(self, other) -> '_ResultStream':
        """
        Combine the emissions of two streams to one item that is a tuple of items of input streams

        :param other: second stream to combine with self
        """
        return _ResultStream(self, ["zip", other._to_proto()])

    def save_all(self, tag):
        """
        Save all items received in stream.
        This will add to :class:`~qm._results.JobResults` a :class:`~qm._results.SingleNamedJobResult` object.

        :param tag: result name
        """
        ra = _get_scope_as_result_analysis()
        ra.save_all(tag, self)

    def save(self, tag):
        """
        Save only the last item received in stream
        This will add to :class:`~qm._results.JobResults` a :class:`~qm._results.MultipleNamedJobResult` object.

        :param tag: result name
        """
        ra = _get_scope_as_result_analysis()
        ra.save(tag, self)

    def dot_product(self, vector) -> '_ResultStream':
        """
        Computes dot product of the given vector and each item of the input stream

        :param vector: constant vector of numbers
        """
        return self.map(FUNCTIONS.dot_product(vector))

    def tuple_dot_product(self) -> '_ResultStream':
        """
        Computes dot product of the given item of the input stream - that should include two vectors
        """
        return self.map(FUNCTIONS.tuple_dot_product())

    def multiply_by(self, scalar_or_vector) -> '_ResultStream':
        """
        Multiply the input stream item by a constant scalar or vector .
        the input item can be either scalar or vector.

        :param scalar_or_vector: either a scalar number, or a vector of scalars.
        """
        return self.map(FUNCTIONS.multiply_by(scalar_or_vector))

    def tuple_multiply(self) -> '_ResultStream':
        """
        Computes multiplication of the given item of the input stream - that can be any combination of
        scalar and vectors
        """
        return self.map(FUNCTIONS.tuple_multiply())

    def convolution(self, constant_vector, mode=None) -> '_ResultStream':
        """
        Computes discrete, linear convolution of one-dimensional constant vector and one-dimensional vector
        item of the input stream.

        :param constant_vector: vector of numbers
        :param mode: "full", "same" or "valid"
        """
        return self.map(FUNCTIONS.convolution(constant_vector, mode))

    def tuple_convolution(self, mode=None) -> '_ResultStream':
        """
        Computes discrete, linear convolution of two one-dimensional vectors that received as the one item from the input stream

        :param mode: "full", "same" or "valid"
        """
        return self.map(FUNCTIONS.tuple_convolution(mode))

    def fft(self) -> '_ResultStream':
        """
        Computes one-dimensional discrete fourier transform for every item in the stream.
        item can be a vector of numbers, in this case fft will assume all imaginary numbers are 0.
        item can also be a vector of number pairs - in this case for each pair- the first will be real and second imaginary
        """
        return self.map(FUNCTIONS.fft())

    def boolean_to_int(self) -> '_ResultStream':
        """
        converts boolean to integer number - 1 for true and 0 for false
        """
        return self.map(FUNCTIONS.boolean_to_int())

    def _to_proto(self):
        return self._operator_array + [self._input_stream._to_proto()]

    def __add__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __sub__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __gt__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __ge__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __lt__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __le__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __eq__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __mul__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __div__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __lshift__(self, other):
        save(other, self)

    def __rshift__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __and__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __or__(self, other):
        raise Exception('Can\'t use this operator on results')

    def __xor__(self, other):
        raise Exception('Can\'t use this operator on results')


class _ResultSource(_ResultStream):
    """
    A python object representing a source of values that can be processing in a :func:`stream_processing()` pipeline

    This interface is chainable, which means that calling most methods on this object will create a new streaming

    See the base class :class:`_ResultStream` for operations
    """
    def __init__(self, name, is_adc_trace, timestamp, input: _Optional[int], only_timestamp: bool = False):
        super().__init__(None, None)
        self._var_name = name
        self._timestamp = timestamp
        self._only_timestamp = only_timestamp
        self._is_adc_trace = is_adc_trace
        self._input = input

    def _to_proto(self):
        result = [_ResultSymbol, self._var_name]
        inputs = ["@macro_input", str(self._input), result] if self._input else result
        timestamp = inputs if self._timestamp else ["withoutTimestamp", inputs]
        only_timestamp = timestamp if not self._only_timestamp else ["onlyTimestamp", timestamp]
        return ["@macro_adc_trace", only_timestamp] if self._is_adc_trace else only_timestamp

    def _get_var_name(self):
        return self._var_name

    def with_timestamps(self) -> _ResultStream:
        """Get a stream with the relevant timestamp for each stream-item"""
        return _ResultSource(self._var_name, self._is_adc_trace, True, self._input)

    def timestamps(self) -> _ResultStream:
        """Get a stream with only the timestamps of the stream-items"""
        return _ResultSource(self._var_name, self._is_adc_trace, True, self._input, True)

    def input1(self) -> '_ResultSource':
        """A stream of raw ADC data from input 1. Only relevant when saving data from measure statement."""
        return _ResultSource(self._var_name, self._is_adc_trace, self._timestamp, 1)

    def input2(self) -> '_ResultSource':
        """A stream of raw ADC data from input 2. Only relevant when saving data from measure statement."""
        return _ResultSource(self._var_name, self._is_adc_trace, self._timestamp, 2)


def bins(start, end, number_of_bins):
    bin_size = _math.ceil((end - start + 1) / float(number_of_bins))
    binsList = []
    while start < end:
        step_end = start + bin_size - 1
        if step_end >= end:
            step_end = end
        binsList = binsList + [[start, step_end]]
        start += bin_size
    return binsList
