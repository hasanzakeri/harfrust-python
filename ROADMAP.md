# Development Plan

## Phase 1 — Project Skeleton

Buildable Python package that imports successfully. Set up `Cargo.toml` (PyO3 cdylib), `pyproject.toml` (maturin backend), a minimal `src/lib.rs` with a version function, and `python/pyharfrust/__init__.py` that re-exports it. Include an MIT `LICENSE` file and a GitHub Actions CI workflow (`maturin develop` + `pytest`).

**Done when:** `maturin develop && pytest` passes with a single `test_import` test, LICENSE exists, and CI is green.

## Phase 2 — Value Types

Expose `Direction`, `Script`, `Language`, `Feature`, and `Variation` as Python classes. Each wraps the corresponding harfrust type and uses its `FromStr` impl for string-based construction (e.g. `Direction("rtl")`, `Feature("+kern")`, `Variation("wght=700")`).

**Done when:** types can be constructed, compared, stringified, and their properties accessed from Python.

## Phase 3 — High-Level `shape()` Function

Wrap `hr_shape::shape()` and `hr_shape::run_from_args()` as top-level Python functions. Set up a `.tests` regression suite with bundled test fonts and data, plus optional discovery of an external harfrust checkout via `HARFRUST_SOURCE`.

**Done when:** `pyharfrust.shape(font_path, text, options)` returns a serialized glyph string and bundled `.tests` cases pass.

## Phase 4 — Buffer Class

Expose `UnicodeBuffer` as a Python `Buffer` class with `add_str()`, direction/script/language properties, `guess_segment_properties()`, and `len()`. Uses `Option<UnicodeBuffer>` internally to track consumption by `shape()`.

**Done when:** buffers can be created, populated, configured, and passed to shaping.

## Phase 5 — Font Class and Object-Level Shaping

Full object API: `Font` (owned-container pattern), `GlyphBuffer`, `GlyphInfo`, `GlyphPosition`. Supports loading from file or bytes, setting variations and point size, shaping a buffer, iterating results, serializing output, and recycling buffers via `GlyphBuffer.clear()`.

**Done when:** the object API produces output identical to the `shape()` string function, and buffer consumption/recycling works correctly.

## Phase 6 — Type Stubs, Polish, and Packaging

Add PEP 561 type stubs (`__init__.pyi`, `py.typed`) and expand the README with usage examples and installation instructions.

**Done when:** the package is publishable with full IDE autocomplete support.

## Phase 7 — shapecmp Test Harness

Separate pure-Python project (`shapecmp-python/`) that compares harfrust vs harfbuzz shaping output across font/text corpora. Includes a CLI for single comparisons, batch `.tests` runs, corpus sweeps, failure minimization, and `.tests` file emission.

**Done when:** `shapecmp run-tests` can execute HarfBuzz `.tests` files against both engines and report differences.
