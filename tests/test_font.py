import os

import pytest

from pyharfrust import (
    Buffer,
    Feature,
    Font,
    GlyphBuffer,
    GlyphInfo,
    GlyphPosition,
    Variation,
    shape,
)

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
PT_SANS = os.path.join(FONTS_DIR, "PT_Sans-Caption-Web-Regular.ttf")
OPEN_SANS = os.path.join(FONTS_DIR, "OpenSans.subset1.ttf")


def _shape_str(font, text, features=None):
    buf = Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    return font.shape(buf, features) if features is not None else font.shape(buf)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_from_path(self):
        font = Font(PT_SANS)
        assert font.face_index == 0
        assert font.units_per_em > 0

    def test_face_index_kw(self):
        font = Font(PT_SANS, face_index=0)
        assert font.face_index == 0

    def test_missing_file_raises(self):
        with pytest.raises(RuntimeError):
            Font("/nonexistent/font.ttf")

    def test_from_bytes(self):
        with open(PT_SANS, "rb") as f:
            data = f.read()
        font = Font.from_bytes(data)
        assert font.units_per_em > 0

    def test_from_bytes_invalid(self):
        with pytest.raises(RuntimeError):
            Font.from_bytes(b"not a font file")


# ---------------------------------------------------------------------------
# Shaping basics
# ---------------------------------------------------------------------------


class TestShape:
    def test_returns_glyph_buffer(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "Hello")
        assert isinstance(gbuf, GlyphBuffer)
        assert len(gbuf) == 5

    def test_glyph_infos_and_positions(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "Hi")
        infos = gbuf.glyph_infos
        positions = gbuf.glyph_positions
        assert len(infos) == len(positions) == len(gbuf)
        assert all(isinstance(i, GlyphInfo) for i in infos)
        assert all(isinstance(p, GlyphPosition) for p in positions)

    def test_glyph_info_fields(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "AB")
        info = gbuf.glyph_infos[0]
        assert isinstance(info.glyph_id, int) and info.glyph_id > 0
        assert info.cluster == 0
        assert isinstance(info.unsafe_to_break, bool)
        assert isinstance(info.unsafe_to_concat, bool)
        assert isinstance(info.safe_to_insert_tatweel, bool)

    def test_glyph_position_fields(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "A")
        pos = gbuf.glyph_positions[0]
        assert pos.x_advance > 0
        assert pos.y_advance == 0
        assert isinstance(pos.x_offset, int)
        assert isinstance(pos.y_offset, int)


# ---------------------------------------------------------------------------
# Iteration / indexing
# ---------------------------------------------------------------------------


class TestIteration:
    def test_iter_yields_pairs(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "Hi")
        items = list(gbuf)
        assert len(items) == 2
        for info, pos in items:
            assert isinstance(info, GlyphInfo)
            assert isinstance(pos, GlyphPosition)

    def test_indexing(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "AB")
        first = gbuf[0]
        last = gbuf[-1]
        assert first[0].cluster == 0
        assert last[0].cluster == 1

    def test_index_out_of_range(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "A")
        with pytest.raises(IndexError):
            gbuf[5]


# ---------------------------------------------------------------------------
# Serialize parity with shape() string function
# ---------------------------------------------------------------------------


class TestSerializeParity:
    def test_matches_shape_string(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "Hello")
        obj_result = gbuf.serialize(font).strip()
        str_result = shape(PT_SANS, "Hello", "").strip()
        assert obj_result == str_result

    def test_matches_shape_with_features(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "AB", features=[Feature("+kern")])
        obj_result = gbuf.serialize(font).strip()
        str_result = shape(PT_SANS, "AB", "--features=+kern").strip()
        assert obj_result == str_result


# ---------------------------------------------------------------------------
# Buffer consumption + recycling
# ---------------------------------------------------------------------------


class TestBufferConsumption:
    def test_buffer_consumed_after_shape(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("Test")
        buf.guess_segment_properties()
        font.shape(buf)
        with pytest.raises(ValueError, match="consumed"):
            len(buf)

    def test_shape_twice_raises(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("Test")
        buf.guess_segment_properties()
        font.shape(buf)
        with pytest.raises(ValueError, match="consumed"):
            font.shape(buf)

    def test_shape_with_invalid_direction_raises(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("Test")  # direction left at default Invalid
        with pytest.raises(ValueError, match="direction"):
            font.shape(buf)


class TestBufferRecycle:
    def test_clear_returns_reusable_buffer(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("First")
        buf.guess_segment_properties()
        gbuf = font.shape(buf)
        buf2 = gbuf.clear()
        assert isinstance(buf2, Buffer)
        assert len(buf2) == 0
        buf2.add_str("Second")
        buf2.guess_segment_properties()
        gbuf2 = font.shape(buf2)
        assert len(gbuf2) == 6

    def test_glyph_buffer_consumed_after_clear(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("X")
        buf.guess_segment_properties()
        gbuf = font.shape(buf)
        gbuf.clear()
        with pytest.raises(ValueError, match="consumed"):
            len(gbuf)

    def test_clear_twice_raises(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("X")
        buf.guess_segment_properties()
        gbuf = font.shape(buf)
        gbuf.clear()
        with pytest.raises(ValueError, match="consumed"):
            gbuf.clear()


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------


class TestFeatures:
    def test_features_list(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "AB", features=[Feature("+kern")])
        assert len(gbuf) == 2

    def test_features_string(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "AB", features="+kern,-liga")
        assert len(gbuf) == 2

    def test_features_empty_list(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "AB", features=[])
        assert len(gbuf) == 2

    def test_features_invalid_string(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("AB")
        with pytest.raises(ValueError, match="invalid feature"):
            font.shape(buf, features="bogus[junk")

    def test_features_wrong_type(self):
        font = Font(PT_SANS)
        buf = Buffer()
        buf.add_str("AB")
        with pytest.raises(TypeError):
            font.shape(buf, features=42)


# ---------------------------------------------------------------------------
# Variations
# ---------------------------------------------------------------------------


class TestVariations:
    def test_set_variations_list(self):
        font = Font(OPEN_SANS)
        font.set_variations([Variation("wght=700")])

    def test_set_variations_string(self):
        font = Font(OPEN_SANS)
        font.set_variations("wght=500,wdth=80")

    def test_variations_affect_output(self):
        # OpenSans.subset1 is variable; weight should change x_advance.
        baseline = Font(OPEN_SANS)
        bold = Font(OPEN_SANS)
        bold.set_variations([Variation("wght=900")])

        a = _shape_str(baseline, "e").glyph_positions[0].x_advance
        b = _shape_str(bold, "e").glyph_positions[0].x_advance
        assert a != b

    def test_set_variations_empty_resets(self):
        font = Font(OPEN_SANS)
        font.set_variations([Variation("wght=900")])
        bold_adv = _shape_str(font, "e").glyph_positions[0].x_advance

        font.set_variations([])
        default_adv = _shape_str(font, "e").glyph_positions[0].x_advance
        assert default_adv != bold_adv

    def test_set_variations_invalid(self):
        font = Font(OPEN_SANS)
        with pytest.raises(ValueError, match="invalid variation"):
            font.set_variations("garbage~~~")

    def test_set_variations_wrong_type(self):
        font = Font(OPEN_SANS)
        with pytest.raises(TypeError):
            font.set_variations(42)


# ---------------------------------------------------------------------------
# Point size
# ---------------------------------------------------------------------------


class TestPointSize:
    def test_set_then_clear(self):
        font = Font(PT_SANS)
        font.set_point_size(12.0)
        font.set_point_size(None)

    def test_shape_runs_with_point_size(self):
        font = Font(PT_SANS)
        font.set_point_size(24.0)
        gbuf = _shape_str(font, "Hi")
        assert len(gbuf) == 2


# ---------------------------------------------------------------------------
# Repr
# ---------------------------------------------------------------------------


class TestRepr:
    def test_font_repr(self):
        font = Font(PT_SANS)
        assert "Font" in repr(font)

    def test_glyph_buffer_repr(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "Hi")
        r = repr(gbuf)
        assert "GlyphBuffer" in r and "2" in r

    def test_glyph_buffer_repr_after_clear(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "X")
        gbuf.clear()
        assert "consumed" in repr(gbuf)

    def test_glyph_info_repr(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "A")
        assert "GlyphInfo" in repr(gbuf.glyph_infos[0])

    def test_glyph_position_repr(self):
        font = Font(PT_SANS)
        gbuf = _shape_str(font, "A")
        assert "GlyphPosition" in repr(gbuf.glyph_positions[0])
