"""Default configuration for the ``runall`` package.

A configuration is a plain dictionary. The same structure may be defined by
the user and passed to :func:`runall.tui.runthat` and
:class:`runall.tui.RunAllApp`.
"""

CONFIG = {
    "runthat": {},
    "input_dir": "instances/ht0_*.txt",
    "output_dir": "output",
    "output_preffix": "out_",
    "output_header": "execucao,arquivo",
    "err_dir": "err",
}
"""Default configuration dictionary.

Keys:
    runthat: Registry that maps function names to the wrapped callables. It is
        populated by the :func:`runall.tui.runthat` decorator.
    input_dir: Glob pattern that selects the input files.
    output_dir: Directory that receives the standard output of each command.
    output_preffix: Prefix of every output file name. The key name keeps its
        historical spelling.
    output_header: Header line written once at the top of each new output file.
    err_dir: Directory that receives the executed commands and their standard
        error output.
"""
