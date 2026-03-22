# TF-IDF

## The Relevance Score

If you search for "dinosaur", you get 100 results. But which one
should be first? The one that mentions "dinosaur" 50 times, or the
one that mentions it once?

**TF-IDF** (Term Frequency × Inverse Document Frequency) answers
this:

### TF: How Often?

**Term Frequency** = how many times the word appears in THIS document.

```
Doc A: "The dinosaur ate the dinosaur food" → TF("dinosaur") = 2
Doc B: "I saw a dinosaur"                  → TF("dinosaur") = 1
```

Doc A is more about dinosaurs, so it scores higher.

### IDF: How Rare?

**Inverse Document Frequency** = how rare the word is across ALL
documents. Common words like "the" get a low score. Rare words like
"dinosaur" get a high score.

```
"the"      appears in 100/100 documents → IDF ≈ 0 (useless)
"dinosaur" appears in 3/100 documents   → IDF ≈ 3.5 (valuable!)
```

### TF × IDF = Relevance

Multiply them: a word that appears often in ONE document but rarely
in others gets the highest score. That's your most relevant result.

## What We Test

- TF increases with word frequency in a document.
- IDF increases with word rarity across documents.
- TF-IDF correctly ranks more relevant documents higher.
- Common words get low scores.

## Next Up

We can find and rank results. But how do we understand complex
queries? Head to [Query Parser](query-parser.md).
