# PySearch

**An educational full-text search engine built from scratch in Python.**

## The Librarian Who Read Every Book

Imagine a librarian who has read every single book in the library. When you ask
her "Which books mention *dinosaurs*?", she doesn't need to open a single book.
She already knows the answer because she kept notes while reading.

For every word she encountered, she wrote down which book it was in and how many
times it appeared. Her notebook is called an **inverted index**, and it lets her
answer your question in the blink of an eye.

But what if ten books mention dinosaurs? Which one should you read first? The
librarian uses a clever trick called **TF-IDF** -- she ranks the books so the
ones that talk about dinosaurs *the most* (and about other things *the least*)
float to the top.

PySearch teaches you how to build this librarian from scratch.

## Examples

### Adding Documents and Searching

```python
from pysearch.engine import SearchEngine

# Create a search engine and add some documents
engine = SearchEngine()
engine.add("doc1", "Python is a great programming language")
engine.add("doc2", "Java is also a popular language")
engine.add("doc3", "Python and Java are both used for web development")

# Search for a single term -- results ranked by relevance
results = engine.search("python")
for doc_id, score in results:
    print(f"{doc_id}: {score:.4f}")

# Boolean queries
results = engine.search("python AND java")   # documents with both
results = engine.search("python OR java")    # documents with either
```

### Using the Tokenizer Directly

```python
from pysearch.tokenizer import tokenize, simple_stem

tokens = tokenize("The quick brown foxes are running!")
print(tokens)  # ['quick', 'brown', 'fox', 'runn']

print(simple_stem("running"))  # 'runn'
print(simple_stem("played"))   # 'play'
print(simple_stem("quickly"))  # 'quick'
```

### Building an Inverted Index

```python
from pysearch.index import InvertedIndex

index = InvertedIndex()
index.add_document("doc1", "cats and dogs")
index.add_document("doc2", "cats and birds")
index.add_document("doc3", "dogs and birds")

print(index.search("cat"))            # ['doc1', 'doc2']
print(index.search_and(["cat", "dog"]))  # ['doc1']
print(index.search_or(["cat", "dog"]))   # ['doc1', 'doc2', 'doc3']
```

## Features

- **Tokenizer** -- Split text into searchable words, remove stop words, and
  apply simple stemming
- **Inverted Index** -- Map every word to the documents that contain it for
  instant lookups
- **TF-IDF Ranking** -- Score and rank results so the most relevant documents
  come first
- **Boolean Queries** -- Combine search terms with AND and OR operators
- **100% Typed** -- Full type annotations with strict Pyright checking

## Quick Start

```bash
# Install from source
git clone https://github.com/robcox2910/pysearch.git
cd pysearch
uv sync --all-extras

# Run the tests
uv run pytest

# Try it in a Python shell
uv run python -c "
from pysearch.engine import SearchEngine
engine = SearchEngine()
engine.add('doc1', 'hello world')
print(engine.search('hello'))
"
```

## Documentation

Full documentation with kid-friendly explanations of every concept:
[https://robcox2910.github.io/pysearch/](https://robcox2910.github.io/pysearch/)

## Related Projects

PySearch is part of a series of educational "build it from scratch" projects:

| Project | What it builds |
|---------|---------------|
| [PyOS](https://github.com/robcox2910/pyos) | An operating system |
| [Pebble](https://github.com/robcox2910/pebble) | A database engine |
| [PyDB](https://github.com/robcox2910/pydb) | A SQL database |
| [PyStack](https://github.com/robcox2910/pystack) | A network stack |
| [PyWeb](https://github.com/robcox2910/pyweb) | An HTTP framework |
| [PyGit](https://github.com/robcox2910/pygit) | A version control system |
| [PyNet](https://github.com/robcox2910/pynet) | A network protocol suite |
| [PyCrypt](https://github.com/robcox2910/pycrypt) | A cryptography library |

## License

MIT -- see [LICENSE](LICENSE) for details.
