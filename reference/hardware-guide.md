# Jumperless V5 Hardware Guide (for Agents)

This file summarizes the key hardware characteristics of the Jumperless V5 that matter when you are planning measurements, wiring, and safety.

For deeper background, see the main docs at `https://docs.jumperless.org/` and the config reference in `docs/06-config.md` of the firmware repo.

---

## Core architecture

- **MCU:** RP2350B (dual‑core)
- **Crossbar switches:** CH446Q array (“chips” A–L)
  - First 8 chips (A–H): breadboard region
  - Last 4 chips (I–L): special‑function region (GPIOs, ADCs, DACs, UART, etc.)
- **Smart breadboard:** every pad is connected to the crossbar and has its own RGB LED.
- **Power range:** approximately −8 V to +8 V for rails and DACs.

The crossbar allows arbitrary routing between:

- Breadboard rows `1`–`60`
- Power rails (`TOP_RAIL`, `BOTTOM_RAIL`, `GND`, `SUPPLY_3V3`, `SUPPLY_5V`, ±8 V supplies)
- DAC nodes (`DAC0`, `DAC1`)
- ADC nodes (`ADC0`–`ADC4`, `ADC7/PROBE`)
- Current‑sense shunt nodes (`ISENSE_PLUS`, `ISENSE_MINUS`)
- Routable GPIOs and UART (`GPIO_1`–`GPIO_8`, `UART_TX`, `UART_RX`)
- Arduino Nano header pins (`D0`–`D13`, `A0`–`A7`, etc.)

---

## USB endpoints (CDC interfaces)

The Jumperless V5 enumerates as a composite USB device with multiple CDC interfaces. In firmware (`include/usb_interface_config.h`) the interface names are:

```c
static const char* USB_CDC_NAMES[] = {
    "Jumperless Main",       // CDC 0 - Main serial
    "JL UART Passthrough",   // CDC 1 - Arduino/Serial1
    "JL Micropython REPL",   // CDC 2 - Micropython REPL
    "JL TUI",                // CDC 3 - TUI
    "JL Serial 3"            // CDC 4 - Serial 3
};
```

On typical systems:

- **macOS:**
  - Ports are `/dev/cu.usbmodemJLV5port1`, `...3`, `...5`, `...7`, etc.
  - The **MicroPython REPL** is on `JLV5port5` (CDC 2).
  - The “Main” interface (`Jumperless Main`) is often `JLV5port1`.

- **Linux:**
  - Ports appear as `/dev/ttyACM0`–`/dev/ttyACM3` (order can vary).
  - The REPL is usually the third interface (CDC 2), so `/dev/ttyACM2` is often correct in a clean system.

- **Windows:**
  - Ports appear as `COMx` with `MI_00`, `MI_02`, `MI_04`, `MI_06`, `MI_08` in the device instance ID.
  - Each CDC function uses two interfaces; CDC index = `MI_XX / 2`.
  - The REPL (CDC 2) corresponds to `MI_04` → that COM port is the MicroPython REPL.

The host helper script (`scripts/jumperless.py`) uses these patterns plus probing to locate the Micropython REPL.

---

## Crossbar resistance and signal integrity

The CH446Q crossbar fabric introduces a non‑negligible series resistance:

- **Per path:** approximately 80 Ω for a single routing path
- **Stacked paths:** firmware can route multiple parallel paths between nodes (`[routing] stack_paths`, etc.), reducing effective resistance to ~20 Ω in heavily used connections

Implications:

- Voltage measurements under load will show some sag vs. ideal circuit math.
- Very low‑resistance loads (e.g. direct short between rails through crossbar) will see limited current; the crossbar acts like a series resistor.
- For sensitive analog circuits, keep in mind the extra series resistance and the breadboard’s own parasitics.

Bandwidth:

- The crossbar can handle signals on the order of ~8 MHz.
- The physical breadboard has ~13 MHz 3 dB roll‑off; expect slower edges and more distortion as frequency increases.

Agents should **not** assume perfect wires; account for finite resistance and bandwidth when interpreting analog measurements or designing high‑speed experiments.

---

## Current sensing (ISENSE shunt)

The current‑sense pair `ISENSE_PLUS` / `ISENSE_MINUS` is implemented as the two ends of a **2 Ω shunt resistor**:

- They are internally shorted through this resistor.
- They must be used **in series** with the circuit being measured (not across a supply).
- The INA218x sensors measure shunt and bus voltages to compute current and power.

Typical use pattern:

1. Insert the shunt in series:
   - `connect(ISENSE_PLUS, node_high)` (e.g. rail or DAC)
   - `connect(ISENSE_MINUS, node_low)` (load side)
2. Read:
   - `ina_get_current(0)` or `ina_get_current(1)` depending on which shunt is wired
   - `ina_get_bus_voltage(sensor)` for voltage
3. Disconnect when done if the measurement is temporary.

Because of the 2 Ω shunt, **ISENSE+ and ISENSE‑ are effectively shorted** at low frequencies; never place them across a low‑impedance supply without understanding that they will conduct.

---

## Voltage ranges and safety

- Rails and DACs:
  - Programmable from about **−8 V to +8 V**.
  - The firmware enforces safe limits; attempts outside range are clamped.

- ADC channels:
  - `ADC0`–`ADC3` — designed for up to ±8 V
  - `ADC4` — 5 V range (safe for logic‑level measurements)
  - `ADC7` / `PROBE` — probe path; see probe docs for details

**Absolute maximums:** the hardware is robust, but as a rule the agent should assume:
- Do not expect correct behavior beyond ±9 V anywhere on the board.
- Avoid building circuits that intentionally source/sink large currents into the crossbar paths.

The firmware will **ignore** some dangerous operations (e.g. directly connecting `TOP_RAIL` to `GND`) by refusing to create such bridges. However, it **cannot** see user‑placed wires or external shorts. The agent must always consider the **physical** circuit description provided by the user.

---

## Config reference (selected fields)

From `docs/06-config.md`, some relevant configuration keys:

```text
[routing] stack_paths = 2;
[routing] stack_rails = 3;
[routing] stack_dacs = 0;
[routing] rail_priority = 1;
```

Meaning:

- `stack_paths` — how many parallel paths to use for general connections.
- `stack_rails` — extra stacking for rail connections (lower effective resistance).
- `stack_dacs` — stacking for DAC paths (0 means none).
- `rail_priority` — routing priority for rail paths vs. others.

Other notable config sections:

- `[dacs]` — limits and behavior for DACs and rails (`limit_max`, `limit_min`, etc.).
- `[calibration]` — calibration constants for DACs and ADCs (offsets and spreads).
- `[logo_pads]` — mapping of special logo pads (UART Tx/Rx, ISENSE pads).
- `[display]` — LED and menu brightness, color modes.
- `[serial_1]` — UART passthrough behavior (baud rate, connect_on_boot, etc.).
- `[top_oled]` — whether the OLED is enabled and how it’s wired.

Agents usually do **not** modify these settings directly, but knowing them helps explain measurement deviations and routing behavior.

---

## Probe and clickwheel notes

- Probe mode uses a resistive divider to sense pad voltages; touching pads with fingers or leaving the probe at an unstable potential leads to noisy readings.
- The probe switch has two positions:
  - `measure` mode — outputs a nominal 3.3 V onto the sense pad (used for measurement calibration).
  - `select` mode — used for normal pad selection.
- The `probe calib` app lets users calibrate probe thresholds; the agent can suggest running this if probe readings are inconsistent.

The clickwheel encoder:

- Supports short press (`click`) and long press (`hold`) semantics.
- Controls onboard menus and can scroll through “virtual nodes” (rails, DACs, ADCs, GPIOs, etc.) even without touching the probe.

While the agent can drive menus conceptually, most higher‑level automation should rely on the MicroPython API rather than simulating user menu actions.

---

## Breadboard LEDs and brightness

Every breadboard hole has an RGB LED underneath that the firmware uses for:

- Net visualization (colors by net)
- Probing and highlighting
- Custom overlays via the overlay API

Brightness considerations:

- Full‑scale white `0xFFFFFF` is **too bright** for normal use.
- Recommended:
  - White: around `0x404040` (or lower)
  - Colorful overlays: use saturated hues with reduced magnitude, e.g.:
    - Blue: `0x2020FF`
    - Green: `0x20FF20`
    - Red: `0xFF2020`
    - Cyan: `0x20FFFF`
- Overlays are drawn on top of the firmware’s own net display; use `0x000000` for “transparent” pixels so wires remain visible.

Animations:

- The firmware updates LEDs at a high frame rate; overlays can be updated every ~150 ms for smooth, non‑jarring motion.
- Simple pulsing or subtle motion is preferred over rapid flashing, both for visibility and comfort.

The `scripts/animations.py` library is designed to follow these guidelines.

---

## Slots, context, and persistence

Slots:

- Up to 8 or 10 “slots” (depending on firmware) store complete circuit configurations as YAML files under `/slots/slotN.yaml`.
- APIs:
  - `nodes_save(slot=None)` — save current circuit to a slot.
  - `switch_slot(slot)` — load a saved slot.
  - `nodes_has_changes()` / `nodes_discard()` — manage unsaved changes.

Context:

- `context_get()` → `"global"` or `"python"`.
- `context_toggle()` — switch between them.

Behavior:

- **python context** — connections made while a MicroPython script runs are rolled back after Python exits.
- **global context** — connections persist across sessions and restarts.

Agents should choose context explicitly and document their assumptions, especially in tutorials or multi‑step procedures.

---

## Summary for planning experiments

When designing hardware‑in‑the‑loop procedures:

1. **Respect voltage and current limits** — stay within ±8 V, and remember crossbar resistance.
2. **Account for the shunt** — `ISENSE+` and `ISENSE−` are a 2 Ω link; always use them in series.
3. **Assume finite impedance** — crossbar and breadboard add non‑ideal behavior; expect some sag and bandwidth limits.
4. **Combine virtual and physical models** — internal state describes only crossbar connections; always integrate the user’s description of external wiring and components.
5. **Use gentle LED patterns** — low brightness, saturated colors, smooth animations.

Keeping these constraints in mind will help you generate safe, realistic experiments and interpret results correctly.

