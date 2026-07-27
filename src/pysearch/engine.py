"""Tie every component together into a complete search engine.

The search engine is the librarian herself. She knows how to file new books
(add documents), understand your question (parse queries), look things up
(search the index), and tell you which results matter most (rank by TF-IDF).
"""

from pysearch.index import InvertedIndex
from pysearch.query import AndQuery, SearchQuery, TermQuery, parse_query
from pysearch.tfidf import rank_results


class SearchEngine:
    """A full-text search engine with TF-IDF ranking and boolean queries."""

    def __init__(self) -> None:
        """Initialise an empty search engine."""
        self._index = InvertedIndex()

    def add(self, doc_id: str, text: str) -> None:
        """Hand the librarian a new book to file away.

        Args:
            doc_id: A unique identifier for the document.
            text: The raw document text.

        """
        self._index.add_document(doc_id, text)

    def search(self, query_text: str) -> list[tuple[str, float]]:
        """Ask the librarian a question and get back the best-matching books, best first.

        Args:
            query_text: A query string such as ``"cats"``, ``"cats AND dogs"``,
                or ``"cats OR dogs"``.

        Returns:
            A list of ``(doc_id, score)`` tuples sorted by relevance.

        """
        query = parse_query(query_text)
        doc_ids = self._execute(query)

        if not doc_ids:
            return []

        # Rank by ALL terms in the query so every word counts.
        all_terms = self._collect_terms(query)
        return rank_results(all_terms, doc_ids, self._index)

    @property
    def document_count(self) -> int:
        """Return the total number of indexed documents."""
        return self._index.document_count

    def _execute(self, query: SearchQuery) -> list[str]:
        """Recursively execute a parsed query against the index.

        Args:
            query: A parsed ``SearchQuery`` tree.

        Returns:
            A list of matching document IDs.

        """
        if isinstance(query, TermQuery):
            return self._index.search(query.term)
        if isinstance(query, AndQuery):
            left = set(self._execute(query.left))
            right = set(self._execute(query.right))
            return list(left & right)
        # Must be OrQuery (type narrowing guarantees this).
        left = set(self._execute(query.left))
        right = set(self._execute(query.right))
        return list(left | right)

    @staticmethod
    def _collect_terms(query: SearchQuery) -> list[str]:
        """Collect every term from a query tree for ranking.

        Walk the whole tree and gather every leaf -- like picking every
        apple off a tree instead of just the first one you see.

        Args:
            query: A parsed ``SearchQuery`` tree.

        Returns:
            A list of all term strings in the query.

        """
        if isinstance(query, TermQuery):
            return [query.term]
        # Must be AndQuery or OrQuery -- collect from both branches.
        return SearchEngine._collect_terms(query.left) + SearchEngine._collect_terms(query.right)
