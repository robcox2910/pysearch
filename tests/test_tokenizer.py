"""Test the tokenizer -- cutting sentences into word cards."""

from pysearch.tokenizer import STOP_WORDS, simple_stem, tokenize

STOP_WORD_COUNT = 24


class TestTokenize:
    """Test the tokenize function."""

    def test_lowercase_output(self) -> None:
        """Verify all tokens are lowercased."""
        result = tokenize("Hello World")
        assert result == ["hello", "world"]

    def test_punctuation_removed(self) -> None:
        """Verify punctuation is stripped from tokens."""
        result = tokenize("hello, world!")
        assert result == ["hello", "world"]

    def test_stop_words_removed(self) -> None:
        """Verify common stop words are filtered out."""
        result = tokenize("the cat is on the mat")
        assert "the" not in result
        assert "is" not in result
        assert "on" not in result
        assert "cat" in result
        assert "mat" in result

    def test_empty_input(self) -> None:
        """Verify empty string returns an empty list."""
        result = tokenize("")
        assert result == []

    def test_only_stop_words(self) -> None:
        """Verify a string of only stop words returns an empty list."""
        result = tokenize("the a an is are")
        assert result == []

    def test_multiple_spaces(self) -> None:
        """Verify multiple spaces between words are handled."""
        result = tokenize("hello    world")
        assert result == ["hello", "world"]

    def test_numbers_kept(self) -> None:
        """Verify numeric tokens are preserved."""
        result = tokenize("version 3 released")
        assert "3" in result

    def test_mixed_punctuation(self) -> None:
        """Verify various punctuation characters are handled."""
        result = tokenize("hello-world foo_bar baz.qux")
        assert "hello" in result
        assert "world" in result
        assert "foo" in result
        assert "bar" in result

    def test_stemming_applied(self) -> None:
        """Verify tokens are stemmed during tokenization."""
        result = tokenize("running played quickly")
        assert "run" in result
        assert "play" in result
        assert "quick" in result

    def test_stop_words_frozenset(self) -> None:
        """Verify STOP_WORDS is a frozenset with the expected count."""
        assert isinstance(STOP_WORDS, frozenset)
        assert len(STOP_WORDS) == STOP_WORD_COUNT

    def test_tabs_and_newlines(self) -> None:
        """Verify tabs and newlines are treated as separators."""
        result = tokenize("hello\tworld\nfoo")
        assert "hello" in result
        assert "world" in result
        assert "foo" in result


class TestSimpleStem:
    """Test the simple_stem function."""

    def test_strip_ing(self) -> None:
        """Verify 'ing' suffix is removed."""
        assert simple_stem("running") == "runn"

    def test_strip_ed(self) -> None:
        """Verify 'ed' suffix is removed."""
        assert simple_stem("played") == "play"

    def test_strip_ly(self) -> None:
        """Verify 'ly' suffix is removed."""
        assert simple_stem("quickly") == "quick"

    def test_strip_er(self) -> None:
        """Verify 'er' suffix is removed."""
        assert simple_stem("faster") == "fast"

    def test_strip_est(self) -> None:
        """Verify 'est' suffix is removed."""
        assert simple_stem("fastest") == "fast"

    def test_strip_s(self) -> None:
        """Verify 's' suffix is removed."""
        assert simple_stem("cats") == "cat"

    def test_no_strip_short_word(self) -> None:
        """Verify suffix is not removed if result would be too short."""
        assert simple_stem("bed") == "bed"

    def test_no_suffix(self) -> None:
        """Verify words without matching suffixes are unchanged."""
        assert simple_stem("python") == "python"

    def test_priority_ing_over_s(self) -> None:
        """Verify 'ing' is checked before 's' for words ending in 'ings'."""
        assert simple_stem("savings") == "sav"
