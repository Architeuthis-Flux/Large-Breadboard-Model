# Jumperless V5 Agent Skill Vision

This document captures the broader goals and design intent behind the Jumperless V5 Agent Skill. It is not loaded into context by default, but serves as a reference for future iterations and contributors.

---

## High-level vision

The Jumperless V5 should feel like an **extension of the agent’s body** into the physical world:

- The agent can **wire, rewire, and measure** a real circuit on a smart breadboard.
- Users describe circuits, components, and goals in natural language.
- The agent translates those into **precise node connections, measurements, and visual guides**.
- The feedback loop is tight: measure → analyze → adjust wiring → measure again.

The end goal is for an LLM to:

1. Understand what hardware the user has placed on the board (chips, modules, passives).
2. Plan tests to learn unknown parameters or debug misbehavior.
3. Use the smart breadboard’s instrumentation to carry out those tests.
4. Interpret results in the context of datasheets and circuit theory.
5. Explain and visualize what’s happening using the OLED and breadboard LEDs.

---

## Core pillars

### 1. Robust connectivity & REPL access

- **Port detection must be reliable and cross‑platform.**
  - Handles macOS (`/dev/cu.usbmodemJLV5port*`), Linux (`/dev/ttyACM*`), Windows (`COMx` + `MI_XX`).
  - Uses both naming heuristics and active probing (Ctrl‑C / REPL prompt).
  - Caches the found port for fast future use.

- **Raw REPL protocol is the primary transport.**
  - Matching JumperIDE’s `rawmode.js` behavior: `Ctrl-A`, send code, `Ctrl-D`, read `OK` + stdout + stderr + `Ctrl-B`.
  - Enables precise control of command boundaries and reduces prompt/parsing ambiguity.

### 2. MicroPython API as the “surface area”

- The MicroPython `jumperless` module is the main abstraction layer.
- The skill documents:
  - Node connections
  - DAC/ADC/INA measurement APIs
  - GPIO and PWM
  - Net/path inspection
  - JFS filesystem access
  - Overlay and OLED control
  - Slots and context
- Where possible, the agent uses **these APIs** instead of manipulating internal firmware details.

### 3. State-based reasoning

- `get_state()` / `set_state()` expose the entire board as a JSON structure.
- The agent:
  - Takes snapshots before making big changes.
  - Uses the state to reason about nets, rails, GPIOs, and overlays.
  - Can perform **batch edits** (e.g. adjusting rail voltages and overlay graphics in one go).
  - Uses `from_wokwi=True` when importing designs directly from Wokwi diagrams.

### 4. Visual guidance via LEDs and OLED

- The breadboard LEDs are not just decoration; they are a **visual UI canvas**:
  - Highlight where to place components.
  - Show animated flows (e.g. “marching ants” along a current path).
  - Encode statuses (OK / warning / error) as subtle brightness or color changes.

- The OLED can display:
  - Measurement readouts.
  - Step‑by‑step instructions.
  - Simplified menus or diagrams.

The `animations.py` and `measurements.py` libraries are the first steps toward a reusable visual and measurement toolkit.

---

## Safety levels and user modeling

We want the agent to be **helpful but not overbearing**. The board is quite robust and has an effectively infinite no‑fault warranty, but users may still be confused or working with delicate external circuits.

Safety levels:

- **Beginner:**
  - Always snapshot state before changes.
  - Confirm before clearing nets or changing rail voltages.
  - Prefer read‑only inspections first (net info, printing help) before rewiring.
  - Explain steps in plain language with extra context.

- **Advanced:**
  - Snapshot, then modify more freely.
  - Use advanced measurement patterns (e.g. DAC+INA resistance measurement, IV sweeps).
  - Give less verbose explanations, focusing on key decisions and edge cases.

- **God mode:**
  - For power users and the hardware designer.
  - The agent can perform broad rewiring, complex overlays, and experimental manipulations with minimal confirmation.
  - Still documents what it did and why, but trusts the user to manage external risks.

The agent should infer a plausible starting level from the user’s language and prior behavior (e.g. “soldered the shunt upside down” vs. “what is a pull‑up?”) and then adapt.

---

## Measurement strategies

The Jumperless provides rich instrumentation:

- DACs (`dac_set`, `dac_get`)
- ADCs (`adc_get`)
- INA current/power sensors (`ina_get_current`, `ina_get_bus_voltage`, `ina_get_power`)
- GPIO digital inputs/outputs

Higher‑level measurement patterns we want to support well:

1. **Voltage at a node**
   - Connect node → ADC using `connect(ADCx, node)`.
   - Read with `adc_get(x)`.
   - Disconnect if it was a temporary probe.

2. **Current through a branch**
   - Insert `ISENSE_PLUS` / `ISENSE_MINUS` in series.
   - Read `ina_get_current(sensor)` and `ina_get_bus_voltage(sensor)`.

3. **Resistance between two nodes**
   - Use DAC + shunt:
     - Drive a known voltage across the unknown resistance via DAC and shunt.
     - Measure bus voltage and current.
     - Compute `R ≈ V / I`, accounting for shunt resistance and crossbar resistance.
   - Repeat at multiple DAC setpoints for better averaging.

4. **IV curves / sweeps**
   - Step DAC over a range and log current/voltage.
   - Present results to the user in a structured, plot‑friendly form.

The `scripts/measurements.py` file provides reusable device‑side helpers for these tasks, so the agent doesn’t need to generate all measurement math from scratch each time.

---

## Overlays and animations

The LED overlay system is a powerful way to communicate visually:

- Canvas: 5×60 “pixels” (with a gap between halves).
- Each pixel: 0xRRGGBB color, with `000000` for transparent.

Design goals:

- **Readable and gentle**:
  - Use high saturation but low brightness.
  - Avoid rapid flashing; prefer smooth breathing/pulsing, sliding highlights, or marching dots.

- **Spatial guidance**:
  - Highlight which **rows** matter (top/bottom halves).
  - Draw boxes, arrows, or “path” lines for current flow or data flow.
  - Mark specific holes (e.g. for IC pins) with small, bright indicators.

The first version of `animations.py` should include:

- `highlight_row(row, color)` — gently pulse all LEDs in a row.
- `highlight_range(start_row, end_row, color)` — highlight multiple rows.
- `arrow_between(from_row, to_row, color)` — an animated arrow showing direction.
- `place_here(row, col)` — a blinking “place component here” indicator.

Future directions:

- Parametric patterns (e.g. scanning bars, per‑net color animations).
- Linking overlay patterns directly to `get_state()` (e.g. highlight all nodes in a net).

---

## Datasheet integration and circuit understanding

To move beyond simple “connect this to that” tasks, the agent should:

- Recognize IC names and part numbers from user descriptions.
- Fetch relevant datasheets and application notes (e.g. op‑amps, 555 timers, sensor modules).
- Build a mental model of the IC’s pinout and recommended circuits.
- Map logical pins to **breadboard nodes** based on how the user placed the part.

Example workflow:

1. User: “I placed an NE555 across rows 1–4 and 31–34, pin 1 at row 1.”
2. Agent:
   - Uses standard DIP mapping (rows 1–4, 31–34).
   - Fetches NE555 datasheet.
   - Plans an astable configuration (R1, R2, C1, C2).
   - Generates `connect(...)` commands to implement it on those nodes.
   - Uses overlays to highlight the nodes associated with each pin and component.
   - Uses ADC/INA to verify the expected oscillation (e.g. threshold levels, frequency).

The skill does not implement datasheet logic itself but is designed so that higher‑level reasoning (possibly via other skills) can plug in this knowledge.

---

## Debugging philosophy

When the user says “it doesn’t work”:

1. **Clarify the intended behavior.**
   - What should the circuit do?
   - What are the expected voltages/currents or waveforms at key nodes?

2. **Inspect internal state.**
   - `get_state()` → inspect nets, rails, GPIOs.
   - `print_nets()`, `print_bridges()`, `get_net_info()` → make sure virtual wiring matches the intended schematic.

3. **Check measurements at key points.**
   - Use ADC/INA to measure actual quantities at important nodes.
   - Compare with theory or datasheet expectations.

4. **Consider external factors.**
   - Missing or mis‑wired components (user’s breadboard placements).
   - Power supply not set to correct voltage.
   - Input signals not present or unstable.

5. **Propose targeted fixes.**
   - Suggest moving a wire, changing a resistor value, or adjusting rail voltage.
   - Update the virtual wiring accordingly and verify again.

The skill encourages clear, step‑by‑step reasoning rather than one‑shot “fixes”.

---

## Roadmap ideas

Potential future extensions for this skill:

1. **Higher-level circuit abstractions**
   - Logical representation of circuits (nets, components, models) that can be converted to Jumperless wiring + state.
   - Libraries for common topologies (voltage dividers, RC filters, op‑amp configs, 555 astables).

2. **Automated characterization suites**
   - MIL‑like test plans: measure component behavior across ranges (e.g. LED IV curves, transistor beta, sensor responses).
   - Store results in host‑side files for plotting and further analysis.

3. **Self‑calibration and diagnostics**
   - Agent‑driven calibration routines for rails, ADCs, DACs, and probes.
   - Automatic detection of stuck bits or dead nodes in the crossbar.

4. **Interactive teaching modes**
   - Guided labs where the agent walks the user through building and measuring classic circuits (e.g. RC charging curves, op‑amp gain, logic gates).
   - Use overlays + terminal + OLED to create “lesson flows”.

5. **Integration with other tools**
   - Seamless hand‑off between schematic capture (e.g. KiCad, Wokwi) and Jumperless state.
   - Automatic mapping from imported designs to breadboard rows and overlays.

---

## How to evolve this skill

When extending this skill:

- Keep `SKILL.md` focused and under ~500 lines; move heavy reference into `reference/`.
- Avoid duplicating complex logic (like port detection) in multiple places; expose clear entry points (e.g. `scripts/jumperless.py`).
- Document new device‑side helpers (`measurements.py`, `animations.py`, any future scripts) in both `SKILL.md` and `reference/api-reference.md` as they become stable.
- Treat `reference/vision.md` as a living design brief — update it when major design decisions change.

