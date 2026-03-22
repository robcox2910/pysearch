# What Is a Search Engine?

## The Librarian Who Read Every Book

Imagine a librarian who has read every single book in the library.
When you ask "Which books mention dinosaurs?", they instantly rattle
off a list -- no searching required. They already know.

A **search engine** does the same thing for text. Before you search,
it reads every document and builds an **index** -- a giant lookup
table that maps every word to the documents it appears in. When you
search, it just looks up the word in the index. Instant results.

## How Google Works (Simplified)

```
Step 1: CRAWL -- read every webpage
Step 2: INDEX -- for each word, note which pages contain it
Step 3: RANK  -- when someone searches, find matching pages
                  and sort by relevance
```

PySearch builds steps 2 and 3 from scratch.

## The Big Ideas

### 1. Tokenization -- Breaking Text into Words

Before indexing, we break text into individual words (tokens):

```
"The quick brown fox" → ["the", "quick", "brown", "fox"]
```

We also **normalize** -- lowercase everything, remove punctuation,
so "Fox" and "fox" match.

### 2. Inverted Index -- The Magic Data Structure

A normal index maps documents to words (like a table of contents).
An **inverted** index flips it: it maps words to documents.

```
Normal:     Book 1 → ["the", "cat", "sat"]
            Book 2 → ["the", "dog", "ran"]

Inverted:   "the" → [Book 1, Book 2]
            "cat" → [Book 1]
            "dog" → [Book 2]
            "sat" → [Book 1]
            "ran" → [Book 2]
```

Searching for "cat" → instantly get [Book 1]. No scanning needed!

### 3. Ranking -- Which Results Come First?

Not all matches are equal. A document mentioning "dinosaur" 50 times
is probably more relevant than one mentioning it once. **TF-IDF**
(Term Frequency - Inverse Document Frequency) scores each result:

- **TF**: How often the word appears in THIS document (more = better)
- **IDF**: How rare the word is across ALL documents (rarer = better)

A word that appears often in one document but rarely in others gets
a high score. Common words like "the" get a low score.

## Our Building Blocks

| Concept | Analogy | What It Does |
|---------|---------|-------------|
| **Tokenizer** | Cutting sentences into word cards | Break text into searchable pieces |
| **Inverted Index** | The librarian's memory | Map words → documents |
| **TF-IDF** | Relevance scoring | Rank results by importance |
| **Query Parser** | Understanding your question | Parse "cat AND dog" into a structured query |
| **Search Engine** | The librarian herself | Tie everything together |

## Let's Start!

Head to [Tokenizer](concepts/tokenizer.md) to learn how text gets
broken into searchable pieces.
