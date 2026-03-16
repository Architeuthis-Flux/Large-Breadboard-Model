"""
Device-side LED overlay animations for Jumperless V5.

Upload this file to the Jumperless filesystem (for example as
`/python_scripts/lib/animations.py`), then import it:

    from animations import *

All functions use the `overlay_*` APIs provided by the Jumperless
MicroPython module and assume a 5x60 LED canvas (rows 1-10, cols 1-30).
"""

try:
    import time
except ImportError:
    time = None  # timing is optional; caller can handle loops


def _clamp_row(row):
    return max(1, min(10, int(row)))


def _clamp_col(col):
    return max(1, min(30, int(col)))


def _color_to_int(color):
    """Accept either 0xRRGGBB int or 'RRGGBB' string and return int."""
    if isinstance(color, int):
        return color & 0xFFFFFF
    if isinstance(color, str):
        try:
            return int(color, 16) & 0xFFFFFF
        except Exception:
            return 0
    return 0


def highlight_row(name, row, color=0x2020FF):
    """
    Create a static overlay that highlights a single row.

    Args:
        name: Overlay name (string).
        row: Row index (1-10).
        color: 0xRRGGBB color, kept at safe brightness by caller.
    """
    row = _clamp_row(row)
    color_hex = "%%06X" % _color_to_int(color)
    colors = [color_hex] * (30 * 1)
    overlay_set(name, row, 1, 30, 1, colors)


def highlight_range(name, start_row, end_row, color=0x20FF20):
    """
    Highlight a vertical strip of rows with a single color.

    Args:
        name: Overlay name.
        start_row: First row (inclusive).
        end_row: Last row (inclusive).
        color: 0xRRGGBB color.
    """
    r1 = _clamp_row(start_row)
    r2 = _clamp_row(end_row)
    if r2 < r1:
        r1, r2 = r2, r1
    height = r2 - r1 + 1
    color_hex = "%%06X" % _color_to_int(color)
    colors = [color_hex] * (30 * height)
    overlay_set(name, r1, 1, 30, height, colors)


def place_here(name, row, col, color=0xFF2020):
    """
    Mark a single LED at (row, col) with a bright but not full-scale color.

    Args:
        name: Overlay name.
        row: Row index (1-10).
        col: Column index (1-30).
        color: 0xRRGGBB color.
    """
    row = _clamp_row(row)
    col = _clamp_col(col)
    color_hex = "%%06X" % _color_to_int(color)
    overlay_set(name, row, col, 1, 1, [color_hex])


def arrow_between(name, from_row, to_row, color=0x20FFFF):
    """
    Draw a simple vertical arrow between two rows, centered horizontally.

    This is a static pattern; callers can move it over time using
    overlay_place or overlay_shift to animate.
    """
    r1 = _clamp_row(from_row)
    r2 = _clamp_row(to_row)
    if r2 < r1:
        r1, r2 = r2, r1
    height = r2 - r1 + 1
    mid_col = 15
    color_hex = "%%06X" % _color_to_int(color)
    colors = []
    for _ in range(height):
        for c in range(1, 31):
            if c == mid_col:
                colors.append(color_hex)
            else:
                colors.append("000000")
    overlay_set(name, r1, 1, 30, height, colors)


def pulse_row(name, row, base_color=0x2020FF, steps=10, delay_s=0.15):
    """
    Simple in-place pulsing effect for a row.

    This function blocks while running; call it from a dedicated
    measurement / guidance script if you need continuous animation.
    """
    if time is None:
        # Fallback: static highlight if time module is unavailable
        highlight_row(name, row, base_color)
        return

    row = _clamp_row(row)
    r = (base_color >> 16) & 0xFF
    g = (base_color >> 8) & 0xFF
    b = base_color & 0xFF

    for i in range(steps):
        # Triangle wave between ~25% and ~100% of base color
        if i < steps // 2:
            frac = 0.25 + 0.75 * (float(i) / float(steps // 2))
        else:
            frac = 0.25 + 0.75 * (float(steps - 1 - i) / float(steps // 2))
        cr = int(r * frac) & 0xFF
        cg = int(g * frac) & 0xFF
        cb = int(b * frac) & 0xFF
        color = (cr << 16) | (cg << 8) | cb
        highlight_row(name, row, color)
        time.sleep(delay_s)

