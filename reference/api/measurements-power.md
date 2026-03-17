# API: Measurements and Power

Use this file for voltage/current/resistance tasks and rail/DAC control.

## Power and DAC

- `dac_set(channel, voltage)` (`DAC0`, `DAC1`, `TOP_RAIL`, `BOTTOM_RAIL`)
- `dac_get(channel)`

Range is typically about `-8.0` to `+8.0` V.

## ADC

- `adc_get(channel)`
  - `ADC0` to `ADC3`: +-8V range
  - `ADC4`: 5V range
  - `ADC7` / `PROBE`: probe channel

Always route the ADC node before reading.

## INA Current/Power

- `ina_get_current(sensor)`
- `ina_get_voltage(sensor)`
- `ina_get_bus_voltage(sensor)`
- `ina_get_power(sensor)`

`ISENSE_PLUS` and `ISENSE_MINUS` are shunt endpoints; use in series.

## Minimal Patterns

```python
# Rail setpoint
dac_set(TOP_RAIL, 3.3)
print(dac_get(TOP_RAIL))
```

```python
# Voltage at row 5
connect(ADC0, 5)
print(adc_get(0))
disconnect(ADC0, -1)
```

```python
# Resistance estimate via DAC + INA
connect(ISENSE_PLUS, DAC1)
connect(ISENSE_MINUS, 5)
dac_set(1, 3.0)
v = ina_get_bus_voltage(1)
i = ina_get_current(1)
print(v / i if i else "inf")
```

## Advanced: baseline-corrected resistance measurement (INA + ADC)

Use this when you want to estimate the resistance between two breadboard rows using the on-board shunt and current sensor, while keeping the measurement current in a good range across different resistor values.

### Topology

- Unknown resistor between `ROW_A` and `ROW_B` (breadboard rows).
- Series chain: `DAC1 -> ISENSE_PLUS -> shunt -> ISENSE_MINUS -> ROW_A -> R_unknown -> ROW_B -> GND`.
- ADC senses the voltage at `ROW_A` (high side of the resistor).
- INA0 measures current through the shunt.

### Stepped DAC setpoint

Keep the INA in a comfortable range by adapting the DAC voltage based on the last measured resistance \(R_{\text{prev}}\):

- If no prior reading: `v_set = 2.0`
- If `R_prev < 200 Ω`: `v_set = 0.5`
- If `200 Ω ≤ R_prev < 1 kΩ`: `v_set = 1.5`
- If `1 kΩ ≤ R_prev < 5 kΩ`: `v_set = 2.5`
- Else: `v_set = 4.0`

You can tune these thresholds depending on noise and linearity; the goal is to avoid both a “microamp” regime for big resistors and a “tens of mA” regime for small ones.

### Baseline-corrected measurement steps

Assume use of `INA0`, `DAC1`, and `ADC0`, and that nothing else is wired to `ROW_A`/`ROW_B` except the resistor under test.

1. **Clear routing**
   - `nodes_clear()`

2. **Set DAC**
   - Choose `v_set` from the ladder above (using any stored `R_prev`).
   - `dac_set(1, v_set)`  (or `dac_set(DAC1, v_set)`).

3. **Baseline INA current (ROW_B floating)**
   - Route:
     - `connect(DAC1, ISENSE_PLUS)`
     - `connect(ISENSE_MINUS, ROW_A)`
     - Leave `ROW_B` floating.
   - Wait ~50 ms (`time.sleep(0.05)`).
   - Sample INA0 current N times (e.g. 16–32):
     - `i0_samples = [ina_get_current(0) for _ in range(N)]`
     - `i0_avg = sum(i0_samples) / len(i0_samples)`
   - Disconnect:
     - `disconnect(DAC1, -1)`
     - `disconnect(ISENSE_PLUS, -1)`
     - `disconnect(ISENSE_MINUS, -1)`
     - `disconnect(ROW_A, -1)`

4. **Loaded current and node voltage**
   - Route:
     - `connect(DAC1, ISENSE_PLUS)`
     - `connect(ISENSE_MINUS, ROW_A)`
     - `connect(ROW_B, GND)`
     - `connect(ADC0, ROW_A)`
   - Wait ~50 ms.
   - Sample N times:
     - `v_samples.append(adc_get(0))`
     - `i1_samples.append(ina_get_current(0))`
   - Compute:
     - `v_avg  = sum(v_samples) / len(v_samples)`
     - `i1_avg = sum(i1_samples) / len(i1_samples)`
   - Disconnect all of the above again.

5. **Compute net current and resistance**
   - `i_net = i1_avg - i0_avg`
   - If `i_net <= 0`, treat as invalid.
   - `R_est = v_avg / i_net`
   - Reject obviously bogus values (e.g. `< 1 Ω` or `> 1e7 Ω`) for this mode.
   - On success, update `R_prev = R_est` for the next call so the DAC ladder can adapt.

6. **Display result (optional)**
   - Terminal:
     - `print("R≈{:.0f}Ω (v_avg={}, i0_avg={}, i1_avg={}, i_net={})".format(R_est, v_avg, i0_avg, i1_avg, i_net))`
   - OLED:
     - `oled_clear()`
     - `oled_print("Row {}-{}:".format(ROW_A, ROW_B))`
     - `oled_print("R≈{:.0f}Ω".format(R_est))`

### Continuous monitor variant

For a “live ohmmeter” between fixed rows (e.g. 1 and 31), wrap the above into a loop:

```python
R_prev = None
while True:
    R_est = measure_resistance_once(ROW_A=1, ROW_B=31, R_prev=R_prev)
    if R_est is not None:
        R_prev = R_est
    time.sleep(0.5)
```

Where `measure_resistance_once(...)` implements the steps above and returns `R_est` or `None`.

## Escalate To

- `scripts/measurements.py` for reusable routines and sweeps.
- `reference/hardware-guide.md` for shunt and crossbar resistance caveats.
