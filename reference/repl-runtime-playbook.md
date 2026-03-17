# REPL and Runtime Playbook

Use this when execution is flaky, slow, or malformed.

## Preferred Execution Modes

1. Short command:

```bash
python scripts/jumperless.py exec "print(adc_get(0))"
```

2. Long script (preferred):

```bash
python scripts/jumperless.py exec --file scripts/session.py
```

3. Piped script:

```bash
python scripts/jumperless.py exec --stdin < scripts/session.py
```

Avoid large shell-quoted multi-line snippets.

## Guided Human-In-The-Loop Mode

```bash
python scripts/jumperless.py guide --file tests/steps_555.txt
```

- One non-empty line per step.
- Each step prints and OLED-renders.
- Continue uses:
  - `probe_button(True)` first
  - `clickwheel_get_button()` fallback

## Updating a Running Loop Script

Loop scripts run on the **device** in MicroPython. The host `exec` process exits after sending the script — the serial port is free. The MicroPython loop keeps running on the Jumperless itself.

### Procedure

1. **Edit the script file** on the host with the desired changes.
2. **Run `exec` with the updated file.** `enter_raw_repl()` sends `\x03\x03` (double Ctrl-C) to interrupt whatever is running on the device before sending new code. No process killing needed.
3. **Start the new script with a cleanup header** so any state left by the interrupted script is cleared:

```python
import time
nodes_clear()
overlay_clear_all()
oled_clear()
time.sleep(0.05)
```

## Failure Recovery

### Timeout in `exec`

- Re-run using `--file`.
- Increase timeout:

```bash
python scripts/jumperless.py exec --file scripts/session.py --timeout 20
```

### Port confusion

```bash
python scripts/jumperless.py detect
python scripts/jumperless.py --port /dev/cu.usbmodemJLV5port5 exec --file scripts/session.py
```

### State safety

Before risky rewiring:

```bash
python scripts/jumperless.py state
```

Inside device script, keep a baseline:

```python
baseline = get_state()
# ... changes ...
set_state(baseline)
```

## Runtime Discipline

- Execute deterministic scripts, not ad-hoc generated command chains.
- Keep each script focused: one objective per run.
- Report measured values and actions taken.
- Ask user only for physical interactions (placing parts, pressing buttons).
