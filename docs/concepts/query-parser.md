# Query Parser

## Understanding Your Question

When you type `dinosaur AND volcano` into a search engine, it needs
to understand that you want documents containing BOTH words, not
documents containing the phrase "dinosaur AND volcano".

The **query parser** breaks your search text into a structured query:

```
"cat AND dog"       → AND(cat, dog)     -- both required
"cat OR dog"        → OR(cat, dog)      -- either works
"cat"               → TERM(cat)         -- just one word
```

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
- AND combines two terms.
- OR combines two terms.
- The parser handles AND and OR between two terms.

## What's Next?

You've learned every piece of a search engine! Tokenization, the
inverted index, TF-IDF ranking, and query parsing. These are the
same concepts that power Google, Elasticsearch, and every search
box you've ever used.
