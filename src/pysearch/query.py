"""Parse search queries into a structured representation.

Understanding your question is the first step to answering it. The query
parser reads what you typed -- like ``cats AND dogs`` or ``cats NOT dogs`` --
and turns it into a tree that the search engine can execute step by step.
"""

from dataclasses import dataclass

from pysearch.errors import QueryParseError
from pysearch.tokenizer import split_words


@dataclass
class TermQuery:
    """A query for a single search term."""

    term: str


@dataclass
class AndQuery:
    """A query requiring both the left and right sub-queries to match."""

    left: SearchQuery
    right: SearchQuery


@dataclass
class OrQuery:
    """A query requiring either the left or right sub-query to match."""

    left: SearchQuery
    right: SearchQuery


@dataclass
class NotQuery:
    """A query keeping the left side's matches that the right side does *not* match.

    Like sorting a pile of books: take everything on the left, then put back
    any book that mentions the word on the right.
    """

    left: SearchQuery
    right: SearchQuery


type SearchQuery = TermQuery | AndQuery | OrQuery | NotQuery


_OPERATORS = frozenset({"AND", "OR", "NOT"})


def parse_query(text: str) -> SearchQuery:
    """Read what you typed -- like "cats AND dogs" -- and turn it into a plan the engine can follow.

    Supported formats:

    - ``"word"`` -- a single term
    - ``"a AND b"`` / ``"a OR b"`` -- both / either must match
    - ``"a NOT b"`` (or ``"a AND NOT b"``) -- a must match and b must not
    - ``"a b"`` -- words next to each other must *all* match (an implied AND)
    - longer chains like ``"a AND b OR c"`` are read left to right:
      ``(a AND b) OR c``

    Each word is cleaned up exactly like document text (see
    :func:`~pysearch.tokenizer.split_words`): punctuation and stop words go,
    and a word that splits into pieces (``"state-of-the-art"``) needs all of
    its pieces.

    Args:
        text: The raw query string.

    Returns:
        A ``SearchQuery`` representing the parsed query.

    Raises:
        QueryParseError: If the query is empty, has nothing searchable, or
            has an operator without a word on both sides.

    """
    words = text.split()
    if not words:
        msg = "Query must not be empty."
        raise QueryParseError(msg)

    result: SearchQuery | None = None
    pending_operator = "AND"
    expecting_term = True
    for word in words:
        operator = word.upper()
        if operator in _OPERATORS:
            if operator == "NOT" and expecting_term and pending_operator == "AND" and result:
                pending_operator = "NOT"  # "a AND NOT b" reads the same as "a NOT b"
                continue
            if expecting_term:
                msg = f"The {operator} operator needs a word on both sides: {text!r}"
                raise QueryParseError(msg)
            pending_operator = operator
            expecting_term = True
            continue
        term = _word_query(word)
        if term is None:
            continue  # a stop word or bare punctuation -- nothing to search for
        result = term if result is None else _combine(result, pending_operator, term)
        pending_operator = "AND"
        expecting_term = False

    if expecting_term and result is not None:
        msg = f"The {pending_operator} operator needs a word on both sides: {text!r}"
        raise QueryParseError(msg)
    if result is None:
        msg = f"Query has no searchable words (only stop words?): {text!r}"
        raise QueryParseError(msg)
    return result


def _word_query(word: str) -> SearchQuery | None:
    """Turn one typed word into a query (several pieces must all match)."""
    pieces = [TermQuery(term=piece) for piece in split_words(word)]
    if not pieces:
        return None
    query: SearchQuery = pieces[0]
    for piece in pieces[1:]:
        query = AndQuery(left=query, right=piece)
    return query


def _combine(left: SearchQuery, operator: str, right: SearchQuery) -> SearchQuery:
    """Join two queries with AND, OR or NOT."""
    if operator == "OR":
        return OrQuery(left=left, right=right)
    if operator == "NOT":
        return NotQuery(left=left, right=right)
    return AndQuery(left=left, right=right)
