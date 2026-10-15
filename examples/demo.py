"""Demonstration of ``runall`` with three simulated commands.

Run this script from the repository root so that the relative paths in the
configuration resolve correctly::

    uv run python examples/demo.py

Each registered function waits five seconds and then prints a line that
identifies the function and the input file. The results are appended to
``output/`` and the executed commands to ``err/``.
"""

# from runall.config import CONFIG
from runall.tui import RunAllApp, runthat

config = {
    "runthat": {},
    "input_dir": "instances/ht0_*.txt",
    "output_dir": "output",
    "output_preffix": "out_",
    "output_header": "execucao,arquivo",
    "err_dir": "err",
}

@runthat(config=config)
def exec1(filename: str) -> str:
    """Build the first simulated command.

    Args:
        filename: Path of the input file.

    Returns:
        A shell command that sleeps and then prints a line tagged ``[1]``.
    """
    return f'sleep 5;echo "[1] {filename}"'


@runthat(config=config)
def exec2(filename: str) -> str:
    """Build the second simulated command.

    Args:
        filename: Path of the input file.

    Returns:
        A shell command that sleeps and then prints a line tagged ``[2]``.
    """
    return f'sleep 5;echo "[2] {filename}"'


@runthat(config=config)
def exec3(filename: str) -> str:
    """Build the third simulated command.

    Args:
        filename: Path of the input file.

    Returns:
        A shell command that sleeps and then prints a line tagged ``[3]``.
    """
    return f'sleep 5;echo "[3] {filename}"'


def main() -> None:
    """Launch the terminal interface with the registered commands."""
    RunAllApp(config).run()


if __name__ == "__main__":
    main()
