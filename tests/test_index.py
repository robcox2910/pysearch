"""Test the inverted index -- the librarian's memory."""

from pysearch.index import InvertedIndex

ZERO = 0
ONE = 1
TWO = 2
THREE = 3


class TestAddDocument:
    """Test adding documents to the index."""

    def test_document_count_increases(self) -> None:
        """Verify document count goes up after adding a document."""
        idx = InvertedIndex()
        assert idx.document_count == ZERO
        idx.add_document("doc1", "hello world")
        assert idx.document_count == ONE

    def test_multiple_documents(self) -> None:
        """Verify document count is correct after adding multiple documents."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello")
        idx.add_document("doc2", "world")
        assert idx.document_count == TWO


class TestSearch:
    """Test single-term search."""

    def test_find_existing_term(self) -> None:
        """Verify a term that exists returns the correct document."""
        idx = InvertedIndex()
        idx.add_document("doc1", "the quick brown fox")
        result = idx.search("quick")
        assert "doc1" in result

    def test_missing_term_returns_empty(self) -> None:
        """Verify a term not in any document returns an empty list."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello world")
        result = idx.search("missing")
        assert result == []

    def test_term_in_multiple_docs(self) -> None:
        """Verify a term found in multiple documents returns all of them."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat sat")
        idx.add_document("doc2", "cat nap")
        result = idx.search("cat")
        assert len(result) == TWO

    def test_case_insensitive_search(self) -> None:
        """Verify search is case insensitive."""
        idx = InvertedIndex()
        idx.add_document("doc1", "Hello World")
        result = idx.search("HELLO")
        assert "doc1" in result

    def test_plural_document_matches_singular_query(self) -> None:
        """Verify a document with plural words is found by a singular search."""
        idx = InvertedIndex()
        idx.add_document("doc1", "the foxes ate the berries")
        assert "doc1" in idx.search("fox")
        assert "doc1" in idx.search("berry")


class TestBooleanSearch:
    """Test AND and OR search operations."""

    def test_search_and_intersection(self) -> None:
        """Verify AND returns only documents containing all terms."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat dog")
        idx.add_document("doc2", "cat bird")
        idx.add_document("doc3", "dog bird")
        result = idx.search_and(["cat", "dog"])
        assert "doc1" in result
        assert "doc2" not in result
        assert "doc3" not in result

    def test_search_or_union(self) -> None:
        """Verify OR returns documents containing any of the terms."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat")
        idx.add_document("doc2", "dog")
        idx.add_document("doc3", "bird")
        result = idx.search_or(["cat", "dog"])
        assert "doc1" in result
        assert "doc2" in result
        assert "doc3" not in result

    def test_search_and_empty_terms(self) -> None:
        """Verify AND with empty terms list returns empty."""
        idx = InvertedIndex()
        assert idx.search_and([]) == []

    def test_search_or_empty_terms(self) -> None:
        """Verify OR with empty terms list returns empty."""
        idx = InvertedIndex()
        assert idx.search_or([]) == []


class TestFrequency:
    """Test term and document frequency methods."""

    def test_term_frequency(self) -> None:
        """Verify term frequency counts occurrences in a document."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat cat cat dog")
        assert idx.get_term_frequency("cat", "doc1") == THREE
        assert idx.get_term_frequency("dog", "doc1") == ONE

    def test_term_frequency_missing(self) -> None:
        """Verify term frequency is zero for a missing term."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello")
        assert idx.get_term_frequency("missing", "doc1") == ZERO

    def test_document_frequency(self) -> None:
        """Verify document frequency counts documents containing the term."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat dog")
        idx.add_document("doc2", "cat bird")
        idx.add_document("doc3", "bird fish")
        assert idx.get_document_frequency("cat") == TWO

    def test_document_frequency_missing(self) -> None:
        """Verify document frequency is zero for a missing term."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello")
        assert idx.get_document_frequency("missing") == ZERO
