"""The brute-force librarian -- answers every question by reading every book, every time.

The real engine keeps an inverted index (a notebook of word -> books) so it
never has to reread anything. This librarian has no notebook. For each
question she opens every book, word by word, and counts. She's slow, but
she's so simple that she's obviously right, so the property tests and the
model check use her to check the real engine's answers.

She borrows only two things from PySearch: the list of stop words and the
stemmer that turns "cats" into "cat". Those decide what *counts* as the
same word. Everything else -- finding the books, AND, OR and NOT, the TF-IDF
scores and the order -- she works out on her own.
"""

import math

from pysearch.tokenizer import STOP_WORDS, simple_stem

# One book, as the strategies make it: its words, and the gap between each pair.
type Book = tuple[list[str], str]


def text_of(book: Book) -> str:
    """Return the book's text: its words with the gap between each pair."""
    words, gap = book
    return gap.join(words)


def root_of(word: str) -> str:
    """Return the root a word is filed under: "Cats" and "cat" both give "cat"."""
    return simple_stem(word.lower())


def roots_in(words: list[str]) -> list[str]:
    """Return the root of every word in a book, skipping stop words."""
    return [root_of(word) for word in words if word.lower() not in STOP_WORDS]


def brute_force_search(library: dict[str, Book], question: list[str]) -> list[tuple[str, float]]:
    """Answer ``question`` by reading every book in ``library`` (doc id -> book).

    The question is a list of pieces such as ``["cats", "OR", "dog", "fox"]``,
    read left to right: two words side by side must both match, so that one
    means ``(cats OR dog) AND fox``. ``NOT`` takes away every book with the
    next word. Each matching book scores the sum, over every word in the
    question except the ``NOT`` ones, of (times the word is in the book) x
    log(books in the library / books with the word). Best score first;
    equal scores go in order of doc id.
    """
    roots = {doc_id: roots_in(words) for doc_id, (words, _gap) in library.items()}

    def books_with(word: str) -> set[str]:
        """Return every book that has the word somewhere in it."""
        return {doc_id for doc_id, found in roots.items() if root_of(word) in found}

    def word_score(doc_id: str, word: str) -> float:
        """Score one question word in one book: times it's there x how rare it is."""
        books_having_it = len(books_with(word))
        if not books_having_it:
            return 0.0
        return roots[doc_id].count(root_of(word)) * math.log(len(library) / books_having_it)

    def score(doc_id: str, words: list[str]) -> float:
        """Add up the score of every question word in one book."""
        # Python's sum() adds floats extra carefully (since 3.12), so adding
        # them one by one with + can be out in the last decimal place.
        return sum(word_score(doc_id, word) for word in words)

    matches = books_with(question[0])
    words = [question[0]]
    join = "AND"
    for piece in question[1:]:
        if piece.upper() in {"AND", "OR", "NOT"}:
            join = piece.upper()
            continue
        if join == "NOT":
            matches -= books_with(piece)  # filters only: it adds nothing to the score
        else:
            matches = matches & books_with(piece) if join == "AND" else matches | books_with(piece)
            words.append(piece)
        join = "AND"
    answers = [(doc_id, score(doc_id, words)) for doc_id in matches]
    return sorted(answers, key=lambda answer: (-answer[1], answer[0]))
