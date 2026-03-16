# Large Breadboard Model – Jumperless V5 Agent Skill

## Hey I totally haven't tested this and it's probably not usable yet but I'm putting it up in case someone wants to try this out and tell me why it sucks.

This repository contains a **Jumperless V5 Agent Skill** that teaches an LLM how to:

- Discover and connect to a Jumperless V5 over USB
- Control the MicroPython REPL on the `JL Micropython REPL` port
- Create and remove virtual jumpers between breadboard nodes
- Set rails and DACs, read ADCs and current sensors
- Drive GPIOs and PWM
- Render guidance and animations on the breadboard LEDs

It follows the [Agent Skills](https://agentskills.io/) open standard and is compatible with tools like Cursor, Claude Code, and others that support `SKILL.md` skills.

---

## Repository structure

```text
Large Breadboard Model/
├── SKILL.md                # Main skill entrypoint (Agent Skills / Cursor / Claude Code)
├── reference/              # Detailed reference docs
│   ├── api-reference.md    # MicroPython API (jumperless module)
│   ├── node-map.md         # Node numbering and aliases
│   ├── hardware-guide.md   # Hardware behavior and limits
│   ├── state-format.md     # JSON format returned by get_state()
│   └── vision.md           # Design goals and roadmap
├── scripts/
│   ├── jumperless.py       # Host-side helper (pyserial, raw REPL, port detect)
│   ├── measurements.py     # Device-side measurement helpers
│   └── animations.py       # Device-side overlay animations
└── examples/
    ├── measure-resistance.md
    ├── circuit-debugging.md
    └── led-animations.md
```

---

## Installation

### For Cursor

Clone this repository into your personal Cursor skills directory:

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone https://github.com/your-org-or-user/large-breadboard-model.git jumperless-v5
```

Cursor will automatically discover `jumperless-v5/SKILL.md` and use it when relevant.

### For Claude Code

Clone into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/your-org-or-user/large-breadboard-model.git jumperless-v5
```

Claude Code will expose the skill as `/jumperless-v5` (or let Claude invoke it automatically based on the description).

> Adjust the Git URL above to match where you host this repo (GitHub, local path, etc.).

---

## Host requirements

On the machine connected to the Jumperless V5:

- Python 3.8+
- `pyserial`:

```bash
pip install pyserial
```

The host helper script lives at `scripts/jumperless.py`.

---

## Quick start

1. **Connect your Jumperless V5** via USB.
2. **Detect the MicroPython REPL port**:

   ```bash
   cd "/Users/kevinsanto/Documents/GitHub/Large Breadboard Model"
   python scripts/jumperless.py detect
   ```

   This prints the detected port path (e.g. `/dev/cu.usbmodemJLV5port5` on macOS or `COM7` on Windows) and caches it in `.jumperless_port`.

3. **Run a simple REPL command**:

   ```bash
   python scripts/jumperless.py exec "print('hello from jumperless')"
   ```

4. **Fetch the current state**:

   ```bash
   python scripts/jumperless.py state
   ```

   This prints the JSON returned by `get_state()` to stdout.

From within an LLM‑driven environment (Cursor, Claude Code, etc.), the agent can call these shell commands when this skill is active.

---

## Device-side helpers

The `scripts/measurements.py` and `scripts/animations.py` files are intended to be uploaded to the Jumperless filesystem (for example under `/python_scripts/lib/`). Once there, you can do:

```python
from measurements import measure_voltage, measure_resistance
from animations import highlight_row, place_here
```

Examples of how to use these helpers are in the `examples/` directory:

- `examples/measure-resistance.md` – using DAC + INA to estimate resistance
- `examples/circuit-debugging.md` – debugging a voltage divider
- `examples/led-animations.md` – guiding users with LED overlays

---

## Documentation

For full hardware and API documentation, see:

- Jumperless docs: `https://docs.jumperless.org/`
- MicroPython API reference (this repo): `reference/api-reference.md`
- Hardware guide and safety notes: `reference/hardware-guide.md`
- State JSON format: `reference/state-format.md`

