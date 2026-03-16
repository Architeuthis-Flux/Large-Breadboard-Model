---
name: jumperless-v5
description: >-
  Control a Jumperless V5 breadboard for hardware-in-the-loop circuit prototyping
  and debugging. Connect/disconnect nodes, take voltage/current measurements, control
  DACs/GPIOs, display overlays on breadboard LEDs, and interact with the MicroPython
  REPL. Use when the user mentions Jumperless, breadboard wiring, circuit testing,
  hardware debugging, or measuring voltage/current/resistance on real hardware.
---

# Jumperless V5 Skill

## What this skill does

This skill teaches the agent how to use a **Jumperless V5** smart breadboard as a hardware extension: it can create and remove virtual jumpers, set power rails and DACs, read ADCs and current sensors, drive GPIOs, and render graphics on the 128×32 OLED and the RGB LEDs under every hole. All control happens through the **MicroPython REPL** running on the `JL Micropython REPL` USB CDC endpoint, using the `jumperless` module APIs that are already available in the global namespace.

Use this skill whenever the user wants to:
- Prototype or debug a circuit on a breadboard using real hardware
- Measure voltages, currents, or resistances on a physical circuit
- Guide a user step‑by‑step in wiring components on a Jumperless board
- Visualize instructions or circuit states using breadboard LED overlays

When unsure about a low‑level detail, prefer to **look it up** in the reference files instead of guessing.

## Getting connected

The recommended way to talk to the Jumperless V5 from a host computer is via the helper script in `scripts/jumperless.py`. This script uses `pyserial` and the raw MicroPython REPL protocol so the agent can reliably send commands and read outputs.

### 1. Install dependencies

On the host machine:

```bash
pip install pyserial
```

### 2. Detect the MicroPython REPL port

To find and cache the correct USB serial port:

```bash
python scripts/jumperless.py detect
```

The script will:
- Enumerate serial ports
- Prefer ports whose name or VID/PID look like a Jumperless (`JLV5`, `Jumperless`, VID `1D50`, PID `ACAB`)
- On macOS, prefer `/dev/cu.usbmodemJLV5port5` (the MicroPython REPL)
- On Linux, prefer the third `/dev/ttyACM*` device (CDC index 2)
- On Windows, prefer the COM port whose interface corresponds to CDC index 2 (MI_04)
- If needed, probe candidate ports by sending raw REPL control characters and checking for a `>>> ` prompt
- Cache the chosen port path in a `.jumperless_port` file for later use

If detection fails, the script prints clear instructions and asks the user to choose a port; the agent should then use that port path for subsequent commands.

### 3. Run a one‑off MicroPython command

You can execute a short MicroPython snippet on the Jumperless like this:

```bash
python scripts/jumperless.py exec "print('hello from jumperless')"
```

The `exec` subcommand:
- Uses the raw REPL protocol (`Ctrl-A` to enter, send code + `Ctrl-D` to run, read `OK`, capture stdout/stderr, `Ctrl-B` to exit)
- Prints the captured stdout to the host terminal
- Treats any stderr as an error the agent must handle and explain

For multi‑line scripts, the agent can either:
- Pass a `"; "`‑joined string to `exec`, or
- Ask the user to run `python scripts/jumperless.py exec -f my_script.py` if file‑based execution is supported by the helper script implementation.

### 4. Get and set full board state

The most powerful interface to the Jumperless is the **state API**:

- `get_state()` → returns a JSON string describing:
  - All rails, DACs, and their voltages
  - Nets, bridges, and node memberships
  - GPIO configuration and readings
  - Active overlays and colors
- `set_state(json_str, clear_first=True, from_wokwi=False)` → applies a complete state

Typical workflow:

```bash
# From the host, ask the device for state
python scripts/jumperless.py exec "import json; print(get_state())"
```

The agent should:
1. Parse the returned JSON into a data structure
2. Reason about connections, power rails, and GPIO states
3. Propose modifications by editing the JSON
4. Re‑serialize and apply with `set_state(...)`

Details of the JSON format are documented in `reference/state-format.md`.

## Quick reference: core MicroPython APIs

These functions are **already available globally** in the MicroPython REPL; no import is needed.

- **Connections**
  - `connect(node1, node2, duplicates=-1)` — create a bridge between two nodes
  - `disconnect(node1, node2)` — remove a specific bridge (`node2=-1` clears all from `node1`)
  - `fast_connect(node1, node2, duplicates=-1)` / `fast_disconnect(node1, node2)` — connect/disconnect without LED updates (faster sweeps)
  - `is_connected(node1, node2)` — returns a truthy `ConnectionState` object if nodes share a net
  - `nodes_clear()` — remove all bridges

- **Power and DAC**
  - `dac_set(channel, voltage)` — set DAC output or rail (channels 0–3 map to DAC0, DAC1, TOP_RAIL, BOTTOM_RAIL)
  - `dac_get(channel)` — read back the configured voltage

- **ADC and current sensing**
  - `adc_get(channel)` — measure voltage on ADC channel (0–3: ±8 V range, 4: 5 V‑limited, 7: probe)
  - `ina_get_current(sensor)` — current in amps (sensor 0 for DAC0/probe, 1 for TOP_RAIL)
  - `ina_get_bus_voltage(sensor)` — bus voltage in volts

- **GPIO and PWM**
  - `gpio_set(pin, value)` / `gpio_get(pin)` — drive or read GPIO_1–GPIO_8 or UART_TX/RX
  - `gpio_set_dir(pin, direction)` — configure input/output
  - `gpio_set_pull(pin, pull)` — configure pull‑up/down/none
  - `pwm(pin, frequency=None, duty=None)` — configure PWM on a GPIO pin
  - `pwm_set_duty_cycle(pin, duty)` / `pwm_set_frequency(pin, freq)` / `pwm_stop(pin)`

- **State and nets**
  - `get_state()` / `set_state(json_str, clear_first=True, from_wokwi=False)`
  - `get_num_nets()` / `get_net_info(net_idx)` / `get_net_nodes(net_idx)`
  - `get_num_paths(include_duplicates=False)` / `get_path_info(path_idx)` / `get_path_between(node1, node2)`

- **LED overlays**
  - `overlay_set(name, row, col, w, h, colors)` — define/update a named overlay
  - `overlay_clear(name)` / `overlay_clear_all()` — remove one or all overlays
  - `overlay_shift(name, dRow, dCol)` / `overlay_place(name, row, col)` — move an overlay
  - `overlay_set_pixel(row, col, color)` — set one LED pixel
  - `overlay_serialize()` — dump overlays as YAML

For the full API, the agent should consult `reference/api-reference.md`.

## Safety levels and risk management

The hardware is robust and protected against many mistakes (for example, `connect(TOP_RAIL, GND)` is ignored), but the board cannot see user‑placed **external wires and components**. A wire between rows 5 and 10 plus `TOP_RAIL→5` and `GND→10` still creates a real short.

The skill assumes three conceptual safety levels:

- **Beginner** — default. Behaviors:
  - Always take a `get_state()` snapshot before making structural changes
  - Avoid changing rails or DACs unless explicitly requested
  - Prefer `adc_get()` and INA measurements over aggressive rewiring
  - Explain what each connection does in plain language

- **Advanced** — user has some electronics experience. Behaviors:
  - Save state, then freely modify connections and rails
  - Use more complex measurement patterns (e.g. IV curves, resistance via DAC+INA)
  - Still warn before large changes (like clearing all nodes)

- **God mode** — user knows the risks and explicitly opts in. Behaviors:
  - Agent can restructure large parts of the circuit
  - Fewer confirmation prompts, but still documents assumptions

The agent should infer an initial level from the user’s language and prior interactions (e.g. whether they mention specific IC part numbers, pin names, or datasheet parameters) and adjust explanations accordingly. When in doubt, default to **Beginner** and ask for permission before clearing nets or changing rails.

## Measurement workflow (recommended pattern)

When asked to “measure X between Y and Z”, follow this pattern:

1. **Clarify the goal**
   - What quantity is being measured? (voltage, current, resistance, frequency)
   - What components are present and where are they on the breadboard?

2. **Capture current state**
   - Call `get_state()` and store the JSON string (either in a variable on device or in the host environment).

3. **Prepare connections**
   - For **voltage**: 
     - Connect the target node to an ADC channel (e.g. `connect(ADC0, 5)`), read with `adc_get(0)`, then `disconnect(ADC0, -1)` if it’s a temporary probe.
   - For **current**:
     - Insert the ISENSE shunt in series: `connect(ISENSE_PLUS, node_high)`, `connect(ISENSE_MINUS, node_low)`.
     - Read with `ina_get_current(0)` or `ina_get_current(1)` depending on which shunt is used.
   - For **resistance**:
     - Use DAC + INA: drive a known voltage across the unknown element, measure current, then compute `R = V / I`.

4. **Apply settings**
   - Set DAC or rail voltages using `dac_set(...)`.
   - Configure GPIOs or PWM if the circuit under test involves them.

5. **Measure and interpret**
   - Take multiple samples if noise is expected.
   - Compare the result against expected ranges from the component’s datasheet.
   - If a result is clearly wrong, inspect `get_state()`, `print_nets()`, or `get_net_info()` for wiring discrepancies.

6. **Restore or keep changes**
   - For temporary experiments, restore the saved JSON via `set_state(saved_json)`.
   - For permanent designs, either leave the new state in place or save it to a slot for later use.

Examples of these workflows are provided in `examples/measure-resistance.md` and `examples/circuit-debugging.md`.

## LED overlay system basics

The breadboard LEDs form a **5×60 grid** of addressable RGB pixels (with a 2‑hole gap between the two halves, like a normal breadboard):
- Rows 1–5: top half (above the center gap)
- Rows 6–10: bottom half (below the gap)
- Columns 1–30: along the length of the breadboard

Overlays are drawn **on top of** any wires or nets the firmware is already rendering. A color value of `0x000000` in an overlay means “transparent” (do not override the underlying visualization).

**Brightness rules:**
- LEDs are very bright. Avoid `0xFFFFFF`.
- Prefer saturated colors at reduced brightness:
  - Good examples: `0x2020FF`, `0x20FF20`, `0xFF2020`, `0x20FFFF`
  - For white, cap around `0x404040`
- When designing animations, favor **subtle pulsing or motion** over high brightness.

The `scripts/animations.py` library (uploaded to the device) provides reusable overlay patterns like:
- Row highlights
- Arrows between two rows
- “Place component here” indicators

The agent should use these helpers whenever possible instead of hand‑crafting color arrays, unless a highly custom effect is needed.

## Key gotchas to remember

- **Crossbar resistance**:
  - Each path through the CH446Q crossbar adds ~80 Ω of resistance.
  - The firmware automatically stacks parallel paths (per `[routing]` config), so effective resistance can drop to ~20 Ω on heavily used nets.
  - This means measured voltages under load will sag compared to ideal calculations; the agent should factor that into expectations.

- **ISENSE+ and ISENSE‑ are shorted internally**:
  - They are the two ends of a **2 Ω shunt resistor**.
  - They must be placed **in series** with the circuit being measured, not across a supply.
  - The board cannot tell when the user has miswired them off‑board; always cross‑check against the user’s description.

- **External wires and components are invisible**:
  - `get_state()` and the net/path APIs describe only **virtual** connections inside the crossbar.
  - Any actual wires, resistors, ICs, or modules on the breadboard are not represented unless the user explains them.
  - The agent must maintain a mental model of the user’s physical layout and combine that with the internal state to reason correctly.

- **Context modes**:
  - `context_get()` returns `\"global\"` or `\"python\"`.
  - In `python` context, connections made during a MicroPython session are rolled back when Python exits.
  - In `global` context, connections persist across sessions.
  - The agent should explicitly decide which mode to use and document the choice.

## Where to find more detail

- **Full API reference**: `reference/api-reference.md`
- **Node numbering and aliases**: `reference/node-map.md`
- **Hardware behavior and limits**: `reference/hardware-guide.md`
- **State JSON format**: `reference/state-format.md`
- **Design goals and future extensions**: `reference/vision.md`
- **Host‑side helper and usage**: `scripts/jumperless.py`
- **Device‑side helpers**:
  - Measurements: `scripts/measurements.py`
  - LED animations: `scripts/animations.py`
- **Worked examples**:
  - `examples/measure-resistance.md`
  - `examples/circuit-debugging.md`
  - `examples/led-animations.md`

The agent should treat this skill as the authoritative source for Jumperless‑specific behavior and use the external Jumperless docs (`https://docs.jumperless.org/`) for additional context when necessary.

