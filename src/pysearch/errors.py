"""Search engine error types."""


class PySearchError(Exception):
    """Base exception for all PySearch errors."""


class QueryParseError(PySearchError):
    """Raise when a search query cannot be parsed."""


class DuplicateDocumentError(PySearchError):
    """Raise when a document id is added to the index a second time."""
