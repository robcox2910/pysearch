"""Parse search queries into a structured representation.

Understanding your question is the first step to answering it. The query
parser reads what you typed -- like ``cats AND dogs`` -- and turns it into a
tree that the search engine can execute step by step.
"""

from __future__ import annotations

from dataclasses import dataclass

from pysearch.errors import QueryParseError


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


SearchQuery = TermQuery | AndQuery | OrQuery


def parse_query(text: str) -> SearchQuery:
    """Parse a text query into a ``SearchQuery`` tree.

    Supported formats:
    - ``"word"`` -- a single term
    - ``"a AND b"`` -- both terms must match
    - ``"a OR b"`` -- either term must match

    Args:
        text: The raw query string.

    Returns:
        A ``SearchQuery`` representing the parsed query.

    Raises:
        QueryParseError: If the query is empty or malformed.
    """
    stripped = text.strip()
    if not stripped:
        msg = "Query must not be empty."
        raise QueryParseError(msg)

    tokens = stripped.split()

    if len(tokens) == 1:
        return TermQuery(term=tokens[0].lower())

    expected_token_count = 3
    if len(tokens) == expected_token_count:
        left, operator, right = tokens
        if operator.upper() == "AND":
            return AndQuery(
                left=TermQuery(term=left.lower()),
                right=TermQuery(term=right.lower()),
            )
        if operator.upper() == "OR":
            return OrQuery(
                left=TermQuery(term=left.lower()),
                right=TermQuery(term=right.lower()),
            )

    msg = f"Cannot parse query: {text!r}"
    raise QueryParseError(msg)
