"""Test the search engine -- the librarian herself."""

import pytest

from pysearch.engine import SearchEngine
from pysearch.errors import QueryParseError

ZERO = 0
ONE = 1
TWO = 2
THREE = 3


class TestAddDocuments:
    """Test adding documents to the search engine."""

    def test_document_count(self) -> None:
        """Verify document count increases after adding documents."""
        engine = SearchEngine()
        assert engine.document_count == ZERO
        engine.add("doc1", "hello world")
        assert engine.document_count == ONE

    def test_multiple_documents(self) -> None:
        """Verify document count is correct after adding several documents."""
        engine = SearchEngine()
        engine.add("doc1", "hello")
        engine.add("doc2", "world")
        engine.add("doc3", "foo bar")
        assert engine.document_count == THREE


class TestSearchSingleTerm:
    """Test single-term searches."""

    def test_find_document(self) -> None:
        """Verify a document can be found by a term it contains."""
        engine = SearchEngine()
        engine.add("doc1", "python programming language")
        results = engine.search("python")
        doc_ids = [doc_id for doc_id, _ in results]
        assert "doc1" in doc_ids

    def test_empty_results(self) -> None:
        """Verify searching for a missing term returns no results."""
        engine = SearchEngine()
        engine.add("doc1", "hello world")
        results = engine.search("missing")
        assert results == []

    def test_results_are_ranked(self) -> None:
        """Verify results are returned as (doc_id, score) tuples."""
        engine = SearchEngine()
        engine.add("doc1", "python python python")
        engine.add("doc2", "python java")
        engine.add("doc3", "java java")
        results = engine.search("python")
        assert len(results) == TWO
        assert all(isinstance(score, float) for _, score in results)

    def test_higher_frequency_ranks_first(self) -> None:
        """Verify documents with more term occurrences rank higher."""
        engine = SearchEngine()
        engine.add("doc1", "python")
        engine.add("doc2", "python python python")
        engine.add("doc3", "java")
        results = engine.search("python")
        assert results[0][0] == "doc2"


class TestBooleanQueries:
    """Test AND and OR queries through the engine."""

    def test_and_query(self) -> None:
        """Verify AND queries return only documents with both terms."""
        engine = SearchEngine()
        engine.add("doc1", "cat dog")
        engine.add("doc2", "cat bird")
        engine.add("doc3", "dog bird")
        results = engine.search("cat AND dog")
        doc_ids = [doc_id for doc_id, _ in results]
        assert "doc1" in doc_ids
        assert len(doc_ids) == ONE

    def test_or_query(self) -> None:
        """Verify OR queries return documents with either term."""
        engine = SearchEngine()
        engine.add("doc1", "cat")
        engine.add("doc2", "dog")
        engine.add("doc3", "bird")
        results = engine.search("cat OR dog")
        doc_ids = [doc_id for doc_id, _ in results]
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids
        assert "doc3" not in doc_ids

    def test_and_no_overlap(self) -> None:
        """Verify AND returns empty when no document has both terms."""
        engine = SearchEngine()
        engine.add("doc1", "cat")
        engine.add("doc2", "dog")
        results = engine.search("cat AND dog")
        assert results == []


class TestEngineErrors:
    """Test error handling in the search engine."""

    def test_empty_query_raises(self) -> None:
        """Verify an empty query raises QueryParseError."""
        engine = SearchEngine()
        with pytest.raises(QueryParseError):
            engine.search("")
