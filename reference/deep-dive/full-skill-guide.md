# Jumperless V5 Full Skill Guide

This file preserves the expanded operating guidance that used to live in `SKILL.md`.
Keep `SKILL.md` concise for fast routing, and use this document when deeper context is needed.

## Use This File When

- You are extending or refactoring the skill.
- You need broad context across routing, measurement, overlays, and safety.
- Task-level references were not enough.

For normal execution tasks, start with:

- `reference/progressive-disclosure-map.md`
- `reference/repl-runtime-playbook.md`
- `reference/api/connections-routing.md`
- `reference/api/measurements-power.md`
- `reference/api/state-nets-filesystem.md`
- `reference/api/ui-interaction-system.md`

## What the skill does

Use Jumperless V5 as active hardware-in-the-loop infrastructure:

- Create/remove virtual jumpers.
- Set rails and DACs.
- Measure voltage/current/resistance.
- Control GPIO and PWM.
- Drive OLED and LED overlays.
- Inspect, edit, and re-apply full state.

Primary transport is MicroPython REPL on the dedicated CDC interface.

## Getting connected

### 1) Install dependency

```bash
pip install pyserial
```

### 2) Detect REPL port

```bash
python scripts/jumperless.py detect
```

Detection behavior:

- Uses VID/PID and naming heuristics first (`JLV5`, `Jumperless`, `1D50:ACAB`).
- Probes candidates by checking for REPL prompt behavior.
- Caches successful port for later calls.

Platform notes:

- macOS: usually `/dev/cu.usbmodemJLV5port5`.
- Linux: commonly `/dev/ttyACM2` for CDC index 2.
- Windows: COM port associated with `MI_04` (CDC index 2).

### 3) Execute commands

Prefer robust execution modes:

```bash
python scripts/jumperless.py exec "print('hello')"
python scripts/jumperless.py exec --file scripts/session.py
python scripts/jumperless.py exec --stdin < scripts/session.py
```

### 4) State I/O

```bash
python scripts/jumperless.py state
python scripts/jumperless.py exec "print(get_state())"
```

Use `get_state()` as baseline before large rewires or rail changes.

## Core MicroPython API quick reference

All of these are available in REPL global namespace.

### Connectivity

- `connect(node1, node2, duplicates=-1)`
- `disconnect(node1, node2)` (`node2=-1` disconnect all from `node1`)
- `fast_connect(...)`, `fast_disconnect(...)`
- `is_connected(node1, node2)`
- `nodes_clear()`

### Rails / DAC

- `dac_set(channel, voltage)` (DAC0/DAC1/TOP_RAIL/BOTTOM_RAIL)
- `dac_get(channel)`

### ADC / INA

- `adc_get(channel)` (`ADC0-3` +-8V, `ADC4` 5V-range, `ADC7` probe)
- `ina_get_current(sensor)`
- `ina_get_bus_voltage(sensor)`
- `ina_get_power(sensor)`

### GPIO / PWM

- `gpio_set(pin, value)`, `gpio_get(pin)`
- `gpio_set_dir(pin, direction)`
- `gpio_set_pull(pin, pull)`
- `pwm(...)`, `pwm_set_duty_cycle(...)`, `pwm_set_frequency(...)`, `pwm_stop(...)`

### State / nets / paths

- `get_state()`, `set_state(json_str, clear_first=True, from_wokwi=False)`
- `get_num_nets()`, `get_net_info(i)`, `get_net_nodes(i)`
- `get_num_paths(...)`, `get_path_info(i)`, `get_path_between(a, b)`

### Overlays / OLED

- `overlay_set(...)`, `overlay_clear(name)`, `overlay_clear_all()`
- `overlay_set_pixel(row, col, color)`
- `overlay_shift(...)`, `overlay_place(...)`, `overlay_serialize()`
- `oled_clear()`, `oled_print(text)`

See `reference/api-reference.md` for complete details.

## Safety levels

- `Beginner`: conservative, frequent snapshots, plain-language explanation.
- `Advanced`: faster iteration, still announces impactful changes.
- `God mode`: broad autonomy, documents assumptions before destructive changes.

Default to `Beginner` unless user context clearly supports more autonomy.

## Recommended measurement workflow

1. Clarify measurement goal and expected range.
2. Snapshot with `get_state()`.
3. Set up temporary measurement routing.
4. Apply rail/DAC settings.
5. Take and interpret readings.
6. Restore baseline when experiment is temporary.

### Voltage example

```python
connect(ADC0, 5)
print(adc_get(0))
disconnect(ADC0, -1)
```

### Current example

```python
connect(ISENSE_PLUS, node_high)
connect(ISENSE_MINUS, node_low)
print(ina_get_current(0))
```

### Resistance (DAC + INA)

```python
connect(ISENSE_PLUS, DAC1)
connect(ISENSE_MINUS, 5)
dac_set(1, 3.0)
v = ina_get_bus_voltage(1)
i = ina_get_current(1)
print(v / i if i else "inf")
```

Account for routing/shunt effects when interpreting results.

## LED overlay usage

Canvas is 5x60 equivalent across breadboard halves (with center gap semantics).

Guidelines:

- Avoid full-white `0xFFFFFF`.
- Prefer reduced-brightness saturated colors (`0x2020FF`, `0x20FF20`, `0xFF2020`).
- Use `0x000000` as transparent in overlays.
- Favor subtle pulsing/motion over harsh flashing.

Use `scripts/animations.py` helpers for common guidance patterns.

## Important gotchas

- Crossbar path has non-trivial resistance; loaded voltages can sag.
- `ISENSE_PLUS` and `ISENSE_MINUS` are ends of a 2 ohm shunt; use in series.
- Internal state does not include user-added external wires/components.
- Context behavior matters (`python` vs `global`) for persistence.

## Human-in-the-loop step execution

For guided assembly/test flows:

```bash
python scripts/jumperless.py guide --file tests/steps_555.txt
```

- One step per line.
- Terminal + OLED prompt each step.
- Continue with `probe_button(True)` or clickwheel button fallback.

## Where to go deeper

- API details: `reference/api-reference.md`
- Node map: `reference/node-map.md`
- Hardware limits and behavior: `reference/hardware-guide.md`
- State schema and patterns: `reference/state-format.md`
- Long-term design context: `reference/vision.md`
- Worked examples: `examples/`
