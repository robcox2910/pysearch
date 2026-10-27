"""Strategies -- recipes for random books and questions, shared by the property tests.

A strategy tells Hypothesis how to invent one kind of input. Each one here
is a named function, named for what it makes, with a one-line docstring.
``tests/test_properties.py`` and ``tests/test_model.py`` both use them.

Random letters almost never spell the same word twice, so a search for a
random word would almost always find nothing. Instead, books and questions
are built from a small word list where several words share a root ("cat"
and "cats", "berry" and "berries"), so searches really do find things.
"""

from hypothesis import strategies as st

from tests.brute_force import Book

# Words a question can use. None of them is a stop word, so every one of
# them is really searched for. Some share a root on purpose.
SEARCH_WORDS: tuple[str, ...] = (
    "cat",
    "cats",
    "Cat",
    "dog",
    "dogs",
    "fox",
    "foxes",
    "berry",
    "berries",
    "run",
    "running",
    "quick",
    "quickly",
)

# Stop words the librarian ignores. Books may contain them; questions don't.
IGNORED_WORDS: tuple[str, ...] = ("the", "and", "AND", "or", "not", "is")

# What can sit between two words in a book: tokenize splits on all of them.
GAPS: tuple[str, ...] = (" ", "  ", ", ", ". ", "-", "!\n")

# What can join two words in a question: an operator in either case, or
# nothing at all (two words side by side must both match).
JOINS: tuple[str, ...] = ("AND", "OR", "NOT", "and", "or", "not", "")

# A library holds at most this many books, each at most this many words.
# Small libraries find the same bugs, and a failure shrinks to a small one anyway.
MOST_BOOKS = 6
MOST_WORDS_PER_BOOK = 8


def doc_ids() -> st.SearchStrategy[str]:
    """Make any document id at all: empty, spaces, emoji, slashes, NUL, the lot."""
    return st.text()


def book_words() -> st.SearchStrategy[list[str]]:
    """Make the words of one book: search words and stop words, in any order."""
    return st.lists(st.sampled_from(SEARCH_WORDS + IGNORED_WORDS), max_size=MOST_WORDS_PER_BOOK)


def books() -> st.SearchStrategy[Book]:
    """Make one book: its words, and the gap that sits between each pair of them."""
    return st.tuples(book_words(), st.sampled_from(GAPS))


def libraries() -> st.SearchStrategy[dict[str, Book]]:
    """Make a whole library: up to six books, each under its own unique id."""
    return st.dictionaries(doc_ids(), books(), max_size=MOST_BOOKS)


def questions() -> st.SearchStrategy[list[str]]:
    """Make a question as a list of pieces: words, with AND, OR or NOT (or nothing) between them."""
    joins = st.sampled_from(JOINS)
    rest = st.lists(st.tuples(joins, st.sampled_from(SEARCH_WORDS)), max_size=4)
    return st.tuples(st.sampled_from(SEARCH_WORDS), rest).map(lay_out_question)


def lay_out_question(parts: tuple[str, list[tuple[str, str]]]) -> list[str]:
    """Lay out a question: the first word, then each join (if there is one) and its word."""
    first, rest = parts
    pieces = [first]
    for join, word in rest:
        pieces.extend([join, word] if join else [word])
    return pieces
