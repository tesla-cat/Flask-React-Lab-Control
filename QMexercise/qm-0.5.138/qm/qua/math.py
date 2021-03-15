import qm.program.expressions as _exp
from qm.qua._dsl import _Expression


def sin2pi(x):
    return _Expression(_exp.math_func("sin2pi", x._exp))


def cos2pi(x):
    return _Expression(_exp.math_func("cos2pi", x._exp))


def sin(x):
    return _Expression(_exp.math_func("sin", x._exp))


def cos(x):
    return _Expression(_exp.math_func("cos", x._exp))


def sum(x):
    return _Expression(_exp.math_func("sum", x._exp))


def max(x):
    return _Expression(_exp.math_func("max", x._exp))


def min(x):
    return _Expression(_exp.math_func("min", x._exp))


def argmax(x):
    return _Expression(_exp.math_func("argmax", x._exp))


def argmin(x):
    return _Expression(_exp.math_func("argmin", x._exp))