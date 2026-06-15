# Jumperless V5 Node Map

This file documents the numeric IDs and common names for all key nodes on the Jumperless V5, based on `modules/jumperless/modjumperless.c`. Use it to translate between human‑readable names (like `D13` or `TOP_RAIL`) and the internal node numbers.

All constants are available in the MicroPython REPL; you normally do **not** need the numbers directly, but the mapping is useful for mental models and debugging.

---

## Breadboard rows (1–60)

Rows 1–60 represent the breadboard rows along the main area:

- `1`–`30` — upper half
- `31`–`60` — lower half

Each row corresponds to a vertical strip of 5 holes on the physical board.

Example:

```python
connect(1, 10)   # connect top row 1 to top row 10
connect(35, GND) # connect lower half row 35 to ground
```


---

## DACs and ADCs

## Special nodes and supplies

| Name                | Aliases                              | ID  | Notes                                   |
|---------------------|--------------------------------------|-----|-----------------------------------------|
| `GND`               | `GROUND`                             | 100 | Global ground net                       |
| `TOP_RAIL`          | `T_R`, `TOP_R`                       | 101 | Adjustable top rail                     |
| `BOTTOM_RAIL`       | `BOT_RAIL`, `B_R`                    | 102 | Adjustable bottom rail                  |
| `DAC0`              | `DAC_0`          | 106 | DAC channel 0 `*`        |
| `DAC1`              | `DAC_1`          | 107 | DAC channel 1          |
 
> [!CAUTION] 
> `*` Avoid using **DAC 0** and **ROUTABLE_BUFFER_IN** because they're used for probe switch sensing

### Current sense

| Name            | Aliases                                   | ID  |
|-----------------|-------------------------------------------|-----|
| `ISENSE_PLUS`   | `ISENSE_POS`, `ISENSE_P`, `INA_P`, `I_P`, `CURRENT_SENSE_PLUS`, `ISENSE_POSITIVE`, `I_POS` | 108 |
| `ISENSE_MINUS`  | `ISENSE_NEG`, `ISENSE_N`, `INA_N`, `I_N`, `CURRENT_SENSE_MINUS`, `ISENSE_NEGATIVE`, `I_NEG` | 109 |

These two nodes are the ends of a **2 Ω shunt resistor** and are internally shorted through that shunt; always use them in series with the circuit being measured.

### ADC nodes

| Name    | Aliases        | ID  | Notes                        |
|---------|----------------|-----|------------------------------|
| `ADC0`  | `ADC_0`, `ADC0_8V` | 110 | ADC channel 0 (±8 V)         |
| `ADC1`  | `ADC_1`, `ADC1_8V` | 111 | ADC channel 1 (±8 V)         |
| `ADC2`  | `ADC_2`, `ADC2_8V` | 112 | ADC channel 2 (±8 V)         |
| `ADC3`  | `ADC_3`, `ADC3_8V` | 113 | ADC channel 3 (±8 V)         |
| `ADC4`  | `ADC_4`, `ADC4_5V` | 114 | ADC channel 4 (5 V range)    |
| `ADC7`  | `ADC_7`, `ADC7_PROBE`, `PROBE` | 115 | Probe ADC channel           |

---

## UART and extra RP GPIOs

| Name         | Aliases        | ID  | Notes                         |
|--------------|----------------|-----|-------------------------------|



---

## User GPIO pins (GPIO_1–GPIO_8)

These are the main user‑accessible GPIOs.

| Name         | Aliases                          | ID  | RP2350B Pin | Notes |
|--------------|----------------------------------|-----|------------|-------------------|
| `RP_GPIO_1`  | `GPIO_1`, `GPIO1`, `GP_1`, `GP1` | 131 | 20         | I'm sorry they're 1-indexed like this
| `RP_GPIO_2`  | `GPIO_2`, `GPIO2`, `GP_2`, `GP2` | 132 | 21         |
| `RP_GPIO_3`  | `GPIO_3`, `GPIO3`, `GP_3`, `GP3` | 133 | 22         |
| `RP_GPIO_4`  | `GPIO_4`, `GPIO4`, `GP_4`, `GP4` | 134 | 23         |
| `RP_GPIO_5`  | `GPIO_5`, `GPIO5`, `GP_5`, `GP5` | 135 | 24         |
| `RP_GPIO_6`  | `GPIO_6`, `GPIO6`, `GP_6`, `GP6` | 136 | 25         |
| `RP_GPIO_7`  | `GPIO_7`, `GPIO7`, `GP_7`, `GP7` | 137 | 25         |
| `RP_GPIO_8`  | `GPIO_8`, `GPIO8`, `GP_8`, `GP8` | 138 | 27         |
| `RP_UART_TX` | `UART_TX`, `TX`                  | 116 | 0          | 2nd serial port passthrough
| `RP_UART_RX` | `UART_RX`, `RX`                  | 117 | 1          |

When working at the MicroPython level you will usually use `GPIO_1`–`GPIO_8` and the higher‑level GPIO APIs.

---

## Buffer nodes

These correspond to a routable buffer block:

| Name                | Aliases                 | ID  |
|---------------------|-------------------------|-----|
| `ROUTABLE_BUFFER_IN`  | `BUFFER_IN`, `BUF_IN`, `BUFF_IN`, `BUFFIN` | 139 |
| `ROUTABLE_BUFFER_OUT` | `BUFFER_OUT`, `BUF_OUT`, `BUFF_OUT`, `BUFFOUT` | 140 |

> [!CAUTION] 
> `*` Avoid using **DAC 0** and **ROUTABLE_BUFFER_IN** because they're used for probe switch sensing
---

## Arduino Nano header

The Nano header pins are mapped as follows:

| Name          | Aliases  | ID  | Routable? | Notes |
|---------------|----------|-----|-----------|-------|
| `NANO_VIN`    | `VIN`    | 69  |N
| `NANO_D0`     | `D0`     | 70  |Y
| `NANO_D1`     | `D1`     | 71  |Y
| `NANO_D2`     | `D2`     | 72  |Y
| `NANO_D3`     | `D3`     | 73  |Y
| `NANO_D4`     | `D4`     | 74  |Y
| `NANO_D5`     | `D5`     | 75  |Y
| `NANO_D6`     | `D6`     | 76  |Y
| `NANO_D7`     | `D7`     | 77  |Y
| `NANO_D9`     | `D9`     | 79  |Y
| `NANO_D10`    | `D10`    | 80  |Y
| `NANO_D11`    | `D11`    | 81  |Y
| `NANO_D12`    | `D12`    | 82  |Y
| `NANO_D13`    | `D13`    | 83  |Y
| `NANO_AREF`   | `AREF`   | 85  |Y
| `NANO_A0`     | `A0`     | 86  |Y
| `NANO_A1`     | `A1`     | 87  |Y
| `NANO_A2`     | `A2`     | 88  |Y
| `NANO_A3`     | `A3`     | 89  |Y
| `NANO_A4`     | `A4`     | 90  |Y
| `NANO_A5`     | `A5`     | 91  |Y
| `NANO_A6`     | `A6`     | 92  |Y
| `NANO_A7`     | `A7`     | 93  |Y
| `NANO_RESET_0`| `RST0`   | 94  |N|Wired directly to RP2350B pin 18
| `NANO_RESET_1`| `RST1`   | 95  |N|PSRAM Mod kits use this as CS (pin 19)
| `NANO_GND_1`  | `N_GND1` | 96  |N
| `NANO_GND_0`  | `N_GND0` | 97  |N
| `NANO_3V3`    |          | 98  |N
| `NANO_5V`     |          | 99  |N

These nodes let you route signals between the RP2350, the breadboard, and any compatible Nano‑footprint dev board (classic Nano, Nano ESP32, Nano RP2040 Connect, etc.).

---

## Rail pads

Special nodes representing where the probe can tap the rails:

| Name             | Aliases                  | ID  |
|------------------|--------------------------|-----|
| `TOP_RAIL`       | `TOP_RAIL_PAD`          | 101 |
| `BOTTOM_RAIL`    | `BOTTOM_RAIL_PAD`       | 102 |
| `TOP_RAIL_GND`   | `TOP_GND_PAD`           | 104 |
| `BOTTOM_RAIL_GND`| `BOT_RAIL_GND`, `BOTTOM_GND_PAD` | 126 |

---

## Breadboard layout (high‑level)

The board follows a standard half‑size breadboard geometry:

- Nano header at the top:

  - Top row: `D12 D11 D10 D9 D8 D7 D6 D5 D4 D3 D2 GND RST1 D0 D1`
  - Second row: `D13 3V3 REF A0 A1 A2 A3 A4 A5 A6 A7 5V RST0 GND VIN`

- Power rails:

  - Top: `TOP_RAIL` above, `GND` below
  - Bottom: `BOTTOM_RAIL` above, `GND` below

- Breadboard rows:

  - Rows `1`–`30` — upper half, between the top rails and the center gap
  - Rows `31`–`60` — lower half, between the center gap and the bottom rails

An ASCII diagram (from the docs) approximates the layout; the agent should treat rows and rails as in any typical solderless breadboard, with the addition that every hole has an individually controllable RGB LED.

### DIP ICs straddling the center gap

A DIP chip (555, op-amp, logic, …) sits across the center gap, with each side in
a different breadboard half. The two halves are independent rows, so the two
sides of the chip map to numerically distant nodes. For a chip whose first pin
sits at upper-half row `N`, the upper-side pins run `N, N+1, …` and the
lower-side pins run from the row directly across the gap (`N+30`).

Worked example — an 8-pin DIP (e.g. a 555) with pin 1 at row 1:

| Pin | Node | Pin | Node |
|-----|------|-----|------|
| 1 | `1` | 8 | `31` |
| 2 | `2` | 7 | `32` |
| 3 | `3` | 6 | `33` |
| 4 | `4` | 5 | `34` |

Pins 1–4 are on the upper side (rows 1–4); pins 5–8 are across the gap on the
lower side (rows 34→31, counting back toward pin 1). Adjust the base row to wherever
the chip is actually placed; verify with the probe or a measurement when unsure.

---

## How to use this map

- Prefer named constants like `D13`, `TOP_RAIL`, `GPIO_1`, `ADC0`, `ISENSE_PLUS` when generating code.
- Use the numeric IDs only when inspecting low‑level debugging output or when matching numeric IDs in `get_state()` / `get_net_info()` results.
- When the user describes physical positions (“top rail”, “bottom left rail”, “row 25”), translate them into these node names/IDs before constructing `connect(...)` commands.

