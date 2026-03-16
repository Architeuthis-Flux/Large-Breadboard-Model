# Example: Measuring Resistance Between Two Nodes

This walkthrough shows how an agent can use the Jumperless V5 to estimate the resistance between two breadboard nodes using the DAC and INA current sensor, via the `measurements.py` helper.

## Prerequisites

- The `measurements.py` module has been uploaded to the Jumperless filesystem, e.g. as `lib/measurements.py`.
- The host can talk to the MicroPython REPL, e.g. using:

```bash
python scripts/jumperless.py exec "import sys; print(sys.ps1)"
```

## 1. User describes the circuit

Ask the user where the unknown resistor is placed. For example:

- “I have a resistor between row 19 and row 11.”

Map this to nodes:

- `node_a = 19`
- `node_b = 11`

## 2. Upload and import helper (if not already present)

From the host, you can upload `scripts/measurements.py` once to the device (path may vary by toolchain). After it is on the filesystem, in MicroPython:

```python
from measurements import measure_resistance
```

## 3. Run a resistance measurement

This call uses DAC1 and INA sensor 0 by default:

```python
from measurements import measure_resistance

R = measure_resistance(19, 11, dac_channel=1, sensor=0, set_voltage=3.0)
print("Approximate resistance between 19 and 11:", R, "ohms")
```

What happens internally:

1. `dac_set(1, 3.0)` sets DAC1 to ~3 V.
2. `connect(DAC1, ISENSE_PLUS)` and `connect(ISENSE_MINUS, 19)` insert the 2 Ω shunt in series with the unknown resistor.
3. `connect(11, GND)` ties the far end of the resistor to ground.
4. `ina_get_bus_voltage(0)` and `ina_get_current(0)` read bus voltage and current.
5. The helper computes `R ≈ V / I` and returns it.
6. All temporary connections are removed if `disconnect_after=True`.

Because of series resistance in the crossbar and the shunt itself, this value is **approximate** but sufficient for many debugging tasks.

## 4. Interpreting the result

Compare `R` to the expected resistor value:

- If the user expected ~1 kΩ and you measure ~1.1 kΩ–1.3 kΩ, that’s likely acceptable given crossbar and shunt resistance.
- If you measure something wildly different (e.g. ~0 Ω or >1 MΩ), consider:
  - Is the resistor actually present between those rows?
  - Is there another path (wire) in parallel or series?
  - Are there other components on that net that change the effective resistance?

In those cases, inspect the internal state:

```python
print_nets()
print_bridges()
```

…and reconcile it with the user’s description of external wiring.

