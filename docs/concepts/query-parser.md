# Query Parser

## Understanding Your Question

When you type `dinosaur AND volcano` into a search engine, it needs
to understand that you want documents containing BOTH words, not
documents containing the phrase "dinosaur AND volcano".

The **query parser** breaks your search text into a structured query:

```
"cat AND dog"       → AND(cat, dog)     -- both required
"cat OR dog"        → OR(cat, dog)      -- either works
"cat NOT dog"       → NOT(cat, dog)     -- cat, but never dog
"cat dog"           → AND(cat, dog)     -- words side by side: all required
"cat"               → TERM(cat)         -- just one word
"cat AND dog OR fish" → OR(AND(cat, dog), fish) -- read left to right
```

## Taking Books Away with NOT

`NOT` is like sorting a pile of books. Grab every book that matches the left
side, then put back any book that mentions the word on the right:

```
"cats NOT dogs"      → books about cats that never mention dogs
"cats AND NOT dogs"  → exactly the same (some people like to write it this way)
```

The word after `NOT` only filters. It never adds to a book's score, because a
book can't be a better match for a word it doesn't contain.

`NOT` needs a word on both sides, just like `AND` and `OR`: `NOT dogs` on its
own is an error, because there's nothing to take the dogs away *from*. And
like `and` and `or`, a lowercase `not` counts as the operator too.

## Cleaning Up Your Words

The parser cleans each word up *exactly* the way documents were cleaned when
they were filed -- otherwise your question and the library's notebook would
spell things differently and never match:

- Punctuation goes: `fox,` searches for `fox`.
- Boring stop words go: `the cats` searches for `cats`.
- A word that falls into pieces needs every piece: `state-of-the-art`
  becomes `state AND art` (`of` and `the` are stop words).

If a query has nothing left to search for (`the of a`), or an `AND`/`OR`/`NOT`
without a word on both sides (`cats OR`), the parser says so with a
`QueryParseError` instead of guessing.

## Query Types in PySearch

```python
from pysearch.query import parse_query

query = parse_query("dinosaur AND volcano")
# AndQuery(left=TermQuery("dinosaur"), right=TermQuery("volcano"))

query = parse_query("cat OR dog")
# OrQuery(left=TermQuery("cat"), right=TermQuery("dog"))

query = parse_query("cat NOT dog")
# NotQuery(left=TermQuery("cat"), right=TermQuery("dog"))
```

## What We Test

- Single words parse as term queries.
- AND, OR and NOT combine terms; longer chains read left to right.
- NOT leaves out books with the word after it, and that word adds nothing to the score.
- Words side by side mean AND.
- Query words lose punctuation and stop words, just like document words.
- Dangling operators and stop-word-only queries raise `QueryParseError`.

## What's Next?

You've learned every piece of a search engine! Tokenization, the
inverted index, TF-IDF ranking, and query parsing. These are the
same concepts that power Google, Elasticsearch, and every search
box you've ever used.
