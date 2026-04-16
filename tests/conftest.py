import os
import re

import pytest

BUNDLED_DATA = os.path.join(os.path.dirname(__file__), "data")
BUNDLED_FONTS = os.path.join(os.path.dirname(__file__), "fonts")
HARFRUST_SOURCE = os.environ.get("HARFRUST_SOURCE")

MIN_EXTERNAL_CASES = 5000

_RS_TEST_RE = re.compile(
    r"shape\(\s*"
    r'"((?:\\.|[^"\\])*)"\s*,\s*'
    r'"((?:\\.|[^"\\])*)"\s*,\s*'
    r'"((?:\\.|[^"\\])*)"\s*,?\s*'
    r"\)\s*,\s*"
    r'"((?:\\.|[^"\\])*)"',
    re.DOTALL,
)
_RS_U_ESC = re.compile(r"\\u\{([0-9A-Fa-f]+)\}")
_RS_LINE_CONT = re.compile(r"\\\n\s*")


def parse_tests_file(path):
    """Parse a harfbuzz-format .tests file into test cases."""
    tests_dir = os.path.dirname(path)
    cases = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("@"):
                continue
            parts = line.split(";")
            if len(parts) != 4:
                continue
            fontfile, options, unicodes, expected = parts
            if expected == "*" or not expected:
                continue
            font_path = os.path.normpath(os.path.join(tests_dir, fontfile))
            if not os.path.exists(font_path):
                continue
            text = "".join(
                chr(int(u.strip()[2:], 16)) for u in unicodes.split(",") if u.strip()
            )
            cases.append((font_path, text, options, expected))
    return cases


def parse_rs_file(path, font_root):
    """Extract test cases from a harfrust-generated tests/shaping/*.rs file.

    Font paths inside the file are relative to the harfrust crate root
    (e.g. "tests/fonts/in-house/X.ttf"); ``font_root`` is that root.
    """
    cases = []
    with open(path) as f:
        content = f.read()
    for font_rel, text_lit, options, expected in _RS_TEST_RE.findall(content):
        text = _RS_LINE_CONT.sub("", text_lit)
        text = _RS_U_ESC.sub(lambda m: chr(int(m.group(1), 16)), text)
        font_path = os.path.normpath(os.path.join(font_root, font_rel))
        if not os.path.exists(font_path):
            continue
        cases.append((font_path, text, options, expected))
    return cases


def collect_tests_files():
    """Yield (case, is_external) pairs for every bundled and external test case."""
    cases = []
    if os.path.isdir(BUNDLED_DATA):
        for f in sorted(os.listdir(BUNDLED_DATA)):
            if f.endswith(".tests"):
                for case in parse_tests_file(os.path.join(BUNDLED_DATA, f)):
                    cases.append((case, False))
    if HARFRUST_SOURCE:
        external_cases = _collect_external_cases(HARFRUST_SOURCE)
        if len(external_cases) < MIN_EXTERNAL_CASES:
            raise RuntimeError(
                f"HARFRUST_SOURCE is set to {HARFRUST_SOURCE!r} but only "
                f"{len(external_cases)} Tier 2 cases were discovered "
                f"(expected at least {MIN_EXTERNAL_CASES}). "
                "Either the checkout is missing tests/shaping/*.rs or the parser "
                "is out of sync with harfrust's test generator."
            )
        cases.extend((c, True) for c in external_cases)
    return cases


def _collect_external_cases(harfrust_source: str):
    cases = []
    harfrust_root = os.path.join(harfrust_source, "harfrust")
    shaping_dir = os.path.join(harfrust_root, "tests", "shaping")
    if os.path.isdir(shaping_dir):
        for f in sorted(os.listdir(shaping_dir)):
            if f.endswith(".rs") and f != "main.rs":
                cases.extend(parse_rs_file(os.path.join(shaping_dir, f), harfrust_root))
    custom_dir = os.path.join(harfrust_root, "tests", "custom")
    if os.path.isdir(custom_dir):
        for f in sorted(os.listdir(custom_dir)):
            if f.endswith(".tests"):
                cases.extend(parse_tests_file(os.path.join(custom_dir, f)))
    return cases


def pytest_generate_tests(metafunc):
    if "tests_case" in metafunc.fixturenames:
        params = [
            pytest.param(
                case,
                marks=(pytest.mark.external,) if is_external else (),
                id=f"{os.path.basename(case[0])}:{case[1][:20]}",
            )
            for case, is_external in collect_tests_files()
        ]
        metafunc.parametrize("tests_case", params)
