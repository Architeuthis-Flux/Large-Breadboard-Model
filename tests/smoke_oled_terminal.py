# pyright: reportUndefinedVariable=false
import sys

msg = "ok from jumperless"
prompt = getattr(sys, "ps1", ">>>")
line = "{} {}".format(prompt, msg)

try:
    oled_clear()
    oled_print(line)
except Exception:
    # OLED might not be available in all contexts; terminal output is still required.
    pass

print(line)
