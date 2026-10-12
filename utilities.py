"""Small filesystem utilities retained for compatibility with the original project."""
from __future__ import annotations

import os
from pathlib import Path


class CleanCache:
    """Remove regular files from a specified cache directory, if it exists.

    This utility is no longer called during word-cloud generation because cleaning
    the entire images directory can delete files belonging to another analysis.
    """
    def __init__(self, directory: str | os.PathLike | None = None):
        if directory is None:
            return
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return
        for child in path.iterdir():
            if child.is_file():
                try:
                    child.unlink()
                except OSError:
                    pass
