# Query Parser

## Understanding Your Question

When you type `dinosaur AND volcano` into a search engine, it needs
to understand that you want documents containing BOTH words, not
documents containing the phrase "dinosaur AND volcano".

The **query parser** breaks your search text into a structured query:

```
"cat AND dog"       → AND(cat, dog)     -- both required
"cat OR dog"        → OR(cat, dog)      -- either works
"cat dog"           → AND(cat, dog)     -- words side by side: all required
"cat"               → TERM(cat)         -- just one word
"cat AND dog OR fish" → OR(AND(cat, dog), fish) -- read left to right
```

## Cleaning Up Your Words

The parser cleans each word up *exactly* the way documents were cleaned when
they were filed -- otherwise your question and the library's notebook would
spell things differently and never match:

- Punctuation goes: `fox,` searches for `fox`.
- Boring stop words go: `the cats` searches for `cats`.
- A word that falls into pieces needs every piece: `state-of-the-art`
  becomes `state AND art` (`of` and `the` are stop words).

If a query has nothing left to search for (`the of a`), or an `AND`/`OR`
without a word on both sides (`cats OR`), the parser says so with a
`QueryParseError` instead of guessing.

## Query Types in PySearch

```python
from pysearch.query import parse_query

query = parse_query("dinosaur AND volcano")
# AndQuery(left=TermQuery("dinosaur"), right=TermQuery("volcano"))

query = parse_query("cat OR dog")
# OrQuery(left=TermQuery("cat"), right=TermQuery("dog"))
```

## What We Test

- Single words parse as term queries.
- AND and OR combine terms; longer chains read left to right.
- Words side by side mean AND.
- Query words lose punctuation and stop words, just like document words.
- Dangling operators and stop-word-only queries raise `QueryParseError`.

## What's Next?

You've learned every piece of a search engine! Tokenization, the
inverted index, TF-IDF ranking, and query parsing. These are the
same concepts that power Google, Elasticsearch, and every search
box you've ever used.
