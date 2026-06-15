---
name: jumperless-v5
description: >-
  Operates a Jumperless V5 breadboard for hardware-in-the-loop prototyping and
  debugging. Uses MicroPython REPL to route connections, set rails/DACs, perform
  measurements, control GPIO/PWM/OLED/LED overlays, and run guided test scripts.
  Use when the user mentions Jumperless, breadboard wiring, circuit testing,
  hardware debugging, or voltage/current/resistance measurements on physical
  hardware.
---

# Jumperless V5 Skill

This skill controls real Jumperless V5 hardware via MicroPython REPL.

**Working directory:** the skill root (this repo). All commands below are
repo-relative — run them from wherever this skill is installed (e.g.
`~/.cursor/skills/jumperless-v5` or `~/.claude/skills/jumperless-v5`). Do not
hardcode an absolute checkout path.

## Communication methods

The Jumperless exposes four USB CDC serial interfaces. This skill drives the
**MicroPython Raw REPL** (port 5) via `scripts/jumperless.py`, which is the
primary transport for everything below.

| Port | macOS suffix | Role |
|------|--------------|------|
| 1 | `JLV5port1` | Main terminal, menu, `>` one-liner Python |
| 3 | `JLV5port3` | Arduino UART passthrough |
| 5 | `JLV5port5` | MicroPython Raw REPL — **what this skill uses** |
| 7 | `JLV5port7` | USBSer3 read-only machine backchannel (`:help` YAML, `:gpio`, `:leds`, `:adc`, …) |

- **REPL (port 5) is primary** — `jumperless.py detect/exec/state/fs/guide`.
- **Port 7 (USBSer3)** is an optional fast, read-only telemetry channel: send
  `:help` for a self-describing YAML index of its verbs, or `:gpio`, `:leds`,
  `:slot`, `:adc` for instant non-blocking snapshots. It never mutates state —
  defer any state changes to the REPL (or the MCP server).
- **MCP alternative:** for MCP-native clients, build the server from the `mcp/`
  submodule (see "MCP alternative" below). Do not run the MCP server and
  `jumperless.py` against the same board simultaneously — they both want the
  USB port exclusively.

## Non-negotiable behavior

- **You ARE the operator.** Always run commands yourself using the Shell tool. Never tell the user to run `python scripts/jumperless.py ...` — execute it directly. The user should only be asked to perform **physical actions** (place/move parts, press probe/clickwheel).
- Treat the Jumperless as an **active hardware tool**, not a passive advisor. When the user asks to wire, measure, or debug something, do it immediately.
- **Settling time matters.** Crossbar routing, DAC changes, and connection changes are not instantaneous. Always allow settling time before measuring:
  - After `connect()` / `disconnect()` / `dac_set()`: wait at least 2–10 ms (`time.sleep_ms(2)` to `time.sleep_ms(10)`) before reading ADC or INA values.
  - After `nodes_clear()` or `set_state()`: wait 50–100 ms.
  - For sensitive measurements (resistance, current), 50 ms minimum. For voltage sweeps, 20 ms per step is usually sufficient.
- **Always light up the board when asking for physical placement.** Whenever you ask the user to place, move, or remove a component or wire, you MUST run an overlay script first to highlight the target location on the breadboard LEDs, and display the instruction on the OLED. Do not just say "place a resistor at row 5" in text — show them on the board. Clear the overlays once placement is confirmed.
- Before risky operations, snapshot with `get_state()` and restore if needed.
- Never assume external wiring is known; verify with measurements when uncertain.

## Full capabilities at a glance

Always keep these in mind — even in the middle of a specific task, a different peripheral may be the better tool:

| Capability | Key APIs | When to reach for it |
|---|---|---|
| **Virtual wiring** | `connect()`, `disconnect()`, `fast_connect()`, `nodes_clear()` | Any routing change on the crossbar |
| **Voltage measurement** | `adc_get(ch)` with `ADC0`–`ADC3` (±8V), `ADC4` (5V), `ADC7`/`PROBE` | Checking node voltages; always route ADC to node first |
| **Current measurement** | `ina_get_current(sensor)`, `ina_get_bus_voltage(sensor)` | Put `ISENSE_PLUS`/`ISENSE_MINUS` in series; 2Ω shunt |
| **Power measurement** | `ina_get_power(sensor)` | Quick power draw check on a rail |
| **Programmable voltage** | `dac_set(ch, v)` — `DAC0`, `DAC1`, `TOP_RAIL`, `BOTTOM_RAIL` (±8V) | Supplying test voltages, driving circuits, sweeps |
| **Resistance estimation** | DAC + INA + ADC combined (see measurement workflow) | Use adaptive DAC voltage for best accuracy |
| **Digital I/O** | `gpio_set()`, `gpio_get()`, `gpio_set_dir()`, `gpio_set_pull()` | Driving/reading logic signals on `GPIO_1`–`GPIO_8` |
| **PWM output** | `pwm(pin, freq, duty)`, `pwm_stop(pin)` | Generating clock/PWM signals |
| **UART passthrough** | `UART_TX`, `UART_RX` nodes (routable) | Talking to Arduino/Nano or serial peripherals |
| **LED guidance** | `overlay_set()`, `overlay_set_pixel()`, `overlay_clear()` | Visual cues on breadboard; use reduced-brightness colors |
| **OLED display** | `oled_print()`, `oled_clear()` | Showing measurement results or step instructions |
| **Probe input** | `probe_read_blocking()`, `probe_button()` | User touching a specific pad, button-gated steps |
| **Clickwheel** | `clickwheel_get_button()`, `clickwheel_get_position()` | User menu/scroll/confirm interactions |
| **State snapshot** | `get_state()` / `set_state()` | Bulk save/restore, Wokwi import, batch edits |
| **Net inspection** | `get_net_info()`, `is_connected()`, `print_nets()` | Debugging unexpected routing |
| **Filesystem** | `jfs.open()`, `jfs.listdir()`, `jfs.exists()` | Reading/writing files on the device |
| **Arduino reset** | `arduino_reset()` | Resetting a Nano-header MCU |
| **Slots** | `nodes_save(slot)`, `switch_slot(slot)` | Storing/recalling circuit configurations |
| **Context** | `context_get()`, `context_toggle()` | `python` context rolls back on exit; `global` persists |

**Think creatively:** If measuring resistance, consider whether INA-based, ADC-based, or mixed approaches suit the range best. If debugging a circuit, you can probe multiple nodes with different ADC channels simultaneously. If a user needs a clock signal, reach for PWM instead of bit-banging GPIO.

## Getting connected

Before any hardware interaction, ensure connectivity:

```bash
pip install pyserial
python scripts/jumperless.py detect
python scripts/jumperless.py exec "print('ok from jumperless')"
```

If `detect` succeeds, the port is cached in `.jumperless_port` for subsequent calls.

## Execution modes

Prefer these modes in order:

1. **Inline command** (short, single-purpose):

```bash
python scripts/jumperless.py exec "connect(1, D4)"
```

2. **Script file** (multi-line logic — preferred for anything beyond a one-liner):

```bash
python scripts/jumperless.py exec --file scripts/session.py
```

3. **Piped script** (dynamically generated scripts):

```bash
python scripts/jumperless.py exec --stdin <<'PYEOF'
import time
connect(ADC0, 5)
time.sleep(0.05)
v = adc_get(0)
disconnect(ADC0, -1)
print(v)
PYEOF
```

For complex logic, **write a temporary .py file** and use `--file`. Do not cram long multi-line logic into shell-quoted one-liners.

Use `--timeout N` when scripts take longer than the default 8 seconds (e.g. continuous monitors, guided flows).

## Updating a running script

Loop scripts run **on the device** in MicroPython. The host `exec` process exits as soon as it finishes sending the script — the serial port is already free. The MicroPython loop keeps running on the Jumperless itself.

To stop it and send a new version:

**1. Write the updated script to the file.**

**2. Run `exec` with the updated file.**  
`enter_raw_repl()` automatically sends a double Ctrl-C (`\x03\x03`) to the device before sending any new code, interrupting whatever MicroPython loop is currently running.

```bash
python scripts/jumperless.py exec --file scripts/my_loop.py --timeout 300
```

That's it — no process killing needed.

**3. Start every loop script with a cleanup header.**  
The interrupted script may have left connections, overlays, or OLED content mid-run. Always reset to a known state at the top:

```python
import time
nodes_clear()
overlay_clear_all()
oled_clear()
time.sleep(0.05)   # let crossbar settle after clear
```

Background long-running loops with `block_until_ms: 0` so the shell doesn't block waiting for them to finish.

## Settling time patterns

Build these into every script. The crossbar routing fabric and DAC output stages need time to stabilize.

```python
import time

# After making connections
connect(ADC0, 5)
connect(DAC1, ISENSE_PLUS)
time.sleep(0.05)  # 50ms settle

# After changing DAC/rail voltage
dac_set(TOP_RAIL, 3.3)
time.sleep(0.02)  # 20ms for DAC to reach setpoint

# After bulk state changes
set_state(new_state)
time.sleep(0.1)   # 100ms for full state application

# For multi-sample measurements, small inter-sample delay
for _ in range(16):
    v = adc_get(0)
    samples.append(v)
    time.sleep(0.01)  # 10ms between samples
```

## Visual placement guidance

Whenever the user needs to place, move, or remove something physical, **run an overlay script before asking**. The board shows them exactly where to go; OLED echoes the instruction in text.

### Overlay coordinate system

The LED canvas is rows 1–10, cols 1–30:

- **Rows 1–5** = top breadboard half (breadboard rows 1–30)
- **Rows 6–10** = bottom breadboard half (breadboard rows 31–60)
- **Col 1–30** = the 30 columns of holes within each half

Breadboard row N → overlay col N (top half, N 1–30) or col N−30 (bottom half, N 31–60).
The 5 holes A–E in each strip correspond to overlay rows 1–5 (top) or 6–10 (bottom).

### Placement patterns

**Single component / pin — use `place_here()` + `oled_print()`:**

```python
import time

# Mark a single hole bright red, tell user on OLED
overlay_set_pixel(3, 10, 0xFF2020)          # direct: row 3, col 10
# — or using animations helper if loaded —
place_here("target_pin", 3, 10, 0xFF2020)

oled_clear()
oled_print("Place R1 pin 1")
oled_print("Row 10, top half")
```

**IC spanning multiple rows — use `highlight_range()` for the body, `place_here()` per pin:**

```python
# IC body across breadboard rows 5-12 (top half → overlay cols 5-12)
highlight_range("ic_body", 1, 1, 0x203030)   # single overlay row, cols 5-12
# Pin 1 marker
place_here("ic_pin1", 2, 5, 0xFF2020)

oled_clear()
oled_print("Place 555 timer")
oled_print("Pin 1 at row 5")
```

**Span of rows (e.g. resistor leg to leg):**

```python
# Highlight rows 5 and 15 where resistor legs go
place_here("r1_a", 1, 5, 0xFF8000)
place_here("r1_b", 1, 15, 0xFF8000)

oled_clear()
oled_print("Place R1: row 5 to 15")
```

**Removal / "move this wire":**

```python
# Use a different color (e.g. red pulsing) to mark what to remove
highlight_row("remove_wire", 3, 0xFF2020)

oled_clear()
oled_print("Remove wire at row 3")
```

### Always clear overlays after confirmation

After the user confirms placement (probe button, clickwheel, or verbal confirmation), clear the guidance overlays so they don't obscure net colors:

```python
overlay_clear("target_pin")
overlay_clear("ic_body")
# — or wipe everything —
overlay_clear_all()
oled_clear()
```

### In guided step flows, pair each step with an overlay

When using `jumperless.py guide`, run a matching overlay script immediately before each button-wait so the board lights up with the current step's target location. Use `overlay_clear_all()` at the start of each step to remove the previous step's marks.

## Workflow selection

Choose based on the task, then read only the files needed. But stay aware of the full capabilities table above — better solutions may combine peripherals across workflows.

1. **Connectivity / rewiring**
   - Read: `reference/node-map.md` → `reference/api/connections-routing.md`
   - Use `fast_connect()` / `fast_disconnect()` for batch operations (skips LED updates)

2. **Measurement (V/I/R, sweeps)**
   - Read: `reference/api/measurements-power.md`
   - For reusable patterns: `scripts/measurements.py`, `measureR.py`
   - Always account for crossbar series resistance (20–40Ω default `connect()`, ~80Ω with `duplicates=0`) and 2Ω ISENSE shunt

3. **Visual guidance (LEDs, OLED)** — mandatory any time you ask for physical action
   - See "Visual placement guidance" section above for patterns
   - Read: `reference/api/ui-interaction-system.md` → `scripts/animations.py`
   - Use reduced-brightness saturated colors (e.g. `0x2020FF`, not `0x0000FF`)
   - `0x000000` = transparent in overlays; always `overlay_clear_all()` after step completes

4. **State surgery / batch edits**
   - Read: `reference/state-format.md` → `reference/api/state-nets-filesystem.md`

5. **Guided human-in-the-loop flows**
   - `python scripts/jumperless.py guide --file steps.txt`
   - One step per line; device shows on OLED and waits for probe button / clickwheel

Only load `reference/api-reference.md` when a task spans multiple API domains.
For transport/hanging issues, load `reference/repl-runtime-playbook.md`.

## Core command patterns

```bash
# Snapshot full state
python scripts/jumperless.py state

# Execute a script file
python scripts/jumperless.py exec --file scripts/session.py

# List device filesystem
python scripts/jumperless.py fs

# Longer timeout for continuous scripts
python scripts/jumperless.py exec --file scripts/measureR.py --timeout 60
```

## Measurement best practices

### Always settle, always sample multiple times

```python
import time

connect(ADC0, 5)
time.sleep(0.05)

samples = [adc_get(0) for _ in range(8)]
v_avg = sum(samples) / len(samples)
print("V at row 5:", v_avg)

disconnect(ADC0, -1)
```

### Resistance: choose method by expected range

- **Low R (<500Ω):** Use lower DAC voltage (0.5–1.5V) to avoid high current. INA-based is most accurate.
- **Medium R (500Ω–10kΩ):** DAC at 2–3V. Mixed ADC+INA gives best results.
- **High R (>10kΩ):** Use higher DAC voltage (3–5V). Baseline-corrected method recommended (measure leakage current with load floating, then subtract).

### Adaptive DAC voltage ladder (from `measureR.py`)

```python
if R_prev is None:     v_set = 2.0
elif R_prev < 200:     v_set = 0.5
elif R_prev < 1000:    v_set = 1.5
elif R_prev < 5000:    v_set = 2.5
else:                  v_set = 4.0
```

### Hardware constraints to remember

- Crossbar path resistance: ~80Ω with `duplicates=0` (single path); ~20–40Ω with default `connect()` (firmware stacks paths in parallel)
- ISENSE shunt: 2Ω (ISENSE_PLUS and ISENSE_MINUS are always connected through it)
- DAC/rail range: approximately ±8V
- ADC0–ADC3: ±8V range; ADC4: 5V range; ADC7/PROBE: probe channel
- Signal bandwidth: ~8MHz through crossbar, ~13MHz 3dB on breadboard
- Firmware refuses dangerous connections (e.g. TOP_RAIL directly to GND)
- Firmware cannot see user-placed external wires — always ask or verify

## Electronics reference

Load `reference/electronics-reference.md` for Ohm's Law, series/parallel, voltage dividers, KVL/KCL, RC time constant, logic levels, LED current limiting, pull-up/pull-down, IC pin numbering (DIP diagrams + common IC tables), decoupling capacitors, and a measurement troubleshooting table.

Load it whenever you need to size a component, verify a measurement makes sense, map IC pins to breadboard rows, or explain a result to the user.

## Safety approach

Default to conservative behavior:
- Snapshot state before making significant changes
- Confirm before clearing all nets or large rail voltage changes
- Start with read-only inspections (net info, measurements) before rewiring

Increase autonomy as user context indicates experience. For power users and the hardware designer, broader rewiring and experimental manipulations are fine — still document what was done and why.

## Debugging circuits

When measurements don't match expectations:

1. Inspect internal state: `get_state()`, `print_nets()`, `print_bridges()`
2. Verify specific connections: `is_connected(node1, node2)`
3. Measure at key nodes using ADC
4. Consider external factors (misplaced parts, wrong resistor values, additional loads)
5. Cross-reference with the user's description of physical component placement

## Performance and context discipline

- Keep reasoning focused on the active task.
- Read only the reference files needed for the current workflow.
- Prefer writing temporary script files over ad-hoc shell-quoted multi-line strings.
- Return measured results concisely — the user cares about values and conclusions, not pages of planning text.
- For long-running scripts (continuous monitors, guided flows), use `--timeout` appropriately and `block_until_ms: 0` to background them.

## MCP alternative

If you are on an MCP-native client (Claude Desktop, Cursor MCP, …), you can use
the **jumperless-mcp** server instead of this skill's shell transport. It lives
as the `mcp/` git submodule in this repo:

```bash
git submodule update --init --recursive    # if not cloned with --recurse-submodules
cd mcp && cargo install --path .            # or use a release binary
```

Point your MCP client at the built `jumperless-mcp` binary. See `mcp/README.md`
for tool list and lifecycle. **The MCP server holds the USB port exclusively
while running** — don't run `jumperless.py` against the same board at the same
time.

## Canonical API reference

`reference/api-reference.md` (and the `reference/api/` split) is a convenience
copy that can drift. When precise call signatures matter, treat the docs site
as canonical: <https://docs.jumperless.org/09.5-micropythonAPIreference/>.

## File map

- Host transport and REPL runner: `scripts/jumperless.py`
- MCP server (submodule): `mcp/` — see `mcp/README.md`
- Measurement helpers (device-side): `scripts/measurements.py`
- Resistance measurement scratch: `measureR.py`
- LED/OLED animation helpers: `scripts/animations.py`
- Progressive routing map: `reference/progressive-disclosure-map.md`
- REPL/runtime playbook: `reference/repl-runtime-playbook.md`
- Full deep guide: `reference/deep-dive/full-skill-guide.md`
- API split: `reference/api/connections-routing.md`
- API split: `reference/api/measurements-power.md`
- API split: `reference/api/state-nets-filesystem.md`
- API split: `reference/api/ui-interaction-system.md`
- API monolith (legacy fallback): `reference/api-reference.md`
- Node IDs/aliases: `reference/node-map.md`
- Hardware behavior: `reference/hardware-guide.md`
- Electronics quick reference: `reference/electronics-reference.md`
- State JSON schema: `reference/state-format.md`
- Design context/roadmap: `reference/vision.md`
