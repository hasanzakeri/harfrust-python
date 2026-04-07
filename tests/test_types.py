import pytest

from pyharfrust import Direction, Feature, Language, Script, Variation


# ---------------------------------------------------------------------------
# Direction
# ---------------------------------------------------------------------------


class TestDirection:
    def test_from_string(self):
        assert Direction("ltr") == Direction.LTR
        assert Direction("rtl") == Direction.RTL
        assert Direction("ttb") == Direction.TTB
        assert Direction("btt") == Direction.BTT

    def test_str(self):
        assert str(Direction.LTR) == "ltr"
        assert str(Direction.RTL) == "rtl"
        assert str(Direction.TTB) == "ttb"
        assert str(Direction.BTT) == "btt"

    def test_repr(self):
        assert repr(Direction.LTR) == "Direction.LTR"
        assert repr(Direction.RTL) == "Direction.RTL"

    def test_equality(self):
        assert Direction("ltr") == Direction("ltr")
        assert Direction("ltr") != Direction("rtl")

    def test_hash(self):
        s = {Direction.LTR, Direction.RTL, Direction.LTR}
        assert len(s) == 2

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid direction"):
            Direction("xyz")

    def test_case_insensitive(self):
        assert Direction("LTR") == Direction.LTR
        assert Direction("Rtl") == Direction.RTL


# ---------------------------------------------------------------------------
# Script
# ---------------------------------------------------------------------------


class TestScript:
    def test_common_scripts(self):
        s = Script("Latn")
        assert s.tag == "Latn"

    def test_arabic(self):
        s = Script("Arab")
        assert s.tag == "Arab"

    def test_str(self):
        s = Script("Latn")
        assert str(s) == "Latn"

    def test_repr(self):
        s = Script("Latn")
        assert repr(s) == 'Script("Latn")'

    def test_equality(self):
        assert Script("Latn") == Script("Latn")
        assert Script("Latn") != Script("Arab")

    def test_hash(self):
        s = {Script("Latn"), Script("Arab"), Script("Latn")}
        assert len(s) == 2

    def test_unknown_script_explicit(self):
        s = Script("Zzzz")
        assert s.tag == "Zzzz"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="4-letter ISO 15924"):
            Script("XXXXX")
        with pytest.raises(ValueError, match="4-letter ISO 15924"):
            Script("")
        with pytest.raises(ValueError, match="4-letter ISO 15924"):
            Script("1234")

    def test_case_normalization(self):
        assert Script("latn").tag == "Latn"


# ---------------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------------


class TestLanguage:
    def test_basic(self):
        lang = Language("en")
        assert str(lang) == "en"

    def test_subtag(self):
        lang = Language("en-US")
        assert str(lang) == "en-us"

    def test_repr(self):
        lang = Language("en")
        assert repr(lang) == 'Language("en")'

    def test_equality(self):
        assert Language("en") == Language("en")
        assert Language("en") != Language("ar")

    def test_hash(self):
        s = {Language("en"), Language("ar"), Language("en")}
        assert len(s) == 2

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid language"):
            Language("")


# ---------------------------------------------------------------------------
# Feature
# ---------------------------------------------------------------------------


class TestFeature:
    def test_enable(self):
        f = Feature("+kern")
        assert f.tag == "kern"
        assert f.value == 1

    def test_disable(self):
        f = Feature("-liga")
        assert f.tag == "liga"
        assert f.value == 0

    def test_with_value(self):
        f = Feature("kern=2")
        assert f.tag == "kern"
        assert f.value == 2

    def test_with_range(self):
        f = Feature("kern[3:5]=2")
        assert f.tag == "kern"
        assert f.start == 3
        assert f.end == 5
        assert f.value == 2

    def test_global_range(self):
        f = Feature("+kern")
        assert f.start == 0
        assert f.end == 2**32 - 1

    def test_str_enabled(self):
        assert str(Feature("+kern")) == "+kern"

    def test_str_disabled(self):
        assert str(Feature("-liga")) == "-liga"

    def test_repr(self):
        assert repr(Feature("+kern")) == 'Feature("+kern")'

    def test_equality(self):
        assert Feature("+kern") == Feature("+kern")
        assert Feature("+kern") != Feature("-kern")

    def test_hash(self):
        s = {Feature("+kern"), Feature("-liga"), Feature("+kern")}
        assert len(s) == 2

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid feature"):
            Feature("")


# ---------------------------------------------------------------------------
# Variation
# ---------------------------------------------------------------------------


class TestVariation:
    def test_basic(self):
        v = Variation("wght=700")
        assert v.tag == "wght"
        assert v.value == 700.0

    def test_float_value(self):
        v = Variation("wdth=85.5")
        assert v.tag == "wdth"
        assert abs(v.value - 85.5) < 0.01

    def test_str(self):
        v = Variation("wght=700")
        assert "wght" in str(v)
        assert "700" in str(v)

    def test_repr(self):
        v = Variation("wght=700")
        assert "wght" in repr(v)
        assert "700" in repr(v)

    def test_equality(self):
        assert Variation("wght=700") == Variation("wght=700")
        assert Variation("wght=700") != Variation("wght=400")

    def test_not_hashable(self):
        with pytest.raises(TypeError, match="unhashable"):
            hash(Variation("wght=700"))

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid variation"):
            Variation("")
