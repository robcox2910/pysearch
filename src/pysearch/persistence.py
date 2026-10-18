"""Save a search engine to disk and load it back.

Closing the library for the night? The librarian writes every book's text
into a notebook (a JSON file). Tomorrow she reads the notebook and files
every book again, so every search gives the same answers as before.

Saving uses :func:`pysearch.atomic.atomic_write_text`, so a crash halfway
through can never leave a half-written notebook.
"""

import json
from pathlib import Path
from typing import cast

from pysearch.atomic import atomic_write_text
from pysearch.engine import SearchEngine
from pysearch.errors import PersistenceError


def save_engine(engine: SearchEngine, path: str | Path) -> None:
    """Save *engine* to a JSON file at *path*.

    Args:
        engine: The engine to save.
        path: Where to write it (its folder must already exist).

    """
    atomic_write_text(Path(path), json.dumps(engine.to_dict(), indent=2))


def load_engine(path: str | Path) -> SearchEngine:
    """Load an engine saved by :func:`save_engine`.

    Args:
        path: The file to read.

    Returns:
        A new engine holding the saved documents.

    Raises:
        PersistenceError: If the file is missing, unreadable, not text, not
            valid JSON, or not a saved engine.

    """
    file_path = Path(path)
    try:
        raw = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:  # missing, unreadable, or not text at all
        msg = f"Failed to load search engine from {file_path}: {exc}"
        raise PersistenceError(msg) from exc
    # Not JSON (JSONDecodeError is a kind of ValueError), a number too long
    # for Python to read (ValueError), or lists nested too deep (RecursionError).
    try:
        data = json.loads(raw)
    except (ValueError, RecursionError) as exc:
        msg = f"Invalid JSON in {file_path}: {exc}"
        raise PersistenceError(msg) from exc
    if not isinstance(data, dict):
        msg = f"{file_path} is not a saved search engine"
        raise PersistenceError(msg)
    try:
        return SearchEngine.from_dict(cast("dict[str, object]", data))
    except (KeyError, TypeError, ValueError) as exc:
        msg = f"{file_path} is not a saved search engine: {exc}"
        raise PersistenceError(msg) from exc
