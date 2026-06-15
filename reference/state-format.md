# Jumperless V5 State JSON Format

The function `get_state()` returns a **JSON string** describing the entire board state: power rails, nets, GPIOs, and overlays. `set_state(json_str, clear_first=True, from_wokwi=False)` applies such a state.


> [!NOTE]
> The entire immediate state of the board is defined in this JSON (or YAML) slot file and can be shared to another Jumperless, saved as a backups, included in tutorials, etc. 


This file explains the structure so agents can safely inspect, modify, and re‑apply state.

---

## Top-level structure

A typical `get_state()` JSON (pretty‑printed) looks like:

```json
{
  "power": {
    "top_rail": 3.8,
    "bottom_rail": 3.8,
    "dac0": 3.25,
    "dac1": 0.0
  },
  "nets": [
    {
      "index": 1,
      "name": "GND",
      "nodes": ["GND", "21"],
      "special": "none"
    },
    {
      "index": 2,
      "name": "Top Rail",
      "nodes": ["TOP_R", "23"],
      "special": "RAIL",
      "voltage": 3.8
    }
    // ...
  ],
  "gpio": [
    {
      "pin": 1,
      "net": null,
      "function": "SIO",
      "direction": "INPUT",
      "pull": "down",
      "reading": "unknown",
      "floating_read": 1
    },
    {
      "pin": "TX",
      "net": 7,
      "function": "UART",
      "direction": "OUTPUT",
      "pull": "down",
      "reading": "unknown",
      "floating_read": 0
    }
  ],
  "overlays": [
    {
      "name": "border",
      "row": 1,
      "col": 1,
      "width": 30,
      "height": 10,
      "colors": ["003333", "003333", "..."]
    }
  ]
}
```

There may be additional keys in future firmware versions; agents should **not** assume the set of keys is fixed and should preserve unknown keys when round‑tripping.

---

## `power` section

```json
"power": {
  "top_rail": 3.8,
  "bottom_rail": 3.8,
  "dac0": 3.25,
  "dac1": 0.0
}
```

Fields:

- `top_rail` — voltage (float) configured for `TOP_RAIL`
- `bottom_rail` — voltage configured for `BOTTOM_RAIL`
- `dac0`, `dac1` — DAC channel setpoints

When using `set_state`, changing these values is equivalent to calling `dac_set()` on the corresponding channels.

---

## `nets` section

Each item describes a net (set of nodes that are electrically connected inside the crossbar).

Example:

```json
{
  "index": 4,
  "name": "DAC 0",
  "nodes": ["DAC_0", "BUF_IN"],
  "special": "DAC",
  "voltage": 3.25
}
```

Fields:

- `index` — numeric net index
- `name` — human‑readable net name (may be auto‑generated or user‑defined)
- `nodes` — array of node names (strings), such as `"GND"`, `"TOP_R"`, `"21"`, `"D13"`, etc.
  - These names correspond to the mapping in `reference/node-map.md`.
- `special` — optional annotation for special nets; typical values:
  - `"none"` — normal net
  - `"RAIL"` — power rail (top or bottom)
  - `"DAC"` — DAC output net
  - `"UART_TX"` / `"UART_RX"` — UART nets
  - Other firmware‑defined markers
- `voltage` — optional; expected or configured voltage on this net (when known)
- Other fields (like `color`, `anim`, etc.) may be present and should be preserved.

**Important:** `nets` describes **logical groupings** of nodes. It is **not** a direct list of bridges; bridges are derived from the crossbar configuration internally.

---

## `gpio` section

Each entry describes one logical GPIO:

```json
{
  "pin": 1,
  "net": null,
  "function": "SIO",
  "direction": "INPUT",
  "pull": "down",
  "reading": "unknown",
  "floating_read": 1
}
```

Fields:

- `pin` — either:
  - An integer `1`–`8` for `GPIO_1`–`GPIO_8`
  - `"TX"` or `"RX"` for the UART pins
- `net` — net index this pin is connected to (or `null` if unconnected)
- `function` — textual description of function:
  - `"SIO"` — standard GPIO
  - `"UART"` — UART TX/RX
  - Other firmware‑defined roles
- `direction` — `"INPUT"` or `"OUTPUT"`
- `pull` — `"up"`, `"down"`, or `"none"`
- `reading` — textual summary of the last known logic state (`"high"`, `"low"`, `"unknown"`, etc.)
- `floating_read` — boolean (0/1) indicating whether floating detection is enabled

Agents can **inspect** this section to understand logical GPIO usage, but should generally **change GPIO configuration via the MicroPython APIs** (`gpio_set_dir`, `gpio_set_pull`, etc.) rather than editing this JSON directly.

---

## `overlays` section

Overlays describe additional graphics drawn on the breadboard RGB LEDs. They are rendered **on top of** the firmware’s net coloring.

Example:

```json
{
  "name": "border",
  "row": 1,
  "col": 1,
  "width": 30,
  "height": 10,
  "colors": [
    "003333", "003333", "...",
    "003333", "000000", "...",
    "... more hex color strings ..."
  ]
}
```

Fields:

- `name` — overlay name (string)
- `row` — top row (1–10)
- `col` — left column (1–30)
- `width` — width in columns
- `height` — height in rows
- `colors` — flat array of **hex color strings without `0x` prefix**, e.g. `"003333"`, `"FF2020"`
  - Length = `width * height`
  - Order is row‑major: top row left→right, then next row down, etc.
  - `"000000"` means “transparent” — do not override underlying LED color

Brightness recommendation:

- Avoid full‑scale white `FFFFFF`.
- Prefer saturated colors with reduced magnitude (~25%): e.g. `2020FF`, `20FF20`, `FF2020`, `404040`.

When editing overlays via JSON:

- Always maintain the correct `width * height` number of color entries.
- Preserve unknown fields if present.
- Ensure that `row`, `col`, `width`, and `height` keep the overlay within the 5×60 canvas (rows 1–10, columns 1–30).

Often it is easier to use the MicroPython overlay APIs (`overlay_set`, `overlay_clear`, etc.) directly instead of editing `overlays` in the state JSON manually. The JSON is still useful for inspection and for bulk export/import of complex scenes.

---

## Editing state safely

General guidelines:

1. **Fetch once, apply locally.**
   - Call `get_state()` and parse the JSON in the host environment.
   - Keep this as your “baseline” snapshot.

2. **Work on a copy.**
   - Clone the baseline object before modifying it.
   - Preserve unknown fields.

3. **Modify only what you care about.**
   - For power: update `power.top_rail`, `power.dac0`, etc.
   - For overlays: add or replace specific entries in `overlays`.
   - Avoid rewriting `nets` unless you fully understand the implications; it is often better to use `connect()`/`disconnect()` APIs to modify connectivity.

4. **Re‑serialize and apply.**
   - Use a standard JSON encoder.
   - Call `set_state(json_string, clear_first=True)` when applying a complete, authoritative state.
   - If you are only adding overlays or adjusting power but want to preserve dynamic routing changes, you may choose `clear_first=False` (if supported and appropriate) or modify only overlays via MicroPython functions.

5. **Rollback on problems.**
   - If `set_state` leads to unexpected behavior, re‑apply the saved baseline snapshot.

---

## Example: adjusting top rail voltage via state

Instead of:

```python
dac_set(TOP_RAIL, 5.0)
```

You can do:

```python
import json
state = json.loads(get_state())
state["power"]["top_rail"] = 5.0
set_state(json.dumps(state))
```

This approach is useful when batching multiple changes (e.g. updating both rail voltages and overlays) in a single atomic operation.

---

## Example: augmenting overlays

Suppose `get_state()` returns a state with existing overlays, and you want to add a new “place‑here” marker at row 3, column 10:

```python
import json

state = json.loads(get_state())

# Create a 1×1 overlay with a bright but not full‑scale green
place_here = {
    "name": "place_here_row3_col10",
    "row": 3,
    "col": 10,
    "width": 1,
    "height": 1,
    "colors": ["20FF20"]
}

state.setdefault("overlays", [])
state["overlays"] = [
    o for o in state["overlays"] if o.get("name") != place_here["name"]
] + [place_here]

set_state(json.dumps(state))
```

This pattern:

- Preserves existing overlays.
- Replaces any prior overlay with the same name.
- Leaves other state fields untouched.

---

## Wokwi import (`from_wokwi=True`)

When `from_wokwi=True`, `set_state()` expects `json_str` to be a Wokwi `diagram.json` rather than a Jumperless state JSON. The firmware converts the Wokwi representation into bridges, nets, and colors.

Agents can:

- Ask the user to paste a Wokwi JSON.
- Pass it directly to `set_state(wokwi_json, clear_first=True, from_wokwi=True)`.

After that, a subsequent `get_state()` will return the standard Jumperless state JSON.

---

## Robustness tips for agents

- Treat `get_state()` as **authoritative** for the current internal configuration, but always cross‑check against the user’s description of external wiring and components.
- Always preserve unknown keys when editing state; future firmware versions may add fields.
- Prefer using high‑level MicroPython APIs (`connect`, `disconnect`, `dac_set`, `overlay_set`, etc.) for incremental changes, and use state JSON editing for **bulk** or **offline** transformations (import/export, heavy refactoring, or pre‑computed overlays).

