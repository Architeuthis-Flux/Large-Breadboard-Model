# Jumperless Progressive Disclosure Map

Use this file first. Pick one task lane, then load only the referenced files.

## Task Lanes

1. **Port / REPL transport issues**
   - Read: `scripts/jumperless.py`
   - Then: `reference/repl-runtime-playbook.md`

2. **Node routing / net debugging**
   - Read: `reference/node-map.md`
   - Then: `reference/api/connections-routing.md`

3. **Measurement workflows (V/I/R, sweeps)**
   - Read: `scripts/measurements.py`
   - Then: `reference/api/measurements-power.md`
   - Then: `reference/hardware-guide.md` (limits + shunt + resistance)

4. **Guided human assembly flows**
   - Read: `scripts/jumperless.py` (`guide` command)
   - Then: `scripts/animations.py`

5. **State import/export and batch edits**
   - Read: `reference/state-format.md`
   - Then: `reference/api/state-nets-filesystem.md`

6. **UI, overlays, and guided interaction**
   - Read: `reference/api/ui-interaction-system.md`
   - Then: `scripts/animations.py`

7. **Skill evolution / design intent**
   - Read: `reference/vision.md`
   - Optional: `reference/deep-dive/full-skill-guide.md`

## Loading Rules

- Do not read all reference files by default.
- Load one lane, execute, and report.
- If blocked, load exactly one additional file.
- Prefer helper scripts over generated one-liners.
- For long execution logic, use `exec --file` or `exec --stdin`.

## Escalation Rules

- If REPL commands hang or parse incorrectly: switch to `--file` mode.
- If result conflicts with expected electronics behavior: read `reference/hardware-guide.md`.
- If connections look right but behavior is wrong: inspect `get_state()` and external wiring assumptions separately.
