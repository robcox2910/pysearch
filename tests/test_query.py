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

    def test_unknown_operator_is_just_another_word(self) -> None:
        """XOR isn't an operator, so it's searched for like any word (implicit AND)."""
        assert parse_query("cats XOR dogs") == AndQuery(
            left=AndQuery(left=TermQuery(term="cats"), right=TermQuery(term="xor")),
            right=TermQuery(term="dogs"),
        )

    def test_long_chains_are_read_left_to_right(self) -> None:
        """Regression: more than two terms used to be rejected."""
        assert parse_query("cats AND dogs OR fish") == OrQuery(
            left=AndQuery(left=TermQuery(term="cats"), right=TermQuery(term="dogs")),
            right=TermQuery(term="fish"),
        )


class TestQueryWords:
    """Query words are cleaned up exactly like document words."""

    def test_bare_words_mean_and(self) -> None:
        """Regression: "cats dogs" used to raise; now it means cats AND dogs."""
        assert parse_query("cats dogs") == AndQuery(
            left=TermQuery(term="cats"), right=TermQuery(term="dogs")
        )

    def test_punctuation_is_stripped(self) -> None:
        """Regression: "fox," used to be searched for with its comma."""
        assert parse_query("fox,") == TermQuery(term="fox")

    def test_hyphenated_word_becomes_its_pieces(self) -> None:
        """A word that splits into pieces needs all of them (stop words dropped)."""
        assert parse_query("state-of-the-art") == AndQuery(
            left=TermQuery(term="state"), right=TermQuery(term="art")
        )

    def test_stop_words_are_skipped(self) -> None:
        """Boring words like "the" are ignored, just as when indexing."""
        assert parse_query("the cats") == TermQuery(term="cats")

    @pytest.mark.parametrize("text", ["AND cats", "cats OR", "cats AND OR dogs"])
    def test_dangling_operators_raise(self, text: str) -> None:
        """An operator needs a word on both sides."""
        with pytest.raises(QueryParseError, match="operator"):
            parse_query(text)

    def test_only_stop_words_raises(self) -> None:
        """A query with nothing searchable left is reported clearly."""
        with pytest.raises(QueryParseError, match="searchable"):
            parse_query("the of a")
