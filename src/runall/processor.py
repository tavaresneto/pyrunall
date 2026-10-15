"""Discovery of the input files that ``runall`` processes."""

import glob

from .config import CONFIG


def discover_input_files(config: dict | None = None) -> list[str]:
    """Return the input files that match the configured glob pattern.

    Args:
        config: Configuration dictionary whose ``"input_dir"`` entry holds the
            glob pattern. When ``None``, the default
            :data:`runall.config.CONFIG` is used.

    Returns:
        The matching paths in lexicographic order. The list is empty when no
        file matches the pattern.
    """
    if config is None:
        config = CONFIG
    return sorted(glob.glob(config["input_dir"]))
