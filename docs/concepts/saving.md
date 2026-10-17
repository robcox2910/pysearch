# Saving Your Index

## The Librarian's Notebook

At the end of the day the library closes and the librarian goes home.
Everything she knew -- which words are in which books -- lives in her head
(the computer's memory), and memory is wiped when the program stops.

So before she leaves, she writes every book into a **notebook**: a JSON
file on disk. Tomorrow she opens the notebook, files every book again, and
answers every question exactly as she did yesterday.

```python
from pysearch.engine import SearchEngine
from pysearch.persistence import load_engine, save_engine

engine = SearchEngine()
engine.add("cats", "Cats purr and nap in the sun")
save_engine(engine, "library.json")

tomorrow = load_engine("library.json")
tomorrow.search("purr")   # [("cats", ...)]
```

## Why Save the Books, Not the Index?

The notebook keeps each book's original text, not the index built from it.
Rebuilding the index on load is quick, and it means a saved file still
works even if we improve how the index is built later.

The file also records a **format number**. If a future version ever saves
things differently, an old program refuses the new file instead of
misreading it.

## Saving Safely

Saving writes a fresh copy beside the old file and then swaps it in, in one
instant step. A crash halfway through leaves yesterday's notebook untouched,
never half of each.

## When the Notebook Is Damaged

If the file is missing, isn't valid JSON, or isn't a saved search engine,
`load_engine` raises a `PersistenceError` that names the file. It never
quietly hands back an empty library.
