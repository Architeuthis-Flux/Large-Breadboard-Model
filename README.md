# Large Breadboard Model – Jumperless V5 automation

This is the **canonical repository for automating a Jumperless V5** from scripts
and LLM agents. One checkout gives you everything:

| Path | What it is |
|------|------------|
| `SKILL.md` + `reference/` + `examples/` | [Agent Skill](https://agentskills.io/) for Cursor / Claude Code |
| `scripts/jumperless.py` | Host REPL helper (detect, exec, state, fs, guide) |
| `mcp/` *(git submodule)* | [jumperless-mcp](https://github.com/LesbianVelociraptor/jumperless-mcp) — Rust MCP server + resident Python library |

It teaches an LLM (or you) how to discover and connect to a Jumperless V5 over
USB, route virtual jumpers, set rails/DACs, read ADCs and current sensors, drive
GPIO/PWM, and render guidance on the breadboard LEDs.

---

## Which tool do I use?

| You want | Use |
|----------|-----|
| Persistent typed tools in an **MCP client** (Claude Desktop, Cursor MCP) | `mcp/` — build/install **jumperless-mcp** |
| An **Agent Skill** that drives the board through host shell scripts | `SKILL.md` + `scripts/jumperless.py` |
| **Fast read-only telemetry** with no Python | USBSer3 backchannel on port 7 (`:help`, `:gpio`, `:leds`, …) |

The skill and the MCP server share the same MicroPython API surface. Pick the
one your client supports best. **Do not run the MCP server and `jumperless.py`
at the same time** — both hold the USB port exclusively.

Full automation overview on the docs site:
<https://docs.jumperless.org/07.5-automation/>.

---

## USB ports

The Jumperless enumerates as four USB CDC serial interfaces:

| Port | macOS suffix | Role |
|------|--------------|------|
| 1 | `JLV5port1` | Main terminal, menu, `>` one-liner Python |
| 3 | `JLV5port3` | Arduino UART passthrough |
| 5 | `JLV5port5` | MicroPython Raw REPL (**primary transport** for this repo) |
| 7 | `JLV5port7` | USBSer3 machine backchannel (`:help` YAML, `:cmds`, status verbs) |

`scripts/jumperless.py detect` auto-finds the Raw REPL port and caches it in
`.jumperless_port`.

---

## Repository structure

```text
Large-Breadboard-Model/
├── SKILL.md                # Main skill entrypoint (Agent Skills / Cursor / Claude Code)
├── reference/              # Progressive-disclosure reference docs
│   ├── api-reference.md    # MicroPython API (jumperless module)
│   ├── api/                # API split by domain
│   ├── node-map.md         # Node numbering and aliases
│   ├── hardware-guide.md   # Hardware behavior and limits
│   ├── state-format.md     # JSON format returned by get_state()
│   └── ...
├── scripts/
│   ├── jumperless.py       # Host-side helper (pyserial, raw REPL, port detect)
│   ├── measurements.py     # Device-side measurement helpers
│   └── animations.py       # Device-side overlay animations
├── examples/               # Worked examples (measurement, debugging, LED guidance)
├── mcp/                    # git submodule → LesbianVelociraptor/jumperless-mcp
└── .gitmodules
```

---

## Installation

Clone **with submodules** so the `mcp/` server comes along:

```bash
git clone --recurse-submodules \
  https://github.com/Architeuthis-Flux/Large-Breadboard-Model.git
```

Already cloned without `--recurse-submodules`?

```bash
git submodule update --init --recursive
```

### As an Agent Skill (Cursor)

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone --recurse-submodules \
  https://github.com/Architeuthis-Flux/Large-Breadboard-Model.git jumperless-v5
```

Cursor discovers `jumperless-v5/SKILL.md` automatically.

### As an Agent Skill (Claude Code)

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone --recurse-submodules \
  https://github.com/Architeuthis-Flux/Large-Breadboard-Model.git jumperless-v5
```

Claude Code exposes it as `/jumperless-v5` (or invokes it automatically from the
skill description).

### As an MCP server

```bash
cd mcp
cargo install --path .      # or grab a release binary
```

Point your MCP client at the built binary:

```json
{
  "mcpServers": {
    "jumperless": {
      "command": "/path/to/Large-Breadboard-Model/mcp/target/release/jumperless-mcp"
    }
  }
}
```

See `mcp/README.md` for the full tool list and lifecycle.

---

## Host requirements

For the skill / `jumperless.py`:

- Python 3.8+
- `pyserial`: `pip install pyserial`

For the MCP server: a Rust toolchain (`cargo`), unless you use a prebuilt binary.

---

## Quick start (skill / scripts)

1. **Connect your Jumperless V5** via USB.
2. **Detect the REPL port** (run from the skill root):

   ```bash
   python scripts/jumperless.py detect
   ```

   Prints the detected port (e.g. `/dev/cu.usbmodemJLV5port5` or `COM7`) and
   caches it in `.jumperless_port`.

3. **Run a REPL command:**

   ```bash
   python scripts/jumperless.py exec "print('hello from jumperless')"
   ```

4. **Fetch current state:**

   ```bash
   python scripts/jumperless.py state
   ```

From within an LLM-driven environment (Cursor, Claude Code, …), the agent runs
these shell commands directly when the skill is active.

---

## Device-side helpers

`scripts/measurements.py` and `scripts/animations.py` are meant to be uploaded
to the Jumperless filesystem (e.g. under `/python_scripts/lib/`):

```python
from measurements import measure_voltage, measure_resistance
from animations import highlight_row, place_here
```

See `examples/` for worked walkthroughs (resistance measurement, voltage-divider
debugging, LED placement guidance).

---

## Documentation

- Jumperless docs: <https://docs.jumperless.org/>
- Automation overview (which tool, ports, MCP, backchannel): <https://docs.jumperless.org/07.5-automation/>
- MicroPython API reference (canonical): <https://docs.jumperless.org/09.5-micropythonAPIreference/>
- In-repo reference: `reference/api-reference.md`, `reference/hardware-guide.md`, `reference/state-format.md`
