# Simple LED drive smoke test using the board's internal path resistance as a current limiter.
# Adjust rows to match your actual LED position.
dac_set(TOP_RAIL, 3.0)
connect(TOP_RAIL, 23)
connect(21, GND)

try:
    oled_clear()
    oled_print("LED drive on: 23->TOP, 21->GND")
except Exception:
    pass

print("LED drive enabled on rows 23/21")
