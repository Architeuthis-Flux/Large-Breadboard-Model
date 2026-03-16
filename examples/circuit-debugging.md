# Example: Debugging a Voltage Divider

This example shows how to debug a simple voltage divider on the Jumperless V5 using `get_state()`, net inspection, and ADC measurements.

## Scenario

The user intends to build a 2:1 divider from `TOP_RAIL` (set to 6 V) to `GND` using 2 kΩ + 2 kΩ resistors, measuring ~3 V at the midpoint.

They report:

> “I connected one end of the first resistor to row 8, the other end to row 6, and the second resistor from row 6 to row 5, with row 8 on TOP_RAIL and row 5 on GND. But I’m not reading 3 V at row 6.”

## 1. Understand the intended schematic

The intended circuit:

- `TOP_RAIL` → R1 (2 kΩ) → node M → R2 (2 kΩ) → `GND`
- Measurement node M should be at ~3 V when `TOP_RAIL` is 6 V.

Mapping to nodes:

- `node_top = 8`
- `node_mid = 6`
- `node_bot = 5`

## 2. Inspect internal state

First, capture and print the state:

```python
import json
s = get_state()
state = json.loads(s)

print("Power:", state["power"])
for net in state["nets"]:
    print(net["index"], net["name"], net.get("nodes"))
```

Check:

- Is there a net that includes `TOP_R` and `8`?
- Is there a net that includes `GND` and `5`?
- Is there a net that includes `6` and both resistor pins as described?

If, for example, `6` appears on the same net as `TOP_R` and `8`, then R1 is probably bypassed or miswired.

You can also use the higher‑level helpers:

```python
print_nets()
print_bridges()
```

These display nets and individual bridges in a more human‑friendly way.

## 3. Verify connections

Use connection checks:

```python
if not is_connected(TOP_RAIL, 8):
    print("Row 8 is not tied to TOP_RAIL")

if not is_connected(GND, 5):
    print("Row 5 is not tied to GND")

if not is_connected(8, 6):
    print("First resistor may not be between 8 and 6")

if not is_connected(6, 5):
    print("Second resistor may not be between 6 and 5")
```

Mismatch messages indicate that the virtual wiring does not match the intended schematic, even if the user placed components physically.

## 4. Measure the midpoint

Assuming the wiring looks correct, measure the voltage at `node_mid`:

```python
from measurements import measure_voltage

v_mid = measure_voltage(6, adc_channel=0, disconnect_after=True)
print("Measured midpoint voltage:", v_mid)
```

If `TOP_RAIL` is 6 V, expect `v_mid` ≈ 3 V. If it’s significantly different:

- Verify `state["power"]["top_rail"]` is actually `6.0`.
- Consider crossbar and shunt resistance; ideal 3.0 V may show up as something like 2.8–3.2 V under load.

## 5. Suggest fixes

Based on the findings:

- If the mid node is on the same net as `TOP_RAIL`, suggest moving the resistor lead so the divider actually has two series resistors.
- If both resistors are correctly wired but the supply is not 6 V, suggest:

```python
dac_set(TOP_RAIL, 6.0)
```

- If measurements are wildly off, ask whether there are additional wires or loads attached to those rows, or if a resistor value was mis‑read (e.g. 200 Ω instead of 2 kΩ).

## 6. Optional: save a known-good state

Once the divider is verified, the agent can suggest saving the configuration:

```python
nodes_save(0)  # or another slot index
```

…and document that the user can later restore it with:

```python
switch_slot(0)
```

