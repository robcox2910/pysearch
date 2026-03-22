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

"running", "runs", and "ran" all mean the same root word: "run".
**Stemming** reduces words to their root form so they all match.
Our simplified stemmer handles common English suffixes.

## What We Test

- Text is split into individual words.
- Everything is lowercased.
- Punctuation is removed.
- Stop words are filtered out.
- Basic stemming works (running → run).

## Next Up

Now that we have word cards, let's build the lookup table.
Head to [Inverted Index](inverted-index.md).
