import pytest

from pyharfrust import Buffer, Direction, Language, Script


# ---------------------------------------------------------------------------
# Construction / length
# ---------------------------------------------------------------------------


class TestCreation:
    def test_empty(self):
        buf = Buffer()
        assert len(buf) == 0

    def test_add_str_ascii(self):
        buf = Buffer()
        buf.add_str("Hello")
        assert len(buf) == 5

    def test_add_str_multi_bmp(self):
        buf = Buffer()
        buf.add_str("العربية")
        assert len(buf) == 7

    def test_add_str_astral(self):
        buf = Buffer()
        buf.add_str("A\U0001f600B")
        assert len(buf) == 3

    def test_add_str_empty(self):
        buf = Buffer()
        buf.add_str("")
        assert len(buf) == 0

    def test_add_str_multiple_calls_append(self):
        buf = Buffer()
        buf.add_str("Hel")
        buf.add_str("lo")
        assert len(buf) == 5

    def test_add_codepoint(self):
        buf = Buffer()
        buf.add(0x0041)
        buf.add(0x0042, cluster=7)
        assert len(buf) == 2


# ---------------------------------------------------------------------------
# Clear / reset
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear_empties(self):
        buf = Buffer()
        buf.add_str("hello")
        buf.clear()
        assert len(buf) == 0

    def test_clear_allows_reuse(self):
        buf = Buffer()
        buf.add_str("one")
        buf.clear()
        buf.add_str("two")
        assert len(buf) == 3

    def test_reset_clusters(self):
        buf = Buffer()
        buf.add_str("abc")
        buf.reset_clusters()
        assert len(buf) == 3


# ---------------------------------------------------------------------------
# Direction / Script / Language properties
# ---------------------------------------------------------------------------


class TestProperties:
    def test_set_get_direction(self):
        buf = Buffer()
        buf.direction = Direction.RTL
        assert buf.direction == Direction.RTL
        buf.direction = Direction.LTR
        assert buf.direction == Direction.LTR

    def test_set_get_script(self):
        buf = Buffer()
        buf.script = Script("Arab")
        assert buf.script == Script("Arab")
        buf.script = Script("Latn")
        assert buf.script == Script("Latn")

    def test_set_get_language(self):
        buf = Buffer()
        buf.language = Language("en")
        assert buf.language == Language("en")
        buf.language = Language("ar")
        assert buf.language == Language("ar")

    def test_language_none_when_unset(self):
        buf = Buffer()
        assert buf.language is None

    def test_direction_setter_rejects_nondirection(self):
        buf = Buffer()
        with pytest.raises(TypeError):
            buf.direction = "ltr"

    def test_script_setter_rejects_nonscript(self):
        buf = Buffer()
        with pytest.raises(TypeError):
            buf.script = "Latn"

    def test_language_setter_rejects_nonlanguage(self):
        buf = Buffer()
        with pytest.raises(TypeError):
            buf.language = "en"


# ---------------------------------------------------------------------------
# Context setters
#
# harfrust exposes only setters for pre/post context (no getters), so these
# tests can only confirm the calls don't raise. The real regression signal
# will come from Phase 5 shaping tests where context changes affect output.
# ---------------------------------------------------------------------------


class TestContext:
    def test_set_pre_context(self):
        buf = Buffer()
        buf.set_pre_context("abc")

    def test_set_post_context(self):
        buf = Buffer()
        buf.set_post_context("xyz")

    def test_set_not_found_variation_selector_glyph(self):
        buf = Buffer()
        buf.set_not_found_variation_selector_glyph(0)
        buf.set_not_found_variation_selector_glyph(42)


# ---------------------------------------------------------------------------
# guess_segment_properties
# ---------------------------------------------------------------------------


class TestGuessSegmentProperties:
    def test_arabic_guesses_rtl(self):
        buf = Buffer()
        buf.add_str("العربية")
        buf.guess_segment_properties()
        assert buf.direction == Direction.RTL
        assert buf.script == Script("Arab")

    def test_latin_guesses_ltr(self):
        buf = Buffer()
        buf.add_str("Hello")
        buf.guess_segment_properties()
        assert buf.direction == Direction.LTR
        assert buf.script == Script("Latn")


# ---------------------------------------------------------------------------
# reserve
# ---------------------------------------------------------------------------


class TestReserve:
    def test_reserve_returns_bool(self):
        buf = Buffer()
        result = buf.reserve(128)
        assert isinstance(result, bool)
        assert result is True

    def test_reserve_does_not_change_length(self):
        buf = Buffer()
        buf.add_str("hi")
        buf.reserve(1024)
        assert len(buf) == 2


# ---------------------------------------------------------------------------
# repr
# ---------------------------------------------------------------------------


class TestRepr:
    def test_repr_mentions_class(self):
        buf = Buffer()
        assert "Buffer" in repr(buf)

    def test_repr_shows_length(self):
        buf = Buffer()
        buf.add_str("hi")
        assert "2" in repr(buf)
