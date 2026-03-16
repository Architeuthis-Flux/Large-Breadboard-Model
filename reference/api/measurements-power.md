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

## Escalate To

- `scripts/measurements.py` for reusable routines and sweeps.
- `reference/hardware-guide.md` for shunt and crossbar resistance caveats.
