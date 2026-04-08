"""
Fuzzy logic bindings for Python implemented in Rust
"""

from fuzzers.plotting import _plot_surface, _plot_variable

from ._fuzzers import PyAntecedent, PyFuzzyEngine, PyRule, PyVariable

PyVariable.plot = _plot_variable
PyFuzzyEngine.plot_decision_surface = _plot_surface


__all__ = ["PyVariable", "PyAntecedent", "PyRule", "PyFuzzyEngine"]
