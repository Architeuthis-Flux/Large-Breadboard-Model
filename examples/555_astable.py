"""
555 astable: place with probe (click to confirm), then wire at that location.

1. Overlay at default; user moves with probe, clicks to confirm → (placed_col, placed_row).
2. Wire nets and set TOP_RAIL using that placement (no file system).

Chip on its side, notch left. Top left = VCC (8). Pins clockwise: top row 8,7,6,5; bottom row 1,2,3,4.

Don't run this as an agent skill, this is an example.
"""

import time

RED = 0x600000
ORANGE = 0x402000
YELLOW = 0x204000
GREEN = 0x004010
BLUE = 0x000040
BODY = 0x0c0c10

# Chip on its side in the breadboard, notch to the left.
# Overlay: row 0 = top row of chip (pins 8,7,6,5), row 1 = bottom row (pins 1,2,3,4). Left = notch side.
# Top left = VCC (8), pins go clockwise: 8,7,6,5 on top row; 1,2,3,4 on bottom row.
COLORS_2D = [
    [RED, BLUE, YELLOW, BODY],   # top row:  8 VCC, 7 DISCH, 6 THRES, 5 CONT
    [RED, BLUE, YELLOW, BODY],   # top row:  8 VCC, 7 DISCH, 6 THRES, 5 CONT
    [GREEN, YELLOW, BLUE,  RED],   # bottom:   1 GND, 2 TRIG,  3 OUT,   4 RESET
    [GREEN, YELLOW, BLUE,  RED],   # bottom:   1 GND, 2 TRIG,  3 OUT,   4 RESET
]
OVERLAY_NAME = "555_astable"
HEIGHT = 4
WIDTH = 4
DEFAULT_COL = 5
DEFAULT_ROW_TOP = 4
DEFAULT_ROW_BOT = 9

VCC_VOLTS = 5.0


def pad_to_node(pad):
    if pad is None:
        return -1
    if isinstance(pad, int):
        return pad
    if hasattr(pad, "node"):
        return getattr(pad, "node", -1)
    try:
        return int(pad)
    except (TypeError, ValueError):
        return -1


def node_to_xy(node):
    if node < 1:
        return (DEFAULT_COL, DEFAULT_ROW_TOP)
    if node <= 30:
        return (node, DEFAULT_ROW_TOP)
    return (node - 30, DEFAULT_ROW_BOT)


def placement_to_rows(placed_col):
    """Map placed column to breadboard rows for each 555 pin.

    Chip on its side, notch to the left. Top left = VCC (pin 8). Pins clockwise.
    - Top half of breadboard (rows 1–30): left→right = pins 8, 7, 6, 5 (VCC, DISCH, THRES, CONT).
    - Bottom half (rows 31–60): left→right = pins 1, 2, 3, 4 (GND, TRIG, OUT, RESET).
    """
    c = placed_col
    # Top half (rows 1–30): top left = pin 8 (VCC) = c, then 7,6,5 clockwise.
    row_p8 = c               # pin 8 VCC (top left)
    row_p7 = c + 1           # pin 7 DISCH
    row_p6 = c + 2           # pin 6 THRES
    row_p5 = c + 3           # pin 5 CONT (top right)

    # Bottom half (rows 31–60): bottom left = pin 1 (GND), then 2,3,4.
    row_p1 = 30 + c          # pin 1 GND (bottom left)
    row_p2 = 30 + c + 1      # pin 2 TRIG
    row_p3 = 30 + c + 2      # pin 3 OUT
    row_p4 = 30 + c + 3      # pin 4 RESET (bottom right)

    return {
        "ROW_GND": row_p1,
        "ROW_TRIG": row_p2,
        "ROW_OUT": row_p3,
        "ROW_RESET": row_p4,
        "ROW_CTRL": row_p5,
        "ROW_THR": row_p6,
        "ROW_DISCH": row_p7,
        "ROW_VCC": row_p8,
        "ROW_LED": row_p3 + 1 if (row_p3 + 1) <= 60 else row_p3,
    }


def tap_pad(instruction, color=0x003020):
    """Show instruction on OLED, wait for probe touch, return breadboard node (1-60).

    instruction: single-line text for the OLED.
    color: 0xRRGGBB used for a 3-pixel-tall confirmation stripe on that column.
    """
    oled_clear()
    oled_print(instruction)
    pad = probe_read_blocking()
    node = pad_to_node(pad)

    # Visual feedback: 3-pixel-tall confirmation stripe and debounce to avoid double-reads.
    try:
        x, y = node_to_xy(node)
        for dy in (-1, 0, 1):
            ry = y + dy
            if 1 <= ry <= 10:
                overlay_set_pixel(x, ry, color)
    except Exception:
        pass

    # Debounce: short delay, then wait for probe release.
    try:
        time.sleep_ms(250)
    except Exception:
        time.sleep(0.25)

    for _ in range(20):  # up to ~1s
        try:
            if pad_to_node(probe_read_nonblocking()) < 1:
                break
        except Exception:
            break
        try:
            time.sleep_ms(50)
        except Exception:
            time.sleep(0.05)

    return node


def do_placement():
    """Show overlay, follow probe, return (placed_col, placed_row) when user clicks."""
    overlay_clear_all()
    oled_clear()
    oled_print("555: tap pad in left corner\nclick probe to confirm")


    overlay_set(OVERLAY_NAME, DEFAULT_COL, DEFAULT_ROW_TOP, HEIGHT, WIDTH, COLORS_2D)
    placed_col = DEFAULT_COL
    placed_row = DEFAULT_ROW_TOP

    while True:
        pad = probe_read_nonblocking()
        node = pad_to_node(pad)
        if node >= 1:
            x_col, y_row = node_to_xy(node)
            if 1 <= x_col <= 30 and 1 <= y_row <= 10:
                overlay_place(OVERLAY_NAME, x_col, y_row)
                placed_col = x_col
                placed_row = y_row
        try:
            force_service("ProbeButton")
        except Exception:
            pass
        if probe_button_nonblocking():
            break
        try:
            if clickwheel_get_button():
                break
        except Exception:
            pass
        time.sleep_ms(100)

    oled_clear()
    oled_print("Placed at col %s" % placed_col)
    oled_print("row %s" % placed_row)
    return (placed_col, placed_row)


def do_taps():
    """Instruct user to tap where R1, R2, C, and LED go; return dict of node numbers."""
    taps = {}
    # Standard astable:
    # R1: VCC (pin 8) <-> DISCH (pin 7)
    # R2: DISCH (pin 7) <-> CAP_NODE (pins 2 & 6 junction)
    # C:  CAP_NODE <-> GND (pin 1)
    taps["r1_vcc"] = tap_pad("R1\n Tap VCC side", RED)
    taps["r1_disch"] = tap_pad("R1\n Tap DISCH side", RED)
    taps["r2_disch"] = tap_pad("R2\n Tap DISCH side", YELLOW)
    taps["r2_cap"] = tap_pad("R2\n Tap CAP-node side", YELLOW)
    taps["cap_node"] = tap_pad("CAP\n Tap + side", BLUE)
    taps["c_gnd"] = tap_pad("CAP\n Tap - side", GREEN)
    taps["led_anode"] = tap_pad("LED +\n Tap anode side", YELLOW)
    taps["led_cathode"] = tap_pad("LED -\n Tap cathode side", GREEN)
    # Done choosing pads; clear tap markers (keep only the 555 placement overlay for a moment)
    try:
        overlay_clear_all()
    except Exception:
        pass
    return taps


def do_wiring(placed_col, placed_row, taps):
    """Apply nets and TOP_RAIL using placement and user-tapped component positions."""
    R = placement_to_rows(placed_col)
    ROW_GND = R["ROW_GND"]
    ROW_TRIG = R["ROW_TRIG"]
    ROW_OUT = R["ROW_OUT"]
    ROW_RESET = R["ROW_RESET"]
    ROW_THR = R["ROW_THR"]
    ROW_DISCH = R["ROW_DISCH"]
    ROW_VCC = R["ROW_VCC"]

    nodes_clear()
    time.sleep(0.05)

    # 555 core
    connect(TOP_RAIL, ROW_VCC)
    connect(ROW_VCC, ROW_RESET)
    connect(GND, ROW_GND)
    # Timing node (CAP_NODE): pins 2 & 6 connect to the capacitor node, NOT to DISCH.
    cap_node = taps.get("cap_node", -1)
    if cap_node < 1:
        # Fallback: keep behavior sane if user missed tap (still tie pins 2&6 together)
        connect(ROW_TRIG, ROW_THR)
    else:
        # Insert ISENSE shunt in series feeding the capacitor high side so we can
        # visualize current into the timing capacitor:
        # TRIG + THR + R2 cap-end -> ISENSE_PLUS -> (2Ω shunt) -> ISENSE_MINUS -> CAP_NODE pad
        connect(ISENSE_MINUS, cap_node, 0)
        connect(ROW_TRIG, ROW_THR)
        connect(ROW_THR, ISENSE_PLUS, 0)

    # R1: VCC <-> DISCH
    r1_vcc = taps.get("r1_vcc", -1)
    r1_disch = taps.get("r1_disch", -1)
    if r1_vcc >= 1:
        connect(ROW_VCC, r1_vcc)
    if r1_disch >= 1:
        connect(ROW_DISCH, r1_disch)

    # R2: DISCH <-> CAP_NODE (via ISENSE shunt on the CAP side)
    r2_disch = taps.get("r2_disch", -1)
    r2_cap = taps.get("r2_cap", -1)
    if r2_disch >= 1:
        connect(ROW_DISCH, r2_disch)
    if cap_node >= 1 and r2_cap >= 1:
        connect(ROW_THR, r2_cap)

    c_gnd = taps.get("c_gnd", -1)
    if cap_node >= 1 and c_gnd >= 1:
        # CAP_NODE side (high side) is the tapped cap_node, fed via ISENSE.
        connect(GND, c_gnd)
    elif c_gnd >= 1:
        connect(GND, c_gnd)

    # LED: OUT to anode; cathode to GND
    led_anode = taps.get("led_anode", -1)
    led_cathode = taps.get("led_cathode", -1)
    if led_anode >= 1:
        connect(ROW_OUT, led_anode)
    if led_cathode >= 1:
        connect(GND, led_cathode)

    time.sleep(0.05)

    # --- Instrumentation: ADC taps on main signal nets (no ADC on ISENSE nets) ---
    # ADC0: DISCH node (pin 7)
    connect(ADC0, ROW_DISCH)
    # ADC1: LED anode (after the series resistor, user-tapped)
    if led_anode >= 1:
        connect(ADC1, led_anode)
    dac_set(TOP_RAIL, VCC_VOLTS)
    time.sleep(0.02)

    oled_clear()
    oled_print("Wired at col %s" % placed_col)
    oled_print("R1 R2 C LED done")
    print("555 astable wired: VCC=%.1f V (col %s)" % (VCC_VOLTS, placed_col))
    print("R1(%s-%s) R2(%s-%s) CAP_NODE(%s) C(%s-GND) LED(OUT-%s, %s-GND)" % (
        r1_vcc if r1_vcc >= 1 else "VCC", r1_disch if r1_disch >= 1 else "DISCH",
        r2_disch if r2_disch >= 1 else "DISCH", r2_cap if r2_cap >= 1 else "CAP",
        cap_node if cap_node >= 1 else "?",
        c_gnd if c_gnd >= 1 else "?",
        led_anode if led_anode >= 1 else "?", led_cathode if led_cathode >= 1 else "?"))

oled_set_text_size(2)
# Run: place 555, then tap R1/R2/C/LED locations, then wire
placed_col, placed_row = do_placement()
taps = do_taps()
do_wiring(placed_col, placed_row, taps)
