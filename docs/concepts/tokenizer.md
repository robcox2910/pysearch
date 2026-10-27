# Tokenizer

## Cutting Sentences into Word Cards

Imagine you have a sentence on a long strip of paper. You take
scissors and cut it into individual word cards. Then you lowercase
each card and throw away punctuation. That's **tokenization**.

```
"The Quick, Brown Fox!" → ["the", "quick", "brown", "fox"]
```

## Why Tokenize?

Without tokenization, searching for "fox" wouldn't match "Fox" or
"fox!" -- they'd be different strings. Tokenization normalizes
everything so matches work naturally.

## Stop Words

Some words are so common they're useless for searching: "the", "a",
"is", "and". These are **stop words** and we filter them out to keep
the index small and results relevant.

```
"The cat is on the mat" → ["cat", "mat"]
(removed: "the", "is", "on")
```

## Stemming (Simplified)

"played", "playing" and "plays" all come from the same root word: "play".
**Stemming** trims words back to a root so they match each other.

Our stemmer is deliberately simple: it snips common English endings like
"-ing", "-ed" and "-s". That works for many words, but not all. "running"
becomes "runn" (the doubled letter stays), and "ran" stays "ran", because a
word that changes its spelling can't be fixed by snipping an ending. Real
search engines use cleverer stemmers (such as Porter or Snowball) or a
dictionary. Trying one is a good exercise!

## What We Test

- Text is split into individual words.
- Everything is lowercased.
- Punctuation is removed.
- Stop words are filtered out.
- Basic stemming works (played → play).

## Next Up

Now that we have word cards, let's build the lookup table.
Head to [Inverted Index](inverted-index.md).
