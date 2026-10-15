# runall

`runall` is a Python package that runs shell commands over a set of input files
and displays the progress in a terminal user interface (TUI). Commands are
declared as ordinary Python functions registered with the `@runthat` decorator.
For every function, the interface shows a progress bar (the bar of the function
that is currently running is highlighted in orange) and a scrolling list of the
files that have been processed.

## Features

- Registers any number of command-building functions with a single decorator.
- Selects input files with a glob pattern.
- Displays one progress bar per function and a running list of processed files.
- Writes the standard output of every command to a CSV file per function.
- Logs each executed command and its standard error output to a separate file.

## Requirements

- Python 3.10 or later
- [Textual](https://textual.textualize.io/) 8.2.8 or later (installed automatically)
- [uv](https://docs.astral.sh/uv/) (recommended for development)

## Installation (by clonning)

Clone the repository and install the project with its dependencies:

```sh
uv sync
```

This creates a local virtual environment and installs `runall` in editable mode.

## Usage

1. Create a configuration dictionary (see [Configuration](#configuration)).
2. Decorate one or more functions with `@runthat(config=config)`. Each function
   receives the path of an input file and returns the shell command to execute.
3. Start the interface with `RunAllApp(config).run()`.

For every input file, `runall` executes each registered function in the order in
which it was defined. The commands run sequentially.

### Example

The complete example below is available in `examples/demo.py`. It registers three
functions that each wait five seconds and then print one line:

```python
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
    return f'sleep 5;echo "[1] {filename}"'


@runthat(config=config)
def exec2(filename: str) -> str:
    return f'sleep 5;echo "[2] {filename}"'


@runthat(config=config)
def exec3(filename: str) -> str:
    return f'sleep 5;echo "[3] {filename}"'


def main() -> None:
    RunAllApp(config).run()


if __name__ == "__main__":
    main()
```

Run it from the repository root, so that the relative paths in the configuration
resolve correctly:

```sh
uv run python examples/demo.py
```

## Configuration

The configuration is a plain dictionary with the following keys:

| Key              | Description                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------- |
| `runthat`        | Registry of decorated functions. Start it as an empty dictionary; `@runthat` fills it in.    |
| `input_dir`      | Glob pattern that selects the input files, for example `instances/ht0_*.txt`.                |
| `output_dir`     | Directory that receives the standard output of each function.                                |
| `output_preffix` | Prefix of every output file name. The key keeps its original spelling.                       |
| `output_header`  | Header line written once at the top of each newly created output file.                       |
| `err_dir`        | Directory that receives the executed commands and their standard error output.               |

A default configuration is also available as `runall.CONFIG`.

## Output files

For a function named `exec1` and the configuration above, `runall` writes:

- `output/out_exec1.csv`: the header line followed by the standard output of every
  execution of `exec1`.
- `err/out_exec1.csv`: for every execution, the line `$ <command>` followed by
  the standard error output of the command, if any.

Both files are opened in append mode, so results accumulate across runs. Remove
the output directories before a run to start from a clean state. Commands should
print lines that match the columns of `output_header`.

## Security considerations

Commands are executed through the shell (`shell=True`), and the file name is
inserted into the command string that your function returns. Quote file names
(for example with `shlex.quote`) if they may contain spaces or shell
metacharacters, and never register commands built from untrusted input.

The exit status of a command is not treated as an error: a failing command is
recorded in the error log and processing continues with the next command.

## Project layout

```text
src/runall/
├── __init__.py    Public API: CONFIG, discover_input_files, runthat
├── config.py      Default configuration
├── processor.py   Input file discovery
└── tui.py         The @runthat decorator and the RunAllApp interface
examples/
└── demo.py        Complete usage example
instances/         Sample input files used by the example
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
