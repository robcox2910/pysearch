"""Compute TF-IDF relevance scores.

TF-IDF stands for Term Frequency - Inverse Document Frequency. It answers the
question: "How important is this word to this particular document?" A word
that appears many times in one document but rarely in others gets a high
score -- it is probably what that document is *about*.
"""

import math

from pysearch.index import InvertedIndex


def compute_tf(term: str, doc_id: str, index: InvertedIndex) -> float:
    """Tally how many times a word shows up in one document -- more mentions, more relevant.

    Args:
        term: The search term.
        doc_id: The document identifier.
        index: The inverted index to query.

    Returns:
        The raw count of *term* in *doc_id* as a float.

    """
    return float(index.get_term_frequency(term, doc_id))


def compute_idf(term: str, index: InvertedIndex) -> float:
    """Figure out how special a word is -- common words like "the" score near zero, rare words like "dinosaur" score high.

    Uses the formula ``log(N / df)`` where *N* is the total number of
    documents and *df* is the number of documents containing *term*. Note that a
    word appearing in *every* document (or the only document) scores exactly
    ``0.0`` -- a fun exercise is to smooth this to ``log(N / df) + 1`` so even a
    lone match keeps a small positive score.

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
    """Blend "how often" with "how special" into one relevance score for a word in a document.

    Args:
        term: The search term.
        doc_id: The document identifier.
        index: The inverted index to query.

    Returns:
        The product of TF and IDF.

    """
    return compute_tf(term, doc_id, index) * compute_idf(term, index)


def rank_results(
    terms: str | list[str],
    doc_ids: list[str],
    index: InvertedIndex,
) -> list[tuple[str, float]]:
    """Rank documents by their TF-IDF score across all *terms*, highest first.

    Think of it like a school report card: each subject (term) gives a grade
    (TF-IDF score), and we add them all up to get the final grade. A document
    that scores well on *every* search word floats to the top.

    Args:
        terms: A single search term or a list of terms.
        doc_ids: The candidate document IDs to rank.
        index: The inverted index to query.

    Returns:
        A list of ``(doc_id, score)`` tuples sorted by score descending.

    """
    term_list = [terms] if isinstance(terms, str) else terms
    scored = [
        (doc_id, sum(compute_tfidf(t, doc_id, index) for t in term_list)) for doc_id in doc_ids
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored
