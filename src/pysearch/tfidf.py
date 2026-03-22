"""Compute TF-IDF relevance scores.

TF-IDF stands for Term Frequency - Inverse Document Frequency. It answers the
question: "How important is this word to this particular document?" A word
that appears many times in one document but rarely in others gets a high
score -- it is probably what that document is *about*.
"""

import math

from pysearch.index import InvertedIndex


def compute_tf(term: str, doc_id: str, index: InvertedIndex) -> float:
    """Compute the term frequency of *term* in *doc_id*.

    Args:
        term: The search term.
        doc_id: The document identifier.
        index: The inverted index to query.

    Returns:
        The raw count of *term* in *doc_id* as a float.
    """
    return float(index.get_term_frequency(term, doc_id))


def compute_idf(term: str, index: InvertedIndex) -> float:
    """Compute the inverse document frequency of *term*.

    Uses the formula ``log(N / df)`` where *N* is the total number of
    documents and *df* is the number of documents containing *term*.

    Args:
        term: The search term.
        index: The inverted index to query.

    Returns:
        The IDF value, or 0.0 if the term appears in no documents.
    """
    df = index.get_document_frequency(term)
    if df == 0:
        return 0.0
    return math.log(index.document_count / df)


def compute_tfidf(term: str, doc_id: str, index: InvertedIndex) -> float:
    """Compute the TF-IDF score for *term* in *doc_id*.

    Args:
        term: The search term.
        doc_id: The document identifier.
        index: The inverted index to query.

    Returns:
        The product of TF and IDF.
    """
    return compute_tf(term, doc_id, index) * compute_idf(term, index)


def rank_results(
    term: str,
    doc_ids: list[str],
    index: InvertedIndex,
) -> list[tuple[str, float]]:
    """Rank documents by their TF-IDF score for *term*, highest first.

    Args:
        term: The search term.
        doc_ids: The candidate document IDs to rank.
        index: The inverted index to query.

    Returns:
        A list of ``(doc_id, score)`` tuples sorted by score descending.
    """
    scored = [(doc_id, compute_tfidf(term, doc_id, index)) for doc_id in doc_ids]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored
