from pathlib import Path


# This file defines utility functions for file operations, such as ensuring that the parent directory of a given path exists before performing file operations. This is important to prevent errors when trying to write to a file in a directory that does not exist.
def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
