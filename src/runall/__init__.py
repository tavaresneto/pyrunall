"""Run shell commands over a set of input files with a terminal progress display.

The ``runall`` package lets a user register Python functions with the
:func:`runthat` decorator. Each registered function receives the path of an
input file and returns a shell command. The command is executed for every
input file that matches a glob pattern, while a Textual-based terminal user
interface (:class:`runall.tui.RunAllApp`) displays one progress bar per
registered function and a running list of the processed files.

Public names:
    CONFIG: A default configuration dictionary.
    discover_input_files: Resolves the input files described by a configuration.
    runthat: Decorator that registers a function in a configuration.
"""

from .config import CONFIG
from .processor import discover_input_files
from .tui import runthat

__all__ = ["CONFIG", "discover_input_files", "runthat"]
