"""Search engine error types."""


class PySearchError(Exception):
    """Base exception for all PySearch errors."""


class QueryParseError(PySearchError):
    """Raise when a search query cannot be parsed."""


class DuplicateDocumentError(PySearchError):
    """Raise when a document id is added to the index a second time."""


class PersistenceError(PySearchError):
    """Raise when a saved search engine can't be read back.

    Like opening the librarian's notebook and finding the pages torn or
    scribbled on -- the file is missing, isn't valid JSON, or isn't a saved
    engine at all.
    """
