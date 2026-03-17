# Electronics Reference

Quick-lookup reference for working with circuits on the Jumperless. Use these to interpret measurements, plan tests, size components, and explain results without reasoning from scratch.

---

## Ohm's Law and power

```
V = I × R       (voltage = current × resistance)
I = V / R       (current = voltage / resistance)
R = V / I       (resistance = voltage / current)
P = V × I       (power in watts)
P = V² / R      (power from voltage and resistance)
P = I² × R      (power from current and resistance)
```

---

## Series and parallel

**Resistors in series:** `R_total = R1 + R2 + R3 ...`  
Current is the same through all; voltages add.

**Resistors in parallel:** `1/R_total = 1/R1 + 1/R2 ...`  
For two: `R_total = (R1 × R2) / (R1 + R2)`  
Voltage is the same across all; currents add.

**Capacitors in series:** `1/C_total = 1/C1 + 1/C2 ...`  
**Capacitors in parallel:** `C_total = C1 + C2 + C3 ...`

---

## Voltage divider

```
Vout = Vin × R2 / (R1 + R2)
```

R1 connects Vin to Vout; R2 connects Vout to GND. Vout sits between Vin and GND proportional to R2's share of the total resistance. Load resistance in parallel with R2 will pull Vout down — keep load impedance >> R2 for accuracy. This also applies when the crossbar's own series resistance acts as an unintended R1.

---

## Kirchhoff's laws

**KVL** — voltages around any closed loop sum to zero. Use this to verify that expected drops across resistors match the supply voltage minus measured node voltages.

**KCL** — currents into a node sum to zero. If two paths feed a node, the outgoing current equals their sum. Use this when interpreting INA readings with multiple parallel paths.

---

## RC time constant

```
τ = R × C       (seconds)
```

Voltage across a charging capacitor: `V(t) = Vfinal × (1 − e^(−t/τ))`  
Reaches 63.2% of final voltage at t = τ, 99.3% at t = 5τ.  
Discharging: `V(t) = Vinitial × e^(−t/τ)`

The crossbar has 20–80Ω series resistance depending on path stacking (see **Crossbar resistance** below), so any capacitor on the board sees that as part of its R even without an external resistor.

---

## Crossbar resistance

The CH446Q crossbar fabric is not a perfect wire. The series resistance of a routed path depends on how many parallel paths the firmware stacks:

| `connect()` call | Paths stacked | Effective resistance |
|---|---|---|
| `connect(a, b, duplicates=0)` | 1 (single path) | ~80 Ω |
| `connect(a, b)` default | firmware decides (typically 2–4) | ~20–40 Ω |
| Rail/supply connections | firmware stacks more aggressively | ~20 Ω or less |

**Rule of thumb:** with default `connect()`, assume ~20–40Ω in series. With `duplicates=0` (forced single path), assume ~80Ω.

This matters for:
- **Voltage measurements under load** — the series resistance causes sag. A 3.3V rail measured through the crossbar with a 330Ω load will read lower than 3.3V.
- **Resistance measurements** — always subtract the known crossbar contribution or use a baseline measurement.
- **RC circuits** — the crossbar R is in series with any capacitor placed on the board.
- **Current capacity** — stacking more paths reduces resistance and allows more current before significant drop. Use default `connect()` (not `duplicates=0`) for power paths.

---

## Logic levels

| Family | Logic LOW | Logic HIGH |
|---|---|---|
| 5V TTL/CMOS | < 0.8V | > 2.0V |
| 3.3V CMOS | < 0.8V | > 2.0V |
| 1.8V CMOS | < 0.5V | > 1.2V |

**Jumperless-specific:** GPIO and UART pins are **3.3V logic**. Connecting a 5V logic output directly to them without level shifting can damage the RP2350. For the Arduino Nano header, signals are 5V unless the Nano is a 3.3V variant (Nano ESP32, Nano RP2040 Connect).

---

## Current limiting for LEDs

```
R = (Vsupply − Vforward) / Iforward
```

Typical values:
- Vforward ≈ 2.0V (red/yellow), 3.0–3.4V (blue/white/green)
- Iforward ≈ 10–20 mA for standard LEDs, 1–5 mA for indicator brightness

Always use a series resistor — never connect an LED directly across a supply. Remember to add crossbar resistance (~20–40Ω default) to your R calculation if routing through the board.

---

## Pull-up / pull-down resistors

Defines the resting logic level of a signal line when nothing is actively driving it:
- **Pull-up:** resistor from signal to VCC → rests HIGH
- **Pull-down:** resistor from signal to GND → rests LOW

Common values: 4.7kΩ–10kΩ. Too low wastes current and loads the driver; too high is slow and noise-prone. The Jumperless GPIO pins have configurable internal pull-up/pull-down via `gpio_set_pull()` — no external resistor needed for logic inputs.

---

## IC pin numbering conventions

### DIP (through-hole) packages

The most common package on breadboards:

- Pin 1 is marked with a **dot**, **notch**, or **chamfer** on one end.
- Looking at the top with the notch at the top-left, **pin 1 is top-left**.
- Numbering goes **counterclockwise**: down the left side, then up the right side.

```
         ┌──────┐
  pin 1 ─┤ •    ├─ pin 8   (8-DIP)
  pin 2 ─┤      ├─ pin 7
  pin 3 ─┤      ├─ pin 6
  pin 4 ─┤      ├─ pin 5
         └──────┘
```

On a breadboard, the IC straddles the center gap: pins 1–N/2 on one side, pins N/2+1–N on the other. Pin 1 at the top-left. For a 14-DIP: pins 1–7 go down one side, pins 8–14 go up the other.

**SOP/SOIC (SMD)** — same counterclockwise rule, pin 1 marked with a dot or chamfer on the body.

### Common 8-DIP ICs

| IC | Pin 1 | Pin 4 | Pin 8 | Function |
|---|---|---|---|---|
| NE555 | GND | RESET | VCC | Timer |
| LM358 / TL072 | OUT1 | VCC− | VCC+ | Dual op-amp |
| LM741 | OFFSET N1 | VCC− | VCC+ | Single op-amp |
| ATtiny85 | RESET | GND | VCC | MCU |
| 24Cxx EEPROM | A0 | GND | VCC | I2C memory |

### Common 14-DIP ICs

| IC | Pin 7 | Pin 14 | Function |
|---|---|---|---|
| LM324 | GND | VCC | Quad op-amp |
| NE556 | GND | VCC | Dual 555 timer |
| 74HC04 | GND | VCC | Hex inverter |
| 74HC08 | GND | VCC | Quad AND |
| 74HC14 | GND | VCC | Hex Schmitt inverter |
| 74HC00 | GND | VCC | Quad NAND |

### Common 16-DIP ICs

| IC | Pin 8 | Pin 16 | Function |
|---|---|---|---|
| 74HC595 | GND | VCC | 8-bit shift register |
| 74HC164 | GND | VCC | 8-bit shift register |
| CD4017 | GND | VCC | Decade counter |
| MAX7219 | GND | VCC | LED driver |
| 74HC138 | GND | VCC | 3-to-8 decoder |

Power pins are almost always at the corners (GND at one end, VCC at the other). **When in doubt, measure before connecting rails** — use ADC to confirm which pin is which before routing power.

---

## Decoupling capacitors

Place 100nF ceramic caps between VCC and GND as close to IC power pins as possible. On the Jumperless, route the supply to the IC's VCC row (`connect(ic_vcc_row, SUPPLY_5V)`), and the user places the cap physically at that row. Without decoupling, fast switching ICs cause supply glitches that corrupt nearby analog measurements.

---

## Interpreting unexpected measurements

| Symptom | Likely cause |
|---|---|
| Floating / noisy ADC reading | ADC node not connected to a defined voltage; floating input |
| Voltage lower than expected | Crossbar series R (20–80Ω) + load forming a divider; or rail not set correctly |
| Voltage higher than expected | Open circuit; ADC input pulled toward a floating supply via parasitic path |
| Zero current (INA) | Open circuit in series path; shunt not actually in the current path |
| Negative current (INA) | ISENSE_PLUS/MINUS polarity reversed — swap them |
| R much lower than expected | Parallel path through crossbar routing or another component on same net |
| R much higher than expected | Poor contact; oxidized breadboard hole; or open connection at a pin |
| R reading unstable / drifting | Insufficient settling time after connect(); add `time.sleep(0.05)` |
| INA reads current with no load | Leakage through crossbar; take baseline measurement with load disconnected and subtract |
