import os

import pytest

import pyharfrust

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
FONT = os.path.join(FONTS, "PT_Sans-Caption-Web-Regular.ttf")


class TestShapeBasic:
    def test_shape_returns_string(self):
        result = pyharfrust.shape(FONT, "AB", "")
        assert isinstance(result, str)
        assert result.startswith("[") and result.endswith("]")

    def test_shape_hello(self):
        result = pyharfrust.shape(FONT, "Hello", "")
        assert result == "[H=0+733|e=1+598|l=2+336|l=3+336|o=4+631]"

    def test_shape_direction_rtl(self):
        result = pyharfrust.shape(FONT, "AB", "--direction rtl")
        assert result == "[B=1+641|A=0+645]"

    def test_shape_empty_options(self):
        result = pyharfrust.shape(FONT, "A", "")
        assert "A=0" in result

    def test_shape_default_options(self):
        result = pyharfrust.shape(FONT, "A")
        assert "A=0" in result

    def test_shape_invalid_font(self):
        with pytest.raises(RuntimeError):
            pyharfrust.shape("/nonexistent/font.ttf", "A", "")


class TestRunFromArgs:
    def test_basic(self):
        result = pyharfrust.run_from_args(["--font-file", FONT, "--text", "Hello"])
        assert result == "[H=0+733|e=1+598|l=2+336|l=3+336|o=4+631]"

    def test_with_unicodes(self):
        result = pyharfrust.run_from_args(["--font-file", FONT, "-u", "U+0041,U+0042"])
        assert result == "[A=0+645|B=1+641]"

    def test_invalid_font(self):
        with pytest.raises(RuntimeError):
            pyharfrust.run_from_args(
                ["--font-file", "/nonexistent/font.ttf", "--text", "A"]
            )


class TestDotTestsRegression:
    def test_shape_matches_tests_file(self, tests_case):
        font_path, text, options, expected = tests_case
        result = pyharfrust.shape(font_path, text, options)
        assert result == expected
