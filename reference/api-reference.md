# Jumperless V5 MicroPython API Reference

This file summarizes the **MicroPython API** exposed by the `jumperless` module on the Jumperless V5. All functions and constants described here are available in the global namespace in the Micropython REPL; you do **not** need to import anything.

For full prose descriptions and examples, see the official docs at `https://docs.jumperless.org/09.5-micropythonAPIreference/`. This file is optimized for agents and quick lookup.

For progressive disclosure, prefer the split API files first:

- `reference/api/connections-routing.md`
- `reference/api/measurements-power.md`
- `reference/api/state-nets-filesystem.md`
- `reference/api/ui-interaction-system.md`

Use this monolithic file only when a task spans multiple API domains.

---

## Node addressing

You can specify nodes in three ways:

1. **By constant** — e.g. `D13`, `TOP_RAIL`, `GPIO_1`, `ADC0`, `ISENSE_PLUS`
2. **By string name** (case‑insensitive) — e.g. `"d13"`, `"top_rail"`, `"gpio_1"`
3. **By number** — breadboard rows `1`–`60`

Use constants or strings whenever possible for clarity. The full mapping of names to numeric IDs is documented in `reference/node-map.md`.

---

## Node connections

These functions manage the virtual “jumpers” on the crossbar.

### `connect(node1, node2, duplicates=-1)`

Create a bridge between two nodes.

- `duplicates=-1` (default): add a connection without changing existing paths.
- `duplicates=0`: ensure there are **no duplicate** parallel paths (keep exactly one).
- `duplicates=N>0`: force **exactly N** duplicates (add or remove as needed).

Examples:

```python
connect(1, 30)                 # connect breadboard rows 1 and 30
connect(D13, TOP_RAIL)         # tie Arduino D13 to the top rail
connect("GPIO_1", "ADC0")      # string names are allowed
```

### `disconnect(node1, node2)`

Remove a bridge between two nodes.

- If `node2 == -1`, remove **all** connections from `node1` to any nodes.

Examples:

```python
disconnect(1, 30)              # remove a specific bridge
disconnect(ADC0, -1)           # disconnect ADC0 from everything
```

### `fast_connect(node1, node2, duplicates=-1)`

Like `connect`, but skips LED/UI updates. Use this when rapidly building many connections.

### `fast_disconnect(node1, node2)`

Like `disconnect`, but without LED/UI updates.

### `is_connected(node1, node2)`

Return a `ConnectionState` object that is truthy when the nodes share a net.

```python
if is_connected(5, GND):
    print("Row 5 is on ground")
```

### `nodes_clear()`

Remove all connections (bridges) from the board.

---

## DAC (Digital-to-Analog Converter) and rails

The Jumperless has two DAC channels and two adjustable rails:

- `DAC0`, `DAC1` — dedicated DAC outputs
- `TOP_RAIL`, `BOTTOM_RAIL` — adjustable rails; the bottom rail can also be configured but is often used for GND.

### `dac_set(channel, voltage)`

Set the output voltage of a DAC or rail.

- `channel` — integer index (0–3) or a string/constant:
  - `0` / `DAC0` — DAC channel 0
  - `1` / `DAC1` — DAC channel 1
  - `2` / `TOP_RAIL`
  - `3` / `BOTTOM_RAIL`
- `voltage` — float in the range \[-8.0, +8.0] volts

```python
dac_set(1, 8.0)        # set DAC1 to +8.0 V
dac_set(0, -3.3)       # set DAC0 to -3.3 V
dac_set(TOP_RAIL, 3.3) # set top rail to +3.3 V
```

### `dac_get(channel)`

Return the configured voltage for a channel (not a live measurement).

```python
v = dac_get(1)
print("DAC1 setpoint:", v)
```

---

## ADC (Analog-to-Digital Converter)

The ADC channels measure voltages on dedicated measurement nodes.

Channels:

- `ADC0`–`ADC3` — ±8 V range
- `ADC4` — 5 V range
- `ADC7` / `PROBE` — special channel for the probe tip

### `adc_get(channel)`

Read an ADC channel and return a floating‑point voltage.

```python
connect(ADC0, 5)
v = adc_get(0)
print("Row 5 voltage:", v)
disconnect(ADC0, -1)
```

**Important:** Always connect the ADC node to a defined voltage (rail, DAC, or circuit node) before reading, or the input will float and produce unreliable values.

---

## INA current/power monitor

Two INA sensors measure current and power on key rails:

- Sensor 0 — typically associated with `DAC0` / probe supply
- Sensor 1 — typically associated with `TOP_RAIL`

### `ina_get_current(sensor)`

Return current in amps for the given sensor index (0 or 1).

### `ina_get_voltage(sensor)`

Return shunt voltage in volts.

### `ina_get_bus_voltage(sensor)`

Return bus voltage in volts.

### `ina_get_power(sensor)`

Return power in watts.

Example (current on TOP_RAIL):

```python
# assume sensor 1 monitors the top rail
top_i = ina_get_current(1)
top_v = ina_get_bus_voltage(1)
print("Top rail:", top_v, "V", top_i, "A")
```

---

## GPIO (RP2350B user pins) and UART

GPIO pins allow digital I/O from the RP2350B:

- `GPIO_1`–`GPIO_8` (user GPIOs)
- `UART_TX`, `UART_RX` — UART pins that also act as a routable serial passthrough

### `gpio_set(pin, value)`

Drive a GPIO pin high or low.

- `pin` — `GPIO_1`–`GPIO_8`, `"GPIO_1"`, or the corresponding numeric ID
- `value` — `HIGH`/`LOW` or `1`/`0`

```python
gpio_set(GPIO_1, HIGH)
gpio_set("GPIO_1", 0)
```

### `gpio_get(pin)`

Read the current digital state of a pin; returns a `GpioState` boolean‑like object.

```python
if gpio_get(GPIO_2):
    print("GPIO_2 is high")
```

### `gpio_set_dir(pin, direction)` / `gpio_get_dir(pin)`

Configure a pin as input or output.

- `direction` — `IN`/`OUT`, `GPIO_IN`/`GPIO_OUT`, or `0`/`1` depending on constants

```python
gpio_set_dir(GPIO_1, OUT)
gpio_set(GPIO_1, HIGH)
```

### `gpio_set_pull(pin, pull)` / `gpio_get_pull(pin)`

Configure internal pull‑up or pull‑down resistors.

- `pull` — `PULL_UP`, `PULL_DOWN`, or `PULL_NONE` (names may vary; see firmware)

### Additional helpers

The firmware also exposes helpers like:

- `gpio_set_floating_read(pin, floating_bool)` — control whether ADC‑based floating detection is used
- `gpio_claim_pin(pin)` / `gpio_release_pin(pin)` / `gpio_release_all_pins()` — for exclusive control and cleanup

See the C header in `modjumperless.c` or the main docs if you need these lower‑level functions.

---

## PWM

You can generate PWM signals on GPIO pins.

### `pwm(pin, frequency=None, duty=None)`

Configure a PWM channel on the given GPIO pin.

- `pin` — GPIO pin constant or string (e.g. `GPIO_1`)
- `frequency` — frequency in Hz (optional)
- `duty` — duty cycle as 0.0–1.0 (or percent 0–100, depending on implementation; check docs)

### `pwm_set_duty_cycle(pin, duty)`

Update the duty cycle while keeping the same frequency.

### `pwm_set_frequency(pin, freq)`

Update the frequency while keeping the same duty cycle.

### `pwm_stop(pin)`

Stop PWM on the given pin.

---

## Nets, paths, and state

### `get_state()`

Return a JSON string describing the **entire board state**, including:

- Power (rails and DAC voltages)
- Nets and their member nodes
- Bridges array
- GPIO configuration and readings
- Active overlays and colors

### `set_state(json_str, clear_first=True, from_wokwi=False)`

Apply a new state to the board.

- `clear_first=True` — clear existing connections before applying the new ones
- `from_wokwi=True` — interpret `json_str` as a Wokwi `diagram.json` and convert it

The agent should generally:

```python
saved = get_state()
# ... modify state locally ...
set_state(saved)
```

See `reference/state-format.md` for the shape of this JSON.

### Net information

- `get_num_nets()` — number of nets
- `get_net_info(net_idx)` — dict with details about a net (name, nodes, color, etc.)
- `get_net_nodes(net_idx)` — comma‑separated node list
- `get_num_bridges()` — count of bridges
- `get_bridge(bridge_idx)` — tuple `(node1, node2, duplicates)`

### Path query API

These functions describe internal routing paths through the crossbar:

- `get_num_paths(include_duplicates=False)` — number of routing paths
- `get_path_info(path_idx)` — dict with detailed info
- `get_all_paths()` — list of all path dicts
- `get_path_between(node1, node2)` — info for the path connecting two nodes, if any

---

## JFS: Jumperless File System

The Jumperless V5 exposes a virtual filesystem (`JFS`) accessible from MicroPython.

File‑like functions:

- `jfs.open(path, mode)` — open a file, returns a file handle
- `jfs.read(file, size=1024)` — read bytes/text
- `jfs.write(file, data)` — write bytes/text
- `jfs.close(file)` — close handle
- `jfs.seek(file, position, whence=0)` — move file pointer
- `jfs.tell(file)` — current offset
- `jfs.size(file)` — size in bytes
- `jfs.available(file)` — bytes available to read

Filesystem‑level helpers:

- `jfs.exists(path)` — `True`/`False`
- `jfs.listdir(path)` — list of entries
- `jfs.mkdir(path)` / `jfs.rmdir(path)` — create/remove directory
- `jfs.remove(path)` — delete file
- `jfs.rename(from_path, to_path)` — rename/move
- `jfs.stat(path)` — status info
- `jfs.info()` — tuple `(total_bytes, used_bytes, free_bytes)`

File object convenience methods (on the returned file handle):

- `file.print(data)`
- `file.flush()`
- `file.position()`
- `file.name()`

---

## Status and debug output

These functions print diagnostics to the main serial port:

- `print_bridges()` — all bridges
- `print_paths()` — routing paths
- `print_crossbars()` — low‑level crossbar array
- `print_nets()` — current nets
- `print_chip_status()` — status of crossbar chips

Use them when measurements don’t match expectations; the agent can parse their textual output or ask the user to paste it back.

---

## OLED display

The top 128×32 OLED can mirror text and status:

- `oled_print("text")` — print text to OLED (and optionally serial, depending on config)
- `oled_clear()` — clear display
- `oled_connect()` / `oled_disconnect()` — (re)connect the OLED

Additional functions exist for fonts and bitmaps (see firmware docs) but are usually not required for basic agent tasks.

---

## Probe and clickwheel

These functions interact with the physical probe and rotary encoder:

- `probe_read_blocking()` — wait for probe touch (returns a node ID)
- `probe_read_nonblocking()` — return node ID or `-1` if no touch
- `get_button(blocking=True)` / `probe_button(blocking=True)` — button state
- `probe_button_blocking()` / `probe_button_nonblocking()` — more explicit variants
- `get_switch_position()` / `set_switch_position(pos)` / `check_switch_position()` — probe switch mode (measure/select)

Clickwheel:

- `clickwheel_get_position()` — raw position counter
- `clickwheel_reset_position()` — reset to 0
- `clickwheel_get_direction(consume=False)` — `NONE`/`UP`/`DOWN`
- `clickwheel_get_button()` — button state

For agent‑driven automation, these are mainly useful when guiding human interaction (“tap this pad now”), not for continuous control.

---

## Graphic overlays (breadboard LED control)

These functions control the RGB LEDs under each breadboard hole. The overlay system is documented in detail in `https://docs.jumperless.org/09.5-micropythonAPIreference/#graphic-overlays`.

### Coordinate system

- 5×60 logical canvas (with a visual gap between rows 5 and 6 like a normal breadboard)
- `row`/`y`: 1–10 (1–5 top half, 6–10 bottom half)
- `col`/`x`: 1–30

### `overlay_set(name, row, col, width, height, colors)`

Create or update a named overlay.

- `name` — overlay name string
- `row`, `col` — top‑left position
- `width`, `height` — dimensions
- `colors` — flat or nested list of 0xRRGGBB values
  - `0x000000` means “transparent” (let underlying net colors show)

### `overlay_clear(name)` / `overlay_clear_all()`

Remove one or all overlays.

### `overlay_shift(name, dRow, dCol)` / `overlay_place(name, row, col)`

Move overlays relative or to an absolute position.

### `overlay_set_pixel(row, col, color)`

Set a single pixel’s color.

### `overlay_count()` / `overlay_serialize()`

Inspect the number and details of active overlays.

Color brightness guidelines are in `reference/hardware-guide.md`. In general, prefer bright but not full‑scale colors (e.g. `0x2020FF` instead of `0x0000FF`, `0x404040` instead of `0xFFFFFF`).

---

## Misc/system functions

Useful utilities:

- `arduino_reset()` — pulse the Arduino Nano header reset
- `run_app("appName")` — run an onboard app
- `pause_core2(pause_bool)` — pause/resume background services
- `send_raw(chip, x, y, setOrClear)` — low‑level crossbar control (expert use only)
- `change_terminal_color(color_idx, flush=True)` / `cycle_term_color(reset=False, step=None, flush=True)` — terminal color effects
- `nodes_save(slot=None)` / `nodes_discard()` / `nodes_has_changes()` — save/discard connection changes
- `switch_slot(slot)` — switch between saved circuit “slots”
- `context_toggle()` / `context_get()` — switch between `python` and `global` connection contexts

These functions are rarely needed for basic measurement and wiring workflows, but they are available when more advanced behavior is required.

