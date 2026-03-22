# Inverted Index

## The Librarian's Memory

A table of contents tells you what's in a book. An **inverted index**
flips it around: it tells you which books contain a specific word.

```
"dinosaur" → [Book 3, Book 7, Book 15]
"volcano"  → [Book 7, Book 22]
"fossil"   → [Book 3, Book 7]
```

Searching for "dinosaur" instantly returns [Book 3, Book 7, Book 15]
without opening a single book. That's the magic of an inverted index.

## How We Build It

1. For each document, tokenize the text into words
2. For each word, record which document it came from
3. Also record how many times it appears (for ranking later)

```python
from pysearch.index import InvertedIndex

index = InvertedIndex()
index.add_document("doc1", "The cat sat on the mat")
index.add_document("doc2", "The dog sat on the log")

index.search("cat")  # ["doc1"]
index.search("sat")  # ["doc1", "doc2"]
```

## Boolean Search

You can combine search terms:

- **AND**: both words must appear → `"cat AND mat"` → [doc1]
- **OR**: either word can appear → `"cat OR dog"` → [doc1, doc2]

## What We Test

- Adding documents populates the index.
- Searching returns correct document IDs.
- Words appearing in multiple documents return all of them.
- Searching for a missing word returns empty.

## Next Up

We can find documents, but which ones are most relevant?
Head to [TF-IDF](tfidf.md).
