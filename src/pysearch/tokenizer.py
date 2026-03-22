"""Tokenize text into searchable words.

Think of a tokenizer like cutting sentences into word cards. You take a long
sentence, snip it into individual words, throw away boring words like "the"
and "is," and keep the interesting ones. Each card can then be filed in the
index so you can find it later.
"""

import re

STOP_WORDS: frozenset[str] = frozenset({
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "and",
    "or",
    "but",
    "not",
    "it",
    "this",
    "that",
    "with",
    "from",
    "by",
})

_SUFFIX_ORDER: tuple[str, ...] = ("ing", "ed", "ly", "er", "est", "s")
_MIN_STEM_LENGTH = 3


def tokenize(text: str) -> list[str]:
    """Split text into lowercase tokens with stop words removed.

    Args:
        text: The raw text to tokenize.

    Returns:
        A list of stemmed, lowercase tokens with stop words removed.
    """
    words = re.split(r"[^a-zA-Z0-9]+", text.lower())
    return [simple_stem(w) for w in words if w and w not in STOP_WORDS]


def simple_stem(word: str) -> str:
    """Strip common English suffixes from a word.

    Only strip a suffix if the remaining stem is at least 3 characters long.
    Suffixes checked (in order): "ing", "ed", "ly", "er", "est", "s".

    Args:
        word: The word to stem.

    Returns:
        The stemmed word.
    """
    for suffix in _SUFFIX_ORDER:
        if word.endswith(suffix) and len(word) - len(suffix) >= _MIN_STEM_LENGTH:
            return word[: -len(suffix)]
    return word
