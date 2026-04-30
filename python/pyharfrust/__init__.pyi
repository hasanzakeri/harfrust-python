from collections.abc import Iterator, Sequence
from typing import ClassVar, final

__version__: str

# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------

@final
class Direction:
    """Text direction: left-to-right, right-to-left, top-to-bottom, bottom-to-top."""

    LTR: ClassVar[Direction]
    RTL: ClassVar[Direction]
    TTB: ClassVar[Direction]
    BTT: ClassVar[Direction]

    def __init__(self, s: str) -> None:
        """Parse a direction string ("ltr", "rtl", "ttb", "btt"; case-insensitive).

        Raises ``ValueError`` on an unknown string.
        """

    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

@final
class Script:
    """An ISO 15924 script tag (e.g. "Latn", "Arab", "Deva")."""

    def __init__(self, s: str) -> None:
        """Construct from a 4-letter ISO 15924 tag.

        Raises ``ValueError`` if the input is not 4 ASCII letters.
        """

    @property
    def tag(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

@final
class Language:
    """A BCP 47 language tag (e.g. "en", "ar", "en-US")."""

    def __init__(self, s: str) -> None:
        """Parse a BCP 47 language tag. Raises ``ValueError`` on empty input."""

    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

@final
class Feature:
    """An OpenType feature setting (e.g. "+kern", "-liga", "kern[3:5]=2")."""

    def __init__(self, s: str) -> None:
        """Parse a feature string. Raises ``ValueError`` on invalid syntax."""

    @property
    def tag(self) -> str: ...
    @property
    def value(self) -> int: ...
    @property
    def start(self) -> int: ...
    @property
    def end(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

@final
class Variation:
    """A font variation axis setting (e.g. "wght=700", "wdth=85.5").

    Not hashable: variation values are floats.
    """

    def __init__(self, s: str) -> None:
        """Parse a variation string. Raises ``ValueError`` on invalid syntax."""

    @property
    def tag(self) -> str: ...
    @property
    def value(self) -> float: ...
    def __eq__(self, other: object) -> bool: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

# ---------------------------------------------------------------------------
# Buffer
# ---------------------------------------------------------------------------

@final
class Buffer:
    """Mutable text buffer used as input to shaping.

    A ``Buffer`` is consumed when passed to :meth:`Font.shape` — any further
    use raises ``ValueError``. Reuse a buffer by recycling it through
    :meth:`GlyphBuffer.clear`.
    """

    def __init__(self) -> None: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def add_str(self, s: str) -> None:
        """Append a Unicode string to the buffer."""

    def add(self, codepoint: int, cluster: int = 0) -> None:
        """Append a single Unicode codepoint with an explicit cluster value."""

    def clear(self) -> None:
        """Drop all codepoints and reset segment properties."""

    def reset_clusters(self) -> None:
        """Reset cluster values to be sequential (0, 1, 2, ...)."""

    def guess_segment_properties(self) -> None:
        """Guess direction, script, and language from the buffer contents."""

    def reserve(self, size: int) -> bool:
        """Reserve capacity for at least ``size`` items."""

    def set_pre_context(self, s: str) -> None:
        """Set context preceding the buffer for shaping decisions."""

    def set_post_context(self, s: str) -> None:
        """Set context following the buffer for shaping decisions."""

    def set_not_found_variation_selector_glyph(self, glyph: int) -> None:
        """Set the glyph emitted for a variation selector with no match."""

    @property
    def direction(self) -> Direction: ...
    @direction.setter
    def direction(self, value: Direction) -> None: ...
    @property
    def script(self) -> Script: ...
    @script.setter
    def script(self, value: Script) -> None: ...
    @property
    def language(self) -> Language | None: ...
    @language.setter
    def language(self, value: Language) -> None: ...

# ---------------------------------------------------------------------------
# Glyphs
# ---------------------------------------------------------------------------

@final
class GlyphInfo:
    """Read-only information about a shaped glyph.

    Snapshot value type: properties reflect the underlying glyph at the time
    the info was retrieved from a :class:`GlyphBuffer`.
    """

    @property
    def glyph_id(self) -> int: ...
    @property
    def cluster(self) -> int: ...
    @property
    def unsafe_to_break(self) -> bool: ...
    @property
    def unsafe_to_concat(self) -> bool: ...
    @property
    def safe_to_insert_tatweel(self) -> bool: ...
    def __repr__(self) -> str: ...

@final
class GlyphPosition:
    """Read-only positioning information for a shaped glyph (font units)."""

    @property
    def x_advance(self) -> int: ...
    @property
    def y_advance(self) -> int: ...
    @property
    def x_offset(self) -> int: ...
    @property
    def y_offset(self) -> int: ...
    def __repr__(self) -> str: ...

@final
class GlyphBuffer:
    """Output of :meth:`Font.shape`: a sequence of glyphs and their positions.

    Iterating yields ``(GlyphInfo, GlyphPosition)`` pairs. The buffer is
    consumed by :meth:`clear`, which returns a recycled :class:`Buffer`.
    """

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> tuple[GlyphInfo, GlyphPosition]: ...
    def __iter__(self) -> Iterator[tuple[GlyphInfo, GlyphPosition]]: ...
    def __repr__(self) -> str: ...
    @property
    def glyph_infos(self) -> list[GlyphInfo]: ...
    @property
    def glyph_positions(self) -> list[GlyphPosition]: ...
    def clear(self) -> Buffer:
        """Consume this glyph buffer and return its underlying buffer for reuse."""

    def serialize(self, font: Font) -> str:
        """Format the shaped glyphs as a string matching ``shape()`` output."""

# ---------------------------------------------------------------------------
# Font
# ---------------------------------------------------------------------------

@final
class Font:
    """A loaded font face used for shaping.

    Owns the font bytes and shaping data. Variations and point size can be
    adjusted between shape calls.
    """

    def __init__(self, path: str, face_index: int = 0) -> None:
        """Load a font from the filesystem.

        Raises ``RuntimeError`` if the file cannot be read or parsed.
        """

    @staticmethod
    def from_bytes(data: bytes, face_index: int = 0) -> Font:
        """Load a font from in-memory bytes.

        Raises ``RuntimeError`` if the data cannot be parsed as a font.
        """

    @property
    def face_index(self) -> int: ...
    @property
    def units_per_em(self) -> int: ...
    def set_variations(self, variations: Sequence[Variation] | str) -> None:
        """Set the active variation axes. An empty sequence resets to defaults.

        Raises ``ValueError`` if a string contains an unparseable variation,
        or ``TypeError`` if the argument is neither a string nor a sequence
        of :class:`Variation` objects.
        """

    def set_point_size(self, size: float | None) -> None:
        """Set the active point size, or clear it with ``None``."""

    def shape(
        self,
        buffer: Buffer,
        features: Sequence[Feature] | str | None = None,
    ) -> GlyphBuffer:
        """Shape the given buffer.

        Consumes the buffer; subsequent use of the same buffer raises
        ``ValueError``. Direction must be set on the buffer (typically via
        :meth:`Buffer.guess_segment_properties`) — otherwise raises
        ``ValueError``.

        Raises ``ValueError`` on invalid feature syntax, or ``TypeError`` if
        ``features`` is not a string, sequence of :class:`Feature`, or ``None``.
        """

    def __repr__(self) -> str: ...

# ---------------------------------------------------------------------------
# High-level functions
# ---------------------------------------------------------------------------

def shape(font_path: str, text: str, options: str = "") -> str:
    """Shape ``text`` with the font at ``font_path`` and return the serialized output.

    ``options`` accepts the same flags as the ``hb-shape`` CLI (e.g.
    ``"--direction=rtl"``, ``"--features=+kern,-liga"``).

    Raises ``RuntimeError`` if the font cannot be loaded or the options are
    invalid.
    """

def run_from_args(args: Sequence[str]) -> str:
    """Run the equivalent of the ``hb-shape`` CLI with ``args``.

    Raises ``RuntimeError`` if argument parsing or shaping fails.
    """
