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
        """Add a document to the search engine.

        Args:
            doc_id: A unique identifier for the document.
            text: The raw document text.

        """
        self._index.add_document(doc_id, text)

    def search(self, query_text: str) -> list[tuple[str, float]]:
        """Parse *query_text*, execute it, and return results ranked by TF-IDF.

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

        # Rank by the first term in the query for simplicity.
        primary_term = self._primary_term(query)
        return rank_results(primary_term, doc_ids, self._index)

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
    def _primary_term(query: SearchQuery) -> str:
        """Extract the leftmost term from a query tree for ranking.

        Args:
            query: A parsed ``SearchQuery`` tree.

        Returns:
            The leftmost term string.

        """
        if isinstance(query, TermQuery):
            return query.term
        # Must be AndQuery or OrQuery.
        return SearchEngine._primary_term(query.left)
