"""Test TF-IDF ranking -- the relevance score."""

from pysearch.index import InvertedIndex
from pysearch.tfidf import compute_idf, compute_tf, compute_tfidf, rank_results

ZERO = 0.0
ONE_OCCURRENCE = 1.0
THREE_OCCURRENCES = 3.0
TWO_RESULTS = 2


class TestComputeTf:
    """Test term frequency computation."""

    def test_tf_single_occurrence(self) -> None:
        """Verify TF is 1.0 for a term appearing once."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat dog")
        assert compute_tf("cat", "doc1", idx) == ONE_OCCURRENCE

    def test_tf_multiple_occurrences(self) -> None:
        """Verify TF increases with repeated terms."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat cat cat")
        assert compute_tf("cat", "doc1", idx) == THREE_OCCURRENCES

    def test_tf_missing_term(self) -> None:
        """Verify TF is zero for a term not in the document."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello")
        assert compute_tf("missing", "doc1", idx) == ZERO


class TestComputeIdf:
    """Test inverse document frequency computation."""

    def test_idf_rare_word_higher(self) -> None:
        """Verify IDF is higher for words in fewer documents."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat dog")
        idx.add_document("doc2", "cat bird")
        idx.add_document("doc3", "bird fish")
        idf_cat = compute_idf("cat", idx)
        idf_fish = compute_idf("fish", idx)
        assert idf_fish > idf_cat

    def test_idf_missing_term_zero(self) -> None:
        """Verify IDF is zero for a term not in any document."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello")
        assert compute_idf("missing", idx) == ZERO

    def test_idf_all_docs_term(self) -> None:
        """Verify IDF is zero when term appears in all documents."""
        idx = InvertedIndex()
        idx.add_document("doc1", "cat")
        idx.add_document("doc2", "cat")
        assert compute_idf("cat", idx) == ZERO


class TestComputeTfidf:
    """Test combined TF-IDF score computation."""

    def test_tfidf_ranks_correctly(self) -> None:
        """Verify document with more occurrences of a rare word scores higher."""
        idx = InvertedIndex()
        idx.add_document("doc1", "python python python java")
        idx.add_document("doc2", "python java")
        idx.add_document("doc3", "java java java")
        score1 = compute_tfidf("python", "doc1", idx)
        score2 = compute_tfidf("python", "doc2", idx)
        assert score1 > score2

    def test_tfidf_common_word_low_score(self) -> None:
        """Verify a word in all documents gets a low TF-IDF score."""
        idx = InvertedIndex()
        idx.add_document("doc1", "common word")
        idx.add_document("doc2", "common thing")
        score = compute_tfidf("common", "doc1", idx)
        assert score == ZERO


class TestRankResults:
    """Test result ranking by TF-IDF."""

    def test_rank_results_sorted(self) -> None:
        """Verify rank_results returns documents sorted by score descending."""
        idx = InvertedIndex()
        idx.add_document("doc1", "python python python java")
        idx.add_document("doc2", "python java")
        idx.add_document("doc3", "java java")
        ranked = rank_results("python", ["doc1", "doc2"], idx)
        assert len(ranked) == TWO_RESULTS
        assert ranked[0][0] == "doc1"
        assert ranked[0][1] >= ranked[1][1]

    def test_rank_results_returns_tuples(self) -> None:
        """Verify each result is a (doc_id, score) tuple."""
        idx = InvertedIndex()
        idx.add_document("doc1", "hello world")
        ranked = rank_results("hello", ["doc1"], idx)
        doc_id, score = ranked[0]
        assert isinstance(doc_id, str)
        assert isinstance(score, float)
