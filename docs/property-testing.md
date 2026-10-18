# Property Testing (Every Book, Every Question)

## The Library Inspector

Our search engine is a librarian with a perfect notebook: for every word,
she has written down which books it's in. Ask her "which books mention
foxes?" and she flips to the right page. She never rereads a book.

How would you check she gets it right? The usual way: put two books on
the shelf, ask about a word you know is in one of them, and check that
book comes back. That's an **example test**. It's useful, but it only
tells you about the one question you thought of.

Now imagine an inspector. She doesn't trust notebooks. All day she
fills the shelves with new books -- tiny ones, empty ones, books with
odd names, books that say "cat" six times -- and asks the librarian
question after question: `cats`, `dog OR fox`, `berries AND running`.
Then, for every single question, she works out the answer the slow way,
by opening every book and reading it, word by word. Her rule is:

> Whatever the books and whatever the question, the librarian's answer
> is exactly what reading every book gives.

That rule is a **property**. It doesn't say what any one answer should
be. It says something that must be true for *every* library and *every*
question.

When the inspector catches a wrong answer, she doesn't just report
"something went wrong with a shelf of six books and a long question".
She tries again with fewer books, shorter books and shorter questions,
checking it still goes wrong each time, until it's as small as it can
be. That boiling-down is called **shrinking**, and the smallest failing
input usually points straight at the bug.

In Python, the inspector is a library called
[Hypothesis](https://hypothesis.readthedocs.io/). PySearch's property
tests live in `tests/test_properties.py`, next to the ordinary example
tests, and the model check (more on that below) is in
`tests/test_model.py`.

## A Property from PySearch

Here's the inspector's main rule. First the recipes for her books and
questions, from `tests/strategies.py`:

```python
def doc_ids() -> st.SearchStrategy[str]:
    """Make any document id at all: empty, spaces, emoji, slashes, NUL, the lot."""
    return st.text()


def books() -> st.SearchStrategy[Book]:
    """Make one book: its words, and the gap that sits between each pair of them."""
    return st.tuples(book_words(), st.sampled_from(GAPS))


def libraries() -> st.SearchStrategy[dict[str, Book]]:
    """Make a whole library: up to six books, each under its own unique id."""
    return st.dictionaries(doc_ids(), books(), max_size=MOST_BOOKS)


def questions() -> st.SearchStrategy[list[str]]:
    """Make a question as a list of pieces: words, with AND or OR (or nothing) between them."""
    joins = st.sampled_from(JOINS)
    rest = st.lists(st.tuples(joins, st.sampled_from(SEARCH_WORDS)), max_size=4)
    return st.tuples(st.sampled_from(SEARCH_WORDS), rest).map(lay_out_question)
```

And the property, from `tests/test_properties.py`:

```python
@given(library=libraries(), question=questions())
def test_search_finds_what_reading_every_book_finds(
    library: dict[str, Book], question: list[str]
) -> None:
    """The engine gives exactly the brute-force librarian's books, scores and order."""
    engine = engine_holding(library)
    answer = engine.search(" ".join(question))
    assert answer == brute_force_search(library, question)
```

Line by line:

- **The functions at the top are strategies**: recipes for random
  inputs. `doc_ids()` makes any string at all as a book's id, including
  `""`, `"🦊"` and `"a/b"`. A book is its list of words plus the gap
  between them (a space, a comma, a hyphen, a new line...).
- **Why a word list?** Random letters almost never spell the same word
  twice, so a search for a random word would almost always find
  nothing. `book_words()` and `questions()` pick from a short list
  where words share roots on purpose (`cat`, `cats`, `Cat`; `berry`,
  `berries`), plus stop words like `the` that must be ignored.
- **`questions()`** makes a first word, then up to four more, each with
  one of the `JOINS` in front: `AND`, `OR` (in either case) or nothing.
  `lay_out_question` flattens that into a list such as
  `['cats', 'OR', 'dog', 'fox']`.
- **`@given(...)`** tells Hypothesis to run the test many times (100 in
  a normal run), each with a fresh library and question.
- **`engine_holding(library)`** is a helper that makes a `SearchEngine`
  and adds every book.
- **`brute_force_search`** (in `tests/brute_force.py`) is the inspector
  reading every book. She has no index. For each question word she
  opens every book and counts; she reads `AND` and `OR`
  [left to right](concepts/query-parser.md) herself; she works out each
  [TF-IDF](concepts/tfidf.md) score from those counts, and sorts best
  first, with equal scores in order of id.
- **The `assert`** compares everything at once: which books, their
  scores, and their order.

Notice what the test *doesn't* say. It never says "the answer to `cats`
is book 1". It doesn't need to know any answers. It only needs a slow
way of working them out that is obviously right.

PySearch has five more properties:

| Rule | Test |
|---|---|
| Scores never go up as you read down the results, and equal scores are in id order | `test_results_come_best_first_and_ties_by_id` |
| Whatever you type, search gives a list of books in the library or a `QueryParseError` | `test_any_question_gives_results_or_query_parse_error` |
| A loaded engine holds the same books and answers every question the same way | `test_save_then_load_gives_back_the_same_engine` |
| Whatever bytes are in the file, loading gives an engine or a `PersistenceError` | `test_any_bytes_on_disk_load_or_raise_persistence_error` |
| Whatever a save-shaped JSON file holds, loading gives an engine or a `PersistenceError` | `test_any_save_shaped_json_load_or_raise_persistence_error` |

**A search that does nothing -- always answering `[]` -- passes the
ordering property**, because an empty list is perfectly in order. That's
why the brute-force property sits beside it: it fails the moment a
search misses a book.

The save/load property is PySearch's oldest. It used to live in
`tests/test_persistence.py` with its own settings; it moved here so all
the properties share one home and one set of settings.

## Checking Against a Model

A property checks one action. But a search engine is something you
change step by step: add a book, ask, add another, save, ask again.
Bugs often hide in the *order* of steps -- adding a book under an id
that's already taken, or asking a question right after reloading.

So the inspector has a second trick. She carries a notebook of her own,
but it's the simplest one possible: just each book's id and its words,
in the order they arrived. After every single step she compares the
librarian with her notebook, and every time the librarian answers a
question, the inspector reads every book in her notebook to check.

That notebook is a **model**: something simple that we already trust.
Here's the heart of `tests/test_model.py`:

```python
class SearchEngineMachine(RuleBasedStateMachine):
    ids = Bundle("ids")

    def __init__(self) -> None:
        super().__init__()
        self.engine = SearchEngine()
        self.model: dict[str, Book] = {}

    @rule(target=ids, doc_id=doc_ids(), book=books())
    def add_book(self, doc_id: str, book: Book) -> str:
        """Add a book under any id: a new id is filed, a taken one is refused."""
        if doc_id in self.model:
            with pytest.raises(DuplicateDocumentError):
                self.engine.add(doc_id, text_of(book))
        else:
            self.engine.add(doc_id, text_of(book))
            self.model[doc_id] = book
        return doc_id

    @rule(question=questions())
    def ask(self, question: list[str]) -> None:
        """Ask a question: the engine gives the brute-force librarian's answer."""
        expected = brute_force_search(self.model, question)
        assert self.engine.search(" ".join(question)) == expected

    @invariant()
    def same_books(self) -> None:
        """After every step, the engine holds exactly the dict's books, in filing order."""
        texts = {doc_id: text_of(book) for doc_id, book in self.model.items()}
        assert self.engine.document_count == len(self.model)
        assert repr(self.engine.to_dict()) == repr({"format": 1, "documents": texts})


# why: 20 steps find the same bugs; 50 (the default) is most of the run time
SearchEngineMachine.TestCase.settings = settings(stateful_step_count=20)
TestSearchEngineModel = cast("type[unittest.TestCase]", SearchEngineMachine.TestCase)
```

Piece by piece:

- **`RuleBasedStateMachine`** is Hypothesis's tool for testing things
  that change step by step. Hypothesis makes up a random **story** of
  steps and plays it.
- **`self.engine` and `self.model`** are the librarian and the
  inspector's notebook (a plain `dict`). Every story starts with both
  empty.
- **Each `@rule`** is one kind of step. The real file has rules to add
  a book, add one under an id that's already taken, ask a question,
  save and reload the engine, and scribble on the saved data the engine
  handed out (the engine must have kept its own copy).
- **`ids = Bundle("ids")`** is a bag of ids used earlier in the story.
  Two random strings almost never match, so without it the story would
  hardly ever try a taken id. `add_book` puts its id in the bag
  (`target=ids`), and the "taken id" rule pulls one out.
- **`add_book`** checks what the engine *says* too: a taken id must be
  refused with `DuplicateDocumentError`. **`ask`** checks every answer
  against the inspector reading every book.
- **The `@invariant()`** runs after every step: the same number of
  books, the same texts, in the same order.
- **`TestSearchEngineModel = ...TestCase`** turns the machine into a
  test that pytest can find. One run plays 100 random stories, each up
  to 20 steps long.

The notebook is a good model because it's obviously right and it's
*not* the engine's code. The engine has an inverted index; the notebook
has none, and the inspector rereads everything every time. If we built
the model by copying the engine, any bug would be in both, and they'd
agree perfectly about the wrong answer.

## Try It Yourself

Let's break the query parser on purpose and watch the inspector find it.

In `src/pysearch/query.py`, `parse_query` reads your question word by
word. Each time it has used a word, it goes back to "words side by side
mean AND". Find that line, near the bottom of the loop, and swap it for
`pass`, as if you'd forgotten it:

```python
        pass  # was: pending_operator = "AND"
```

Now `dog OR dog cat` means `dog OR dog OR cat`, when it should mean
`(dog OR dog) AND cat`. Run the property tests:

```bash
uv run pytest tests/test_properties.py tests/test_model.py --no-cov
```

Hypothesis reports this (trimmed to the interesting part):

```
    @given(library=libraries(), question=questions())
    def test_search_finds_what_reading_every_book_finds(
        library: dict[str, Book], question: list[str]
    ) -> None:
        """The engine gives exactly the brute-force librarian's books, scores and order."""
        engine = engine_holding(library)
        answer = engine.search(" ".join(question))
>       assert answer == brute_force_search(library, question)
E       AssertionError: assert [('', 0.0)] == []
E
E         Left contains one more item: ('', 0.0)
E       Failing test case: test_search_finds_what_reading_every_book_finds(
E           library={'': (['cat'], ' ')},
E           question=['dog', 'OR', 'dog', 'cat'],
E       )
```

Look at how small that is. One book, with an empty id, that says just
`cat`. One question: `dog OR dog cat`. No book mentions a dog, so
`(dog OR dog) AND cat` finds nothing, and the inspector's answer is
`[]`. But the engine read it as "dog, or dog, or cat" and handed back
the cat book. (Its score is `0.0` because a word that's in *every* book
tells you nothing: log(1 / 1) is 0.)

The model check catches it too, with a two-step story: add the book
`cat`, then ask `cat OR cat dog`. The ordering property stays green:
the wrong answer is still sorted nicely.

The example tests all still pass. Only the property notices. The
examples try `cat OR dog`, chains like `cats AND dogs OR fish`, and
words side by side (`cats dogs`), but none puts two words side by side
*after* an `OR`.

Put the line back and run the tests again. They pass.

!!! tip "Older Hypothesis versions"
    Older versions of Hypothesis print `Falsifying example:` instead of
    `Failing test case:`. It means the same thing.

## A Bug We Found

When we first ran `test_any_bytes_on_disk_load_or_raise_persistence_error`,
it failed on PySearch's real code -- no deliberate bug needed:

```
E   UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 0: invalid start byte
E   Failing test case: test_any_bytes_on_disk_load_or_raise_persistence_error(
E       junk=b'\x80',
E   )
```

A save file holding **one byte**, `0x80`, crashed `load_engine` with a
`UnicodeDecodeError` instead of a `PersistenceError`. In UTF-8 that
byte can only sit in the *middle* of a character, so a file starting
with it isn't text at all. The loader expected a missing file
(`OSError`) or text that isn't JSON, but this fails in between: the
bytes are read fine, then can't be turned into text.

The example tests tried a missing file and `{not json` -- both text.
Nobody thought to try a file that isn't text at all. The inspector
didn't need to: `st.binary()` makes bytes like that all the time.

The fix:

```python
except (OSError, UnicodeDecodeError) as exc:  # was: except OSError as exc:
```

and the shrunk input became an example test in
`tests/test_persistence.py`:

```python
    def test_a_file_that_is_not_text_raises_persistence_error(self, tmp_path: Path) -> None:
        """Regression: a lone 0x80 byte (found by Hypothesis) raised UnicodeDecodeError."""
        path = tmp_path / "engine.json"
        path.write_bytes(b"\x80")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)
```

We found two cousins by *reading* the code, not with the property:
a 5,000-digit number (`ValueError`) and 100,000 `[` characters
(`RecursionError`) also crashed the loader. Random JSON is almost never
that big. Both are now a `PersistenceError` and pinned as tests.
Reading the code also turned up a third bug, in `search` this time: a
question of about 1,000 words or more crashed it with `RecursionError`.
No property found that one either. A 2,000-word question is now
answered like any other, and pinned as a test.

## Run It Yourself

Run just the property tests and the model check (100 examples each, the
same every time):

```bash
uv run pytest tests/test_properties.py tests/test_model.py --no-cov
```

The `--no-cov` turns off the coverage check, which expects the *whole*
test suite to run and would fail on two files.

Run them the long way (2,000 random examples each, different every run)
to hunt for rarer bugs. It takes about two minutes:

```bash
uv run pytest tests/test_properties.py tests/test_model.py --no-cov --hypothesis-profile=thorough
```

The normal run uses a fixed seed, so it tries the same inputs every time
and a passing build means the same thing on every computer. The thorough
run is random, so each time you run it the inspector brings a brand-new
pile of books and questions. Both settings live in `conftest.py` at the
top of the project.

## Your Turn

Write one new property for PySearch. Does `cats OR dogs` give exactly
the same answer as `dogs OR cats`, whatever is on the shelves? What's
the strategy? (Look in `tests/strategies.py`.) What's
the `assert`? Try it in a scratch file and watch it pass. Then break
`OR` on purpose and watch the inspector find it.
