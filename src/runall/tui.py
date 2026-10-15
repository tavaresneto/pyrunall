"""Command registration and terminal user interface for ``runall``.

This module provides the :func:`runthat` decorator, which registers functions
that build shell commands, and :class:`RunAllApp`, a Textual application that
runs every registered function over every input file while it displays
progress.
"""

import asyncio
import functools
import pathlib
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, ProgressBar

# from .config import CONFIG
from .processor import discover_input_files


def _output_path(config: dict, label: str) -> pathlib.Path:
    """Build the path of the output file for a registered function.

    Args:
        config: Configuration dictionary.
        label: Name of the registered function.

    Returns:
        The path ``<output_dir>/<output_preffix><label>.csv``.
    """
    return pathlib.Path(config["output_dir"]) / f"{config['output_preffix']}{label}.csv"


def _err_path(config: dict, label: str) -> pathlib.Path:
    """Build the path of the error log file for a registered function.

    Args:
        config: Configuration dictionary.
        label: Name of the registered function.

    Returns:
        The path ``<err_dir>/<output_preffix><label>.csv``.
    """
    return pathlib.Path(config["err_dir"]) / f"{config['output_preffix']}{label}.csv"


def _redirect_output(
    config: dict, label: str, proc: subprocess.CompletedProcess, cmd: str
) -> None:
    """Persist the result of a command to the output and error files.

    The standard output is appended to the output file. When that file does
    not exist yet, it is created with the configured header line first. The
    executed command and its standard error output are appended to the error
    file. Missing directories are created as needed.

    Args:
        config: Configuration dictionary.
        label: Name of the registered function that produced the command.
        proc: Completed process whose streams are persisted.
        cmd: Shell command that was executed.
    """
    out_path = _output_path(config, label)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not out_path.exists():
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"{config['output_header']}\n")
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(proc.stdout)

    err_path = _err_path(config, label)
    err_path.parent.mkdir(parents=True, exist_ok=True)
    with open(err_path, "a", encoding="utf-8") as f:
        f.write(f"$ {cmd}\n")
        if proc.stderr:
            f.write(proc.stderr)


def runthat(config: dict):
    """Create a decorator that registers a command-building function.

    The decorated function receives the path of an input file and must return
    a shell command as a string. The returned wrapper executes that command
    through the shell, writes its output through :func:`_redirect_output`, and
    returns the completed process. The wrapper is stored in
    ``config["runthat"]`` under the name of the decorated function.

    The command runs with ``shell=True``. Input file names are therefore
    interpolated into a shell command line, and the function must quote them
    when they may contain special characters. The exit status of the command
    is recorded in the returned process but is not treated as an error.

    Args:
        config: Configuration dictionary. It must contain a ``"runthat"``
            dictionary, which receives the registered wrapper.

    Returns:
        A decorator that registers a function and returns its wrapper.
    """

    def decorator(func):
        """Wrap and register a command-building function.

        Args:
            func: Function that maps an input file path to a shell command.

        Returns:
            The wrapper that executes the command for a given input file.
        """

        @functools.wraps(func)
        def wrapper(filename: str) -> subprocess.CompletedProcess:
            """Execute the command built for an input file.

            Args:
                filename: Path of the input file.

            Returns:
                The completed process with captured text output.
            """
            cmd = func(filename)
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            _redirect_output(config, func.__name__, proc, cmd)
            return proc

        config["runthat"][func.__name__] = wrapper
        return wrapper

    return decorator


CSS = """
#ls {
    height: 75%;
    width: 90%;
}

#ls .fn-row {
    height: 1;
    padding: 0;
    align: left middle;
}

#ls .fn-label {
    width: 12;
}

#ls ProgressBar {
    width: 1fr;
}

Bar > .bar--bar {
    color: $primary;
}

Bar.running > .bar--bar {
    color: #ffa500;
}

Bar.done > .bar--bar {
    color: $success;
}

#li {
    height: 15;
    max-height: 25%;
    margin: 0 1;
    border: round $primary;
    background: $surface;
}

#li Label {
    padding: 0 1;
}
"""
"""Textual stylesheet of the application.

The progress bar of the function that is currently running is drawn in orange.
"""


class RunAllApp(App):
    """Textual application that runs registered functions over input files.

    The interface shows one progress bar per registered function and a scrolling
    list of the input files in the order in which they are processed. For each
    input file, every registered function runs in registration order. The
    application exits when all files have been processed.

    Attributes:
        config: Configuration dictionary shared with the registered functions.
        files: Input files to process. It is assigned when the application is
            mounted.
    """

    TITLE = "RunAll"
    CSS = CSS

    def __init__(self, config: dict, **kwargs: object) -> None:
        """Initialize the application.

        Args:
            config: Configuration dictionary. Its ``"runthat"`` entry holds the
                registered functions and its ``"input_dir"`` entry selects the
                input files.
            **kwargs: Additional keyword arguments forwarded to
                :class:`textual.app.App`.
        """
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        """Build the widget tree.

        Yields:
            One labeled progress bar for each registered function, followed by
            a scrollable container that lists the processed files.
        """
        total = len(discover_input_files(self.config))
        with Vertical(id="ls"):
            for label in self.config["runthat"]:
                with Horizontal(id=f"fn-row-{label}", classes="fn-row"):
                    yield Label(label, classes="fn-label")
                    yield ProgressBar(
                        total=total,
                        show_percentage=True,
                        show_eta=False,
                        id=f"bar-{label}",
                    )
        with VerticalScroll(id="li"):
            yield Label("")

    def on_mount(self) -> None:
        """Start processing once the interface is mounted.

        The application exits with a message, without processing anything,
        when no function is registered or no input file matches the configured
        pattern.
        """
        if not self.config["runthat"]:
            self.exit(message="Nenhuma função registrada com @runthat.")
            return
        self.files = discover_input_files(self.config)
        if not self.files:
            self.exit(message=f"Nenhum arquivo encontrado: {self.config['input_dir']}")
            return
        self.run_worker(self.process_all())

    async def process_all(self) -> None:
        """Run every registered function over every input file.

        Files are processed sequentially. For each file, the registered
        functions run one after another in a worker thread so that the
        interface stays responsive. The progress bar of the running function is
        highlighted and advances when the function finishes. The application
        exits after the last file.
        """
        total = len(self.files)
        for index, filename in enumerate(self.files, start=1):
            await self._add_file_line(index, total, filename)
            for label in self.config["runthat"]:
                pb = self.query_one(f"#bar-{label}", ProgressBar)
                bar = pb.query_one("#bar")
                bar.set_class(True, "running")
                await asyncio.to_thread(self.config["runthat"][label], filename)
                bar.set_class(False, "running")
                pb.advance(1)
        self.exit(message="Processamento concluído.")

    async def _add_file_line(self, index: int, total: int, filename: str) -> None:
        """Append a line for the file being processed to the file list.

        Args:
            index: One-based position of the file.
            total: Total number of input files.
            filename: Path of the file.
        """
        line = Label(f"[{index}/{total}] {filename}")
        await self.query_one("#li", VerticalScroll).mount(line)
