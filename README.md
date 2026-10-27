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
print(sorted(index.search_and(["cat", "dog"])))  # ['doc1']
print(sorted(index.search_or(["cat", "dog"])))   # ['doc1', 'doc2', 'doc3']
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

## Concepts

Saving an engine to disk and loading it back: [Saving Your Index](docs/concepts/saving.md).

<!-- docs:start -->
## Documentation

Full docs (with kid-friendly explanations of every idea): https://robcox2910.github.io/pysearch/

## Install

[![PyPI](https://img.shields.io/pypi/v/fromscratch-pysearch)](https://pypi.org/project/fromscratch-pysearch/)

```bash
pip install fromscratch-pysearch
```

Or get the whole series at once: `pip install fromscratch-pystack`.
<!-- docs:end -->

## Releasing

Other projects in the series ([PyStack](https://github.com/robcox2910/pystack)) use a released version of this one from PyPI,
not whatever is on `main`. To publish a change for them:

1. Merge the change to `main`.
2. Release it: `gh release create vX.Y.Z --target main --generate-notes`
   (or push a `vX.Y.Z` tag); the release workflow publishes it to PyPI.
   A change to the public API bumps the minor version (`v0.1.0` → `v0.2.0`);
   anything else bumps the patch (`v0.1.0` → `v0.1.1`).
3. In each project that uses it, raise the `fromscratch-pysearch>=X.Y.Z` floor in
   `pyproject.toml`, run `uv lock --upgrade-package fromscratch-pysearch`, and open
   a pull request so CI checks the pair together.

<!-- series:start -->
## Related Projects

This project is one of a series that builds real systems "from scratch in Python" to teach how they work. See the [series home](https://robcox2910.github.io/) for the full story.

| Project | What it teaches | Repository | Docs | PyPI |
| --- | --- | --- | --- | --- |
| PyOS | Operating systems | [py-os](https://github.com/robcox2910/py-os) | [Docs](https://robcox2910.github.io/py-os/) | [fromscratch-pyos](https://pypi.org/project/fromscratch-pyos/) |
| Pebble | Compilers and programming languages | [pebble-lang](https://github.com/robcox2910/pebble-lang) | [Docs](https://robcox2910.github.io/pebble-lang/) | [fromscratch-pebble](https://pypi.org/project/fromscratch-pebble/) |
| PyDB | Relational databases | [pydb](https://github.com/robcox2910/pydb) | [Docs](https://robcox2910.github.io/pydb/) | [fromscratch-pydb](https://pypi.org/project/fromscratch-pydb/) |
| PyKV | Key-value stores | [pykv](https://github.com/robcox2910/pykv) | [Docs](https://robcox2910.github.io/pykv/) | [fromscratch-pykv](https://pypi.org/project/fromscratch-pykv/) |
| PyDocDB | Document databases | [pydoc-db](https://github.com/robcox2910/pydoc-db) | [Docs](https://robcox2910.github.io/pydoc-db/) | [fromscratch-pydocdb](https://pypi.org/project/fromscratch-pydocdb/) |
| PyGraphDB | Graph databases | [pygraphdb](https://github.com/robcox2910/pygraphdb) | [Docs](https://robcox2910.github.io/pygraphdb/) | [fromscratch-pygraphdb](https://pypi.org/project/fromscratch-pygraphdb/) |
| PyTSDB | Time-series databases | [pytsdb](https://github.com/robcox2910/pytsdb) | [Docs](https://robcox2910.github.io/pytsdb/) | [fromscratch-pytsdb](https://pypi.org/project/fromscratch-pytsdb/) |
| PyVecDB | Vector databases | [pyvecdb](https://github.com/robcox2910/pyvecdb) | [Docs](https://robcox2910.github.io/pyvecdb/) | [fromscratch-pyvecdb](https://pypi.org/project/fromscratch-pyvecdb/) |
| PyColDB | Column-family databases | [pycoldb](https://github.com/robcox2910/pycoldb) | [Docs](https://robcox2910.github.io/pycoldb/) | [fromscratch-pycoldb](https://pypi.org/project/fromscratch-pycoldb/) |
| PyCrypt | Cryptography | [pycrypt](https://github.com/robcox2910/pycrypt) | [Docs](https://robcox2910.github.io/pycrypt/) | [fromscratch-pycrypt](https://pypi.org/project/fromscratch-pycrypt/) |
| PyNet | Computer networking | [pynet](https://github.com/robcox2910/pynet) | [Docs](https://robcox2910.github.io/pynet/) | [fromscratch-pynet](https://pypi.org/project/fromscratch-pynet/) |
| PyWeb | HTTP web servers | [pyweb](https://github.com/robcox2910/pyweb) | [Docs](https://robcox2910.github.io/pyweb/) | [fromscratch-pyweb](https://pypi.org/project/fromscratch-pyweb/) |
| PyGit | Version control | [pygit](https://github.com/robcox2910/pygit) | [Docs](https://robcox2910.github.io/pygit/) | [fromscratch-pygit](https://pypi.org/project/fromscratch-pygit/) |
| **PySearch** | **Search engines** | [pysearch](https://github.com/robcox2910/pysearch) | [Docs](https://robcox2910.github.io/pysearch/) | [fromscratch-pysearch](https://pypi.org/project/fromscratch-pysearch/) |
| PyMQ | Message queues | [pymq](https://github.com/robcox2910/pymq) | [Docs](https://robcox2910.github.io/pymq/) | [fromscratch-pymq](https://pypi.org/project/fromscratch-pymq/) |
| PyLLM | Language models (the brain) | [pyllm](https://github.com/robcox2910/pyllm) | [Docs](https://robcox2910.github.io/pyllm/) | [fromscratch-pyllm](https://pypi.org/project/fromscratch-pyllm/) |
| PyScheduler | Job scheduling | [pyscheduler](https://github.com/robcox2910/pyscheduler) | [Docs](https://robcox2910.github.io/pyscheduler/) | [fromscratch-pyscheduler](https://pypi.org/project/fromscratch-pyscheduler/) |
| PyStack | Full-stack integration | [pystack](https://github.com/robcox2910/pystack) | [Docs](https://robcox2910.github.io/pystack/) | [fromscratch-pystack](https://pypi.org/project/fromscratch-pystack/) |
<!-- series:end -->

## License

MIT -- see [LICENSE](LICENSE) for details.
