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

## Installation

Wheels are not yet published. To build from source you need a Rust toolchain (>= 1.85) and Python (>= 3.11):

```bash
git clone https://github.com/hasanzakeri/harfrust-python.git
cd harfrust-python
pip install maturin
maturin develop --release
```

The package is imported as `pyharfrust`:

```python
import pyharfrust
print(pyharfrust.__version__)
```

PEP 561 type stubs (`__init__.pyi`, `py.typed`) ship with the package, so editors and type checkers see the full API.

## Quick start

Two ways to shape a string. Both produce the same output.

### High-level `shape()` function

```python
from pyharfrust import shape

result = shape("path/to/font.ttf", "Hello World", "")
# "[H=0+733|e=1+598|l=2+336|l=3+336|o=4+631|space=5+272|W=6+871|o=7+631|r=8+380|l=9+336|d=10+629]"
```

The third argument accepts the same flags as the `hb-shape` CLI:

```python
shape("font.ttf", "AB", "--features=+kern,-liga --direction=ltr")
```

### Object API

For repeated shaping, font configuration, or access to per-glyph metadata, use the object API:

```python
from pyharfrust import Buffer, Feature, Font

font = Font("path/to/font.ttf")

buf = Buffer()
buf.add_str("Hello World")
buf.guess_segment_properties()  # infers direction/script/language

glyphs = font.shape(buf, features=[Feature("+kern")])

for info, pos in glyphs:
    print(f"glyph={info.glyph_id} cluster={info.cluster} "
          f"advance=({pos.x_advance},{pos.y_advance}) "
          f"offset=({pos.x_offset},{pos.y_offset})")
```

The `serialize()` method produces the same string format as the high-level `shape()` function:

```python
print(glyphs.serialize(font))
```

## Configuration types

All configuration types accept either a string or their structured form. Strings parse with the same syntax as `hb-shape`:

```python
from pyharfrust import Direction, Feature, Language, Script, Variation

Direction("ltr")          # or Direction.LTR
Script("Latn")            # 4-letter ISO 15924 tag
Language("en-US")
Feature("+kern")          # enable; "-liga" disables; "kern[3:5]=2" applies a range
Variation("wght=700")     # variable-font axis setting
```

## Variable fonts

```python
from pyharfrust import Font, Variation

font = Font("variable.ttf")
font.set_variations([Variation("wght=700"), Variation("wdth=85")])
# or
font.set_variations("wght=700,wdth=85")

# Reset to defaults:
font.set_variations([])
```

## Buffer recycling

Buffers are consumed by `shape()`. Recycle them via `GlyphBuffer.clear()`:

```python
from pyharfrust import Buffer, Font

font = Font("font.ttf")
buf = Buffer()
buf.add_str("First")
buf.guess_segment_properties()
glyphs = font.shape(buf)

# Reuse the same allocation for a new shaping call:
buf = glyphs.clear()
buf.add_str("Second")
buf.guess_segment_properties()
glyphs = font.shape(buf)
```

Reusing a consumed `Buffer` (or `GlyphBuffer`) raises `ValueError`.

## Errors

- `RuntimeError` — font cannot be loaded or parsed.
- `ValueError` — invalid string input (`Direction("xyz")`, `Feature("=")`), unset buffer direction at shape time, or use of an already-consumed buffer.
- `TypeError` — wrong argument types (e.g. assigning a string to `Buffer.direction`).

## Technical Approach

- **PyO3 + maturin** — the standard modern toolchain for building Rust extensions for Python.
- **Owned-container pattern** — the Python `Font` object owns all its backing data, with transient Rust borrows scoped to individual method calls. This cleanly bridges Rust's lifetime system and Python's garbage-collected memory model.
- **Standalone project** — not a member of the harfrust Cargo workspace, allowing an independent release cadence and CI configuration.

## Status

This project is in early development. See the [development plan](https://github.com/hasanzakeri/harfrust-python/blob/main/ROADMAP.md) for the phased roadmap.

## License

MIT
