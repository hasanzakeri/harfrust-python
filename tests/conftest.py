import os

import pytest

BUNDLED_DATA = os.path.join(os.path.dirname(__file__), "data")
BUNDLED_FONTS = os.path.join(os.path.dirname(__file__), "fonts")
HARFRUST_SOURCE = os.environ.get("HARFRUST_SOURCE")


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


def collect_tests_files():
    """Yield (case, is_external) pairs for every bundled and external test case."""
    cases = []
    if os.path.isdir(BUNDLED_DATA):
        for f in sorted(os.listdir(BUNDLED_DATA)):
            if f.endswith(".tests"):
                for case in parse_tests_file(os.path.join(BUNDLED_DATA, f)):
                    cases.append((case, False))
    if HARFRUST_SOURCE:
        ext_tests = os.path.join(HARFRUST_SOURCE, "harfrust", "tests", "custom")
        if os.path.isdir(ext_tests):
            for f in sorted(os.listdir(ext_tests)):
                if f.endswith(".tests"):
                    for case in parse_tests_file(os.path.join(ext_tests, f)):
                        cases.append((case, True))
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
