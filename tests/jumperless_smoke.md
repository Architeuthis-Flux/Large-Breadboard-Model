Use the Jumperless V5 skill to:
1. Detect the Micropython REPL port
2. Run a command that prints the Micropython prompt and 'ok from jumperless' on both the OLED and terminal
3. Drive an LED using the internal crossbar resistance
4. Guide the user through wiring a 555 timer circuit with OLED prompts and LED overlays

## Host-side Python/shell sequence

```bash
# 1. Ensure dependency is installed
pip install pyserial

# 2. Detect the MicroPython REPL port and cache it in .jumperless_port
python scripts/jumperless.py detect

# 3. Smoke test: print prompt + message on OLED and terminal (safe file-based execution)
python scripts/jumperless.py exec --file tests/smoke_oled_terminal.py

# 4. LED test: use crossbar resistance as current limit
python scripts/jumperless.py exec --file tests/smoke_led_drive.py

# 5. Run single-script interactive 555 guide (each step waits for probe/clickwheel button)
python scripts/jumperless.py guide --file tests/steps_555.txt
```