"""Build and query an inverted index.

An inverted index is like the librarian's memory. Instead of reading every
book to find a word, the librarian keeps a notebook: for each word, she writes
down which books contain it and how many times it appears. When you ask her
about a word, she just flips to that page in her notebook -- instant answer!
"""

from collections import defaultdict

from pysearch.tokenizer import tokenize


class InvertedIndex:
    """Map terms to the documents that contain them.

    The index stores two things for every (term, document) pair:
    - which documents contain the term (for searching)
    - how many times the term appears in each document (for ranking)
    """

    def __init__(self) -> None:
        """Initialise an empty inverted index."""
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._doc_count = 0

    def add_document(self, doc_id: str, text: str) -> None:
        """Tokenize *text* and add every token to the index under *doc_id*.

        Args:
            doc_id: A unique identifier for the document.
            text: The raw document text.
        """
        self._doc_count += 1
        tokens = tokenize(text)
        for token in tokens:
            self._index[token][doc_id] += 1

    def search(self, term: str) -> list[str]:
        """Return document IDs that contain *term*.

        Args:
            term: A single search term (will be stemmed).

        Returns:
            A list of matching document IDs.
        """
        from pysearch.tokenizer import simple_stem

        stemmed = simple_stem(term.lower())
        return list(self._index.get(stemmed, {}))

    def search_and(self, terms: list[str]) -> list[str]:
        """Return document IDs that contain **all** of the given terms.

        Args:
            terms: A list of search terms.

        Returns:
            Document IDs present in every term's posting list (intersection).
        """
        if not terms:
            return []
        sets = [set(self.search(t)) for t in terms]
        result = sets[0]
        for s in sets[1:]:
            result &= s
        return list(result)

    def search_or(self, terms: list[str]) -> list[str]:
        """Return document IDs that contain **any** of the given terms.

        Args:
            terms: A list of search terms.

        Returns:
            Document IDs present in at least one term's posting list (union).
        """
        if not terms:
            return []
        result: set[str] = set()
        for t in terms:
            result |= set(self.search(t))
        return list(result)

    @property
    def document_count(self) -> int:
        """Return the total number of indexed documents."""
        return self._doc_count

    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Return how many times *term* appears in *doc_id*.

        Args:
            term: The search term (will be stemmed).
            doc_id: The document identifier.

        Returns:
            The number of occurrences, or 0 if not found.
        """
        from pysearch.tokenizer import simple_stem

        stemmed = simple_stem(term.lower())
        return self._index.get(stemmed, {}).get(doc_id, 0)

    def get_document_frequency(self, term: str) -> int:
        """Return how many documents contain *term*.

        Args:
            term: The search term (will be stemmed).

        Returns:
            The number of documents containing the term.
        """
        from pysearch.tokenizer import simple_stem

        stemmed = simple_stem(term.lower())
        return len(self._index.get(stemmed, {}))
