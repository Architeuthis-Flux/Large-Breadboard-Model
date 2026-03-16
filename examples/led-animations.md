# Example: Using LED Overlays and Animations

This example shows how to use the `animations.py` helper library to guide users visually on the Jumperless V5 breadboard.

## Prerequisites

- The `animations.py` module has been uploaded to the Jumperless filesystem, e.g. as `lib/animations.py`.
- The host can execute MicroPython snippets via the REPL.

## 1. Highlighting a row

To statically highlight row 10:

```python
from animations import highlight_row

highlight_row("row10_highlight", 10, color=0x2020FF)
```

This overlays a blue (but not full‑scale) bar across row 10. The color is chosen to be bright yet comfortable.

To clear it:

```python
overlay_clear("row10_highlight")
```

## 2. Pulsing a row

To create a simple breathing effect on row 5:

```python
from animations import pulse_row

pulse_row("row5_pulse", 5, base_color=0x20FF20, steps=20, delay_s=0.15)
```

This function:

- Repeats 20 steps where the brightness smoothly ramps up and down.
- Uses `delay_s` between frames (150 ms by default).
- Keeps colors within a safe brightness envelope.

Note: `pulse_row` is blocking; call it from a dedicated script if you want continuous animation while the user watches.

## 3. “Place component here” indicator

To mark a specific hole (row 3, column 10) where the user should place a component:

```python
from animations import place_here

place_here("place_here_R1", 3, 10, color=0xFF2020)
```

This sets a single bright red LED at the target location. You can pair this visual cue with textual instructions sent over serial or to the OLED, for example:

```python
oled_clear()
oled_print("Place R1 at row 3, col 10")
```

## 4. Drawing an arrow between rows

To show the direction between two important rows (e.g. 8 → 20):

```python
from animations import arrow_between

arrow_between("arrow_8_to_20", 8, 20, color=0x20FFFF)
```

This draws a vertical cyan arrow centered horizontally, spanning from row 8 to row 20.

To animate motion, you can move the overlay over time with MicroPython:

```python
import time

for offset in range(0, 5):
    overlay_place("arrow_8_to_20", 8 + offset, 1)
    time.sleep(0.15)
```

The agent can generate similar small loops to create motion while keeping refresh intervals gentle (~150 ms).

## 5. Combining overlays with net colors

Remember:

- Overlays are drawn **on top of** the firmware’s own net visualizations.
- Pixels colored `"000000"` in an overlay are transparent.

This means you can:

- Use overlays sparingly to augment, not replace, net colors.
- Draw borders, cursors, or indicators while keeping net wiring visible underneath.

If an overlay becomes visually cluttered, you can clear it:

```python
overlay_clear_all()
```

…or clear just the specific named overlays you created.

