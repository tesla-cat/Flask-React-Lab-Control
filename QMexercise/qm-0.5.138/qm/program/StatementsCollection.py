from qm.pb.inc_qua_pb2 import QuaProgram

from qm._loc import _get_loc


class StatementsCollection(object):
    def __init__(self, body):
        super(StatementsCollection, self).__init__()
        self._body = body

    def play(self, pulse, element, duration=None, condition=None, target=""):
        """
        Play a pulse to a quantum element as per the OPX config
        :param pulse: A tuple (pulse, amp). pulse is string of pulse name, amp is a 4 matrix
        :param element:
        :param duration:
        :param condition:
        :param target:
        :return:
        """

        amp = None
        if type(pulse) is tuple:
            pulse, amp = pulse

        loc = _get_loc()
        statement = self._body.statements.add()
        statement.play.SetInParent()
        statement.play.loc = loc
        if isinstance(pulse, QuaProgram.RampPulse):
            statement.play.rampPulse.SetInParent()
            statement.play.rampPulse.CopyFrom(pulse)
        else:
            statement.play.namedPulse.SetInParent()
            statement.play.namedPulse.name = pulse
            statement.play.pulse.name = pulse
        statement.play.qe.name = element
        statement.play.targetInput = target
        if duration is not None:
            statement.play.duration.CopyFrom(duration)
        if condition is not None:
            statement.play.condition.CopyFrom(condition)
        if amp is not None:
            statement.play.amp.SetInParent()
            statement.play.amp.loc = loc
            statement.play.amp.v0.CopyFrom(amp[0])
            for i in range(1, 4, 1):
                if amp[i] is not None:
                    getattr(statement.play.amp, "v" + str(i)).CopyFrom(amp[i])

    def pause(self, *elements):
        """
        Pause the execution of the given quantum elements
        :param elements:
        :return:
        """
        statement = self._body.statements.add()
        statement.pause.SetInParent()
        statement.pause.loc = _get_loc()
        for i, element in enumerate(elements):
            element_ref = statement.pause.qe.add()
            element_ref.name = element

    def update_frequency(self, element, new_frequency):
        """
        Updates the frequency of a given Quantum Element
        :param element: The quantum element to set the frequency to
        :param new_frequency: The new frequency value to set
        :return:
        """
        statement = self._body.statements.add()
        statement.updateFrequency.SetInParent()
        statement.updateFrequency.loc = _get_loc()
        statement.updateFrequency.qe.name = element
        statement.updateFrequency.value.CopyFrom(new_frequency)

    def update_correction(self, element, c00, c01, c10, c11):
        """
        Updates the correction of a given Quantum Element
        :param element: The quantum element to set the correction to
        :param c00:
        :param c01:
        :param c10:
        :param c11:
        :return:
        """
        statement = self._body.statements.add()
        statement.updateCorrection.SetInParent()
        statement.updateCorrection.qe.name = element
        statement.updateCorrection.correction.SetInParent()
        statement.updateCorrection.correction.c0.CopyFrom(c00)
        statement.updateCorrection.correction.c1.CopyFrom(c01)
        statement.updateCorrection.correction.c2.CopyFrom(c10)
        statement.updateCorrection.correction.c3.CopyFrom(c11)

    def align(self, *elements):
        """
        Align the given quantum elements
        :param elements:
        :return:
        """
        statement = self._body.statements.add()
        statement.align.SetInParent()
        statement.align.loc = _get_loc()
        for i, element in enumerate(elements):
            element_ref = statement.align.qe.add()
            element_ref.name = element

    def reset_phase(self, element):
        """
        TODO: document
        :param element:
        :return:
        """
        statement = self._body.statements.add()
        statement.resetPhase.SetInParent()
        statement.resetPhase.qe.SetInParent()
        statement.resetPhase.qe.name = element

    def wait(self, duration, *elements):
        """
        Waits for the given duration on all provided quantum elements
        :param duration:
        :param elements:
        :return:
        """
        statement = self._body.statements.add()
        statement.wait.SetInParent()
        statement.wait.loc = _get_loc()
        statement.wait.time.CopyFrom(duration)
        for i, element in enumerate(elements):
            element_ref = statement.wait.qe.add()
            element_ref.name = element

    def wait_for_trigger(self, pulse_to_play, *elements):
        statement = self._body.statements.add()
        statement.waitForTrigger.SetInParent()
        statement.waitForTrigger.loc = _get_loc()
        if pulse_to_play is not None:
            statement.waitForTrigger.pulseToPlay.name = pulse_to_play
        for i, element in enumerate(elements):
            element_ref = statement.waitForTrigger.qe.add()
            element_ref.name = element

    def save(self, source, result):
        statement = self._body.statements.add()
        statement.save.SetInParent()
        statement.save.loc = _get_loc()
        statement.save.source.CopyFrom(source)
        statement.save.tag = result._get_var_name()

    def z_rotation(self, angle, *elements):
        statement = self._body.statements.add()
        statement.zRotation.SetInParent()
        statement.zRotation.loc = _get_loc()
        statement.zRotation.value.CopyFrom(angle)
        for i, element in enumerate(elements):
            element_ref = statement.zRotation.qe.add()
            element_ref.name = element

    def reset_frame(self, *elements):
        statement = self._body.statements.add()
        statement.resetFrame.SetInParent()
        statement.resetFrame.loc = _get_loc()
        for i, element in enumerate(elements):
            element_ref = statement.resetFrame.qe.add()
            element_ref.name = element

    def ramp_to_zero(self, element, duration):
        statement = self._body.statements.add()
        statement.rampToZero.SetInParent()
        statement.rampToZero.qe.SetInParent()
        statement.rampToZero.qe.name = element
        if duration is not None:
            statement.rampToZero.duration.SetInParent()
            statement.rampToZero.duration.value = duration

    def measure(self, pulse, element, stream=None, *processes):
        """
        Measure a quantum element using the given pulse, process the result with the integration weights and
        store the results to the provided variables
        :param pulse:
        :param element:
        :param stream:
        :type stream: _ResultSource
        :param processes: an iterable of analog processes
        :return:
        """
        amp = None
        if type(pulse) is tuple:
            pulse, amp = pulse

        loc = _get_loc()
        statement = self._body.statements.add()
        statement.measure.SetInParent()
        statement.measure.loc = loc
        statement.measure.pulse.name = pulse
        statement.measure.qe.name = element
        if stream is not None:
            statement.measure.streamAs = stream._get_var_name()

        for analog_process in processes:
            added_process = statement.measure.analogMeasureProcesses.add()
            added_process.CopyFrom(analog_process)

        if amp is not None:
            statement.measure.amp.SetInParent()
            statement.measure.amp.loc = loc
            statement.measure.amp.v0.CopyFrom(amp[0])
            for i in range(1, 4, 1):
                if amp[i] is not None:
                    getattr(statement.measure.amp, "v" + str(i)).CopyFrom(amp[i])

    def if_block(self, condition):
        statement = self._body.statements.add()
        ifstatement = getattr(statement, "if")
        ifstatement.SetInParent()
        ifstatement.loc = _get_loc()
        ifstatement.condition.CopyFrom(condition)
        ifstatement.body.SetInParent()
        return StatementsCollection(ifstatement.body)

    def for_each(self, iterators):
        statement = self._body.statements.add()
        forEach = getattr(statement, "forEach")
        forEach.SetInParent()
        forEach.loc = _get_loc()
        for it in iterators:
            pb_it = forEach.iterator.add()
            pb_it.variable.CopyFrom(it[0])
            pb_it.array.CopyFrom(it[1])
        forEach.body.SetInParent()
        return StatementsCollection(forEach.body)

    def get_last_statement(self):
        statements = self._body.statements
        l = len(statements)
        if l == 0:
            return None
        return statements[l - 1]

    def for_block(self):
        statement = self._body.statements.add()
        forstatement = getattr(statement, "for")
        forstatement.SetInParent()
        forstatement.loc = _get_loc()
        return forstatement

    def strict_timing_block(self):
        statement = self._body.statements.add()
        strict_timing_statement = getattr(statement, "strictTiming")
        strict_timing_statement.SetInParent()
        strict_timing_statement.loc = _get_loc()
        return strict_timing_statement

    def assign(self, target, expression):
        """
        Assign a value calculated by :expression into :target
        :param target: The name of the variable to assign to
        :param expression: The expression to calculate
        :return:
        """
        statement = self._body.statements.add()
        statement.assign.SetInParent()
        statement.assign.loc = _get_loc()
        statement.assign.target.CopyFrom(target)
        statement.assign.expression.CopyFrom(expression)
