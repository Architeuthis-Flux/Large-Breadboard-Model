# API: UI, Interaction, and System

Use this file for OLED, LED overlays, probe/clickwheel input, GPIO/PWM, and misc control.

## OLED

- `oled_print(text)`
- `oled_clear()`
- `oled_connect()`, `oled_disconnect()`

## LED Overlays

- `overlay_set(name, row, col, width, height, colors)`
- `overlay_clear(name)`, `overlay_clear_all()`
- `overlay_shift(name, dRow, dCol)`, `overlay_place(name, row, col)`
- `overlay_set_pixel(row, col, color)`
- `overlay_count()`, `overlay_serialize()`

Guidelines:

- Use reduced-brightness saturated colors.
- Avoid full `0xFFFFFF`.
- Use `0x000000` as transparent.

## Probe and Clickwheel

- `probe_read_blocking()`, `probe_read_nonblocking()`
- `probe_button(blocking=True)` and related variants
- `clickwheel_get_position()`, `clickwheel_reset_position()`
- `clickwheel_get_direction(consume=False)`, `clickwheel_get_button()`

Use these for human-in-the-loop step gating and guided workflows.

## GPIO and PWM

- `gpio_set(pin, value)`, `gpio_get(pin)`
- `gpio_set_dir(pin, direction)`, `gpio_get_dir(pin)`
- `gpio_set_pull(pin, pull)`, `gpio_get_pull(pin)`
- `pwm(pin, frequency=None, duty=None)`
- `pwm_set_duty_cycle(pin, duty)`, `pwm_set_frequency(pin, freq)`, `pwm_stop(pin)`

## Misc System Functions

- `arduino_reset()`
- `run_app("appName")`
- `pause_core2(pause_bool)`
- `send_raw(chip, x, y, setOrClear)` (expert only)

## Escalate To

- `scripts/animations.py` for reusable visual patterns.
- `reference/hardware-guide.md` for brightness and hardware behavior constraints.
