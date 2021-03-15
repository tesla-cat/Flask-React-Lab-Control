from typing import Optional

from qm.pb.inc_qua_pb2 import QuaProgram, QuaResultAnalysis
from qm.program.StatementsCollection import StatementsCollection
from qm.program._ResultAnalysis import _ResultAnalysis


class _Program:
    def __init__(self, config=None, program: Optional[QuaProgram] = None):
        super().__init__()
        self._program = program if program is not None else QuaProgram()
        self._program.script.SetInParent()
        self._program.resultAnalysis.SetInParent()
        self._program.script.body.SetInParent()
        self._qua_config = config
        self._result_analysis = _ResultAnalysis(self._program.resultAnalysis)

    def _declare_var(self, name, var_type, size, value):
        declaration = self._program.script.variables.add()
        declaration.name = name
        declaration.type = var_type
        declaration.size = size
        if value is None:
            pass
        elif type(value) is list:
            for i in value:
                added_value = declaration.value.add()
                added_value.CopyFrom(i)
        else:
            added_value = declaration.value.add()
            added_value.CopyFrom(value)

    def declare_int(self, name, size, value):
        self._declare_var(name, QuaProgram.INT, size, value)

    def declare_real(self, name, size, value):
        self._declare_var(name, QuaProgram.REAL, size, value)

    def declare_bool(self, name, size, value):
        self._declare_var(name, QuaProgram.BOOL, size, value)

    @property
    def body(self):
        return StatementsCollection(self._program.script.body)

    @property
    def result_analysis(self) -> _ResultAnalysis:
        return self._result_analysis

    def build(self, config):
        copy = QuaProgram()
        copy.CopyFrom(self._program)
        copy.config.CopyFrom(config)
        return copy
