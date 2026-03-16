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

## Special nodes and supplies

| Name                | Aliases                              | ID  | Notes                                   |
|---------------------|--------------------------------------|-----|-----------------------------------------|
| `GND`               | `GROUND`                             | 100 | Global ground net                       |
| `TOP_RAIL`          | `T_R`, `TOP_R`                       | 101 | Adjustable top rail                     |
| `BOTTOM_RAIL`       | `BOT_RAIL`, `B_R`                    | 102 | Adjustable bottom rail                  |
| `SUPPLY_3V3`        | `3V3`, `3.3V`                        | 103 | Internal 3.3 V supply                   |
| `TOP_RAIL_GND`      | `TOP_GND`                            | 104 | Top rail ground segment                 |
| `SUPPLY_5V`         | `5V`, `+5V`                          | 105 | Internal 5 V supply                     |
| `SUPPLY_8V_P`       | `8V_P`, `8V_POS`                     | 120 | +8 V rail                               |
| `SUPPLY_8V_N`       | `8V_N`, `8V_NEG`                     | 121 | −8 V rail                               |
| `BOTTOM_RAIL_GND`   | `BOT_GND`, `BOTTOM_GND`              | 126 | Bottom rail ground segment              |
| `EMPTY_NET`         | `EMPTY`                              | 127 | Special “empty” net marker              |

---

## DACs and ADCs

### DAC nodes

| Name     | Aliases          | ID  | Notes                  |
|----------|------------------|-----|------------------------|
| `DAC0`   | `DAC_0`          | 106 | DAC channel 0          |
| `DAC1`   | `DAC_1`,         | 107 | DAC channel 1          |

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
| `RP_UART_TX` | `UART_TX`, `TX`| 116 | Routable UART TX / GPIO 16   |
| `RP_UART_RX` | `UART_RX`, `RX`| 117 | Routable UART RX / GPIO 17   |
| `RP_GPIO_18` | `GP_18`        | 118 | Internal GPIO 18              |
| `RP_GPIO_19` | `GP_19`        | 119 | Internal GPIO 19              |

---

## User GPIO pins (GPIO_1–GPIO_8)

These are the main user‑accessible GPIOs.

| Name         | Aliases                    | ID  |
|--------------|----------------------------|-----|
| `RP_GPIO_1`  | `GPIO_1`, `GPIO1`, `GP_1`, `GP1` | 131 |
| `RP_GPIO_2`  | `GPIO_2`, `GPIO2`, `GP_2`, `GP2` | 132 |
| `RP_GPIO_3`  | `GPIO_3`, `GPIO3`, `GP_3`, `GP3` | 133 |
| `RP_GPIO_4`  | `GPIO_4`, `GPIO4`, `GP_4`, `GP4` | 134 |
| `RP_GPIO_5`  | `GPIO_5`, `GPIO5`, `GP_5`, `GP5` | 135 |
| `RP_GPIO_6`  | `GPIO_6`, `GPIO6`, `GP_6`, `GP6` | 136 |
| `RP_GPIO_7`  | `GPIO_7`, `GPIO7`, `GP_7`, `GP7` | 137 |
| `RP_GPIO_8`  | `GPIO_8`, `GPIO8`, `GP_8`, `GP8` | 138 |

When working at the MicroPython level you will usually use `GPIO_1`–`GPIO_8` and the higher‑level GPIO APIs.

---

## Buffer nodes

These correspond to a routable buffer block:

| Name                | Aliases                 | ID  |
|---------------------|-------------------------|-----|
| `ROUTABLE_BUFFER_IN`  | `BUFFER_IN`, `BUF_IN`, `BUFF_IN`, `BUFFIN` | 139 |
| `ROUTABLE_BUFFER_OUT` | `BUFFER_OUT`, `BUF_OUT`, `BUFF_OUT`, `BUFFOUT` | 140 |

---

## Arduino Nano header

The Nano header pins are mapped as follows:

| Name          | Aliases  | ID  |
|---------------|----------|-----|
| `NANO_VIN`    | `VIN`    | 69  |
| `NANO_D0`     | `D0`     | 70  |
| `NANO_D1`     | `D1`     | 71  |
| `NANO_D2`     | `D2`     | 72  |
| `NANO_D3`     | `D3`     | 73  |
| `NANO_D4`     | `D4`     | 74  |
| `NANO_D5`     | `D5`     | 75  |
| `NANO_D6`     | `D6`     | 76  |
| `NANO_D7`     | `D7`     | 77  |
| `NANO_D8`     | `D8`     | 78  |
| `NANO_D9`     | `D9`     | 79  |
| `NANO_D10`    | `D10`    | 80  |
| `NANO_D11`    | `D11`    | 81  |
| `NANO_D12`    | `D12`    | 82  |
| `NANO_D13`    | `D13`    | 83  |
| `NANO_RESET`  | `RESET`  | 84  |
| `NANO_AREF`   | `AREF`   | 85  |
| `NANO_A0`     | `A0`     | 86  |
| `NANO_A1`     | `A1`     | 87  |
| `NANO_A2`     | `A2`     | 88  |
| `NANO_A3`     | `A3`     | 89  |
| `NANO_A4`     | `A4`     | 90  |
| `NANO_A5`     | `A5`     | 91  |
| `NANO_A6`     | `A6`     | 92  |
| `NANO_A7`     | `A7`     | 93  |
| `NANO_RESET_0`| `RST0`   | 94  |
| `NANO_RESET_1`| `RST1`   | 95  |
| `NANO_GND_1`  | `N_GND1` | 96  |
| `NANO_GND_0`  | `N_GND0` | 97  |
| `NANO_3V3`    |          | 98  |
| `NANO_5V`     |          | 99  |

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

  - Top row: `D12 D11 D10 D9 D8 D7 D6 D5 D4 D3 D2 GND RST D0 D1`
  - Second row: `D13 3V3 REF A0 A1 A2 A3 A4 A5 A6 A7 5V RST GND VIN`

- Power rails:

  - Top: `TOP_RAIL` above, `GND` below
  - Bottom: `BOTTOM_RAIL` above, `GND` below

- Breadboard rows:

  - Rows `1`–`30` — upper half, between the top rails and the center gap
  - Rows `31`–`60` — lower half, between the center gap and the bottom rails

An ASCII diagram (from the docs) approximates the layout; the agent should treat rows and rails as in any typical solderless breadboard, with the addition that every hole has an individually controllable RGB LED.

---

## How to use this map

- Prefer named constants like `D13`, `TOP_RAIL`, `GPIO_1`, `ADC0`, `ISENSE_PLUS` when generating code.
- Use the numeric IDs only when inspecting low‑level debugging output or when matching numeric IDs in `get_state()` / `get_net_info()` results.
- When the user describes physical positions (“top rail”, “bottom left rail”, “row 25”), translate them into these node names/IDs before constructing `connect(...)` commands.

