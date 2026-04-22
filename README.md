# harfrust-python

Python bindings for [HarfRust](https://github.com/nickkuk/harfrust), a pure-Rust port of the [HarfBuzz](https://harfbuzz.github.io/) text shaping engine.

## What is text shaping?

Text shaping is the process of converting a sequence of Unicode codepoints into positioned glyphs — selecting the right glyph forms, applying ligatures, kerning, and reordering as required by the script. It is a critical step in any text rendering pipeline, especially for complex scripts like Arabic, Devanagari, and Thai.

HarfBuzz is the industry-standard text shaping engine used by Firefox, Chrome, Android, and many other platforms. HarfRust is a faithful pure-Rust port of HarfBuzz, and this project aims to make that engine accessible from Python.

## Goals

- **Standalone Python package** — a proper, independently usable Python library for text shaping, not just a test utility.
- **Two-tier API** — a high-level `shape()` function for quick one-shot shaping, and a lower-level object API (`Font`, `Buffer`, `GlyphBuffer`) for full control over the shaping pipeline.
- **Pythonic interface** — string-based construction for configuration types (`Direction("rtl")`, `Feature("+kern")`, `Variation("wght=700")`), iteration over glyph results, and clear error messages.
- **HarfBuzz test compatibility** — ability to run against HarfBuzz's `.tests` regression format, enabling direct comparison between the two engines.

## Technical Approach

- **PyO3 + maturin** — the standard modern toolchain for building Rust extensions for Python.
- **Owned-container pattern** — the Python `Font` object owns all its backing data, with transient Rust borrows scoped to individual method calls. This cleanly bridges Rust's lifetime system and Python's garbage-collected memory model.
- **Standalone project** — not a member of the harfrust Cargo workspace, allowing an independent release cadence and CI configuration.

## Status

This project is in early development. See the [development plan](https://github.com/nickkuk/harfrust-python/blob/main/ROADMAP.md) for the phased roadmap.

## License

MIT
