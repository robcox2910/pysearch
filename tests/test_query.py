"""Test the query parser -- understanding your question."""

import pytest

from pysearch.errors import QueryParseError
from pysearch.query import AndQuery, OrQuery, TermQuery, parse_query


class TestTermQuery:
    """Test parsing single-term queries."""

    def test_single_word(self) -> None:
        """Verify a single word is parsed as a TermQuery."""
        result = parse_query("python")
        assert isinstance(result, TermQuery)
        assert result.term == "python"

    def test_case_insensitive(self) -> None:
        """Verify terms are lowercased during parsing."""
        result = parse_query("Python")
        assert isinstance(result, TermQuery)
        assert result.term == "python"

    def test_whitespace_trimmed(self) -> None:
        """Verify leading and trailing whitespace is stripped."""
        result = parse_query("  hello  ")
        assert isinstance(result, TermQuery)
        assert result.term == "hello"


class TestAndQuery:
    """Test parsing AND queries."""

    def test_and_query(self) -> None:
        """Verify 'a AND b' is parsed as an AndQuery."""
        result = parse_query("cats AND dogs")
        assert isinstance(result, AndQuery)
        assert isinstance(result.left, TermQuery)
        assert isinstance(result.right, TermQuery)
        assert result.left.term == "cats"
        assert result.right.term == "dogs"

    def test_and_case_insensitive_operator(self) -> None:
        """Verify AND operator is case insensitive."""
        result = parse_query("cats and dogs")
        assert isinstance(result, AndQuery)

    def test_and_mixed_case_operator(self) -> None:
        """Verify AND operator works with mixed case."""
        result = parse_query("cats And dogs")
        assert isinstance(result, AndQuery)


class TestOrQuery:
    """Test parsing OR queries."""

    def test_or_query(self) -> None:
        """Verify 'a OR b' is parsed as an OrQuery."""
        result = parse_query("cats OR dogs")
        assert isinstance(result, OrQuery)
        assert isinstance(result.left, TermQuery)
        assert isinstance(result.right, TermQuery)
        assert result.left.term == "cats"
        assert result.right.term == "dogs"

    def test_or_case_insensitive_operator(self) -> None:
        """Verify OR operator is case insensitive."""
        result = parse_query("cats or dogs")
        assert isinstance(result, OrQuery)


class TestQueryErrors:
    """Test error handling in query parsing."""

    def test_empty_query_raises(self) -> None:
        """Verify an empty query raises QueryParseError."""
        with pytest.raises(QueryParseError):
            parse_query("")

    def test_whitespace_only_raises(self) -> None:
        """Verify a whitespace-only query raises QueryParseError."""
        with pytest.raises(QueryParseError):
            parse_query("   ")

    def test_invalid_operator_raises(self) -> None:
        """Verify an unknown operator raises QueryParseError."""
        with pytest.raises(QueryParseError):
            parse_query("cats XOR dogs")

    def test_too_many_tokens_raises(self) -> None:
        """Verify more than three tokens raises QueryParseError."""
        with pytest.raises(QueryParseError):
            parse_query("cats AND dogs AND fish")
