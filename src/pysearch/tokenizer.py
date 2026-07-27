"""Tokenize text into searchable words.

Think of a tokenizer like cutting sentences into word cards. You take a long
sentence, snip it into individual words, throw away boring words like "the"
and "is," and keep the interesting ones. Each card can then be filed in the
index so you can find it later.
"""

import re

STOP_WORDS: frozenset[str] = frozenset(
    {
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
    }
)

_SUFFIX_ORDER: tuple[str, ...] = ("ing", "ed", "ly", "er", "est", "es", "s")
_MIN_STEM_LENGTH = 3


def tokenize(text: str) -> list[str]:
    """Cut a sentence into clean word cards -- lowercased, punctuation gone, boring words tossed.

    Args:
        text: The raw text to tokenize.

    Returns:
        A list of stemmed, lowercase tokens with stop words removed.

    """
    words = re.split(r"[^a-zA-Z0-9]+", text.lower())
    return [simple_stem(w) for w in words if w and w not in STOP_WORDS]


def simple_stem(word: str) -> str:
    """Trim a word down to its root so "foxes" and "fox" count as the same word.

    We only chop an ending off if enough of the word is left over (at least 3
    letters), so tiny words like "bed" stay whole. Plural "-ies" becomes "-y"
    ("berries" -> "berry"), plural "-es" is dropped ("foxes" -> "fox"), and the
    other endings checked in order are: "ing", "ed", "ly", "er", "est", "s".

    Args:
        word: The word to stem.

    Returns:
        The stemmed word.

    """
    # Plural "-ies" -> "-y" so "berries" and "berry" collapse to the same stem.
    if word.endswith("ies") and len(word) - len("ies") >= _MIN_STEM_LENGTH - 1:
        return word[:-3] + "y"
    for suffix in _SUFFIX_ORDER:
        if word.endswith(suffix) and len(word) - len(suffix) >= _MIN_STEM_LENGTH:
            return word[: -len(suffix)]
    return word
