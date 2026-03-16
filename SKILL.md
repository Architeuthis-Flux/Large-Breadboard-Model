---
name: jumperless-v5
description: >-
  Operates a Jumperless V5 breadboard for hardware-in-the-loop prototyping and
  debugging. Uses MicroPython REPL to route connections, set rails/DACs, perform
  measurements, control GPIO/OLED/LED overlays, and run guided test scripts. Use
  when the user mentions Jumperless, breadboard wiring, circuit testing, hardware
  debugging, or voltage/current/resistance measurements on physical hardware.
---

# Jumperless V5 Skill

This skill controls real Jumperless hardware via MicroPython REPL.

## Jumperless At A Glance

Jumperless V5 is a smart breadboard that can:

- Virtually wire nodes (`connect`, `disconnect`) without moving jumpers.
- Measure voltages/currents using onboard ADC/INA paths.
- Set rails/DACs, drive GPIO/PWM, and render OLED/LED guidance.
- Run human-in-the-loop procedures with probe/clickwheel step gating.

Minimal patterns:

```python
# Basic connection
connect(1, D4)
```

```python
# Basic measurement
connect(ADC0, 5)
print(adc_get(0))
disconnect(ADC0, -1)
```

## Start Here (Progressive Disclosure)

Read `reference/progressive-disclosure-map.md` first, choose one task lane, and load only those files.

## Non-negotiable behavior

- Treat this as an **active hardware tool**, not a passive advisor.
- By default, perform routing/measurement actions directly on Jumperless using REPL commands.
- Ask the user only for **physical actions** (place/move parts, press probe/clickwheel).
- Before risky operations, snapshot with `get_state()` and restore when needed.
- Never assume external wiring is known; verify with measurements.

## Fast start (host)

```bash
pip install pyserial
python scripts/jumperless.py detect
python scripts/jumperless.py exec "print('ok from jumperless')"
```

Prefer these execution modes:
- Short command: `python scripts/jumperless.py exec "print(adc_get(0))"`
- Multi-line script: `python scripts/jumperless.py exec --file scripts/run_test.py`
- Piped script: `python scripts/jumperless.py exec --stdin < scripts/run_test.py`

Do **not** cram long multi-line logic into shell-quoted one-liners unless necessary.

## Guided step mode (single long script + button continue)

Use built-in guided execution when the task is procedural:

```bash
python scripts/jumperless.py guide --file steps.txt
```

- `steps.txt` format: one non-empty line per step.
- Device script prints each step, renders on OLED, then waits for continue:
  - first choice: `probe_button(True)`
  - fallback: `clickwheel_get_button()`

Use this for assembly/test checklists so the user advances each stage by pressing hardware controls.

## Workflow selection

Choose one workflow, run it, then return results:

1. **Connectivity / rewiring task**
   - Read: `reference/node-map.md`
   - Then: `reference/api/connections-routing.md`
2. **Measurement task**
   - Read: `scripts/measurements.py`
   - Then: `reference/api/measurements-power.md`
3. **Visual guidance task**
   - Read: `scripts/animations.py`
   - Then: `reference/api/ui-interaction-system.md`
4. **State surgery / large edits**
   - Read: `reference/state-format.md`
   - Then: `reference/api/state-nets-filesystem.md`

Only load `reference/api-reference.md` when a task spans multiple API domains.
For transport/hanging execution issues, load `reference/repl-runtime-playbook.md`.

## Core command patterns

```bash
# Snapshot state
python scripts/jumperless.py state

# Execute a robust multi-line script from file
python scripts/jumperless.py exec --file scripts/session.py

# List device filesystem
python scripts/jumperless.py fs
```

## Safety profiles

- **Beginner**: conservative changes, frequent explanation, auto-snapshot/restore.
- **Advanced**: fewer prompts, allow temporary rail/DAC rewiring for tests.
- **God mode**: broad autonomy, still announce assumptions before destructive changes.

Default to **Beginner** unless user confidence and context indicate otherwise.

## Performance and context discipline

- Keep reasoning local to the active workflow.
- Avoid loading all references; read only required files.
- Prefer deterministic helper scripts over ad-hoc generated command strings.
- Use concise execution scripts and return measured results, not long planning text.

## File map

- Host transport and REPL runner: `scripts/jumperless.py`
- Measurement helpers: `scripts/measurements.py`
- LED/OLED animation helpers: `scripts/animations.py`
- Progressive routing map: `reference/progressive-disclosure-map.md`
- REPL/runtime playbook: `reference/repl-runtime-playbook.md`
- Full deep guide (extension/migration): `reference/deep-dive/full-skill-guide.md`
- API split: `reference/api/connections-routing.md`
- API split: `reference/api/measurements-power.md`
- API split: `reference/api/state-nets-filesystem.md`
- API split: `reference/api/ui-interaction-system.md`
- API monolith (legacy fallback): `reference/api-reference.md`
- Node IDs/aliases: `reference/node-map.md`
- Hardware behavior: `reference/hardware-guide.md`
- State JSON schema: `reference/state-format.md`
- Design context/roadmap: `reference/vision.md`

