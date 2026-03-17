"""
Jumperless Stylophone
Musical instrument using probe and GPIO to generate audio tones.

Hardware Setup:
1. Connect speaker between rows 25 (positive) and 55 (negative)    
"""

import time
import jumperless as j

speaker_pos_row = 25
speaker_neg_row = 55
freq_multiplier = 40.0

def setup_audio():
    j.disconnect(speaker_pos_row, -1)
    j.disconnect(speaker_neg_row, -1)
    j.connect(j.GPIO_1, speaker_pos_row)
    j.connect(j.GND, speaker_neg_row)
    j.pwm(j.GPIO_1, 10, 0.5)
    print("Connect speaker: positive to row " + str(speaker_pos_row) + ", negative to row " + str(speaker_neg_row))
    time.sleep(0.1)

print("Jumperless Stylophone")
j.oled_print("Touch pads!")

setup_audio()


sustain = 500
sustain_timer = sustain

while True:
    
    pad = j.probe_read_nonblocking()
    if pad != j.NO_PAD:

        frequency = float(pad) * freq_multiplier
        j.pwm(j.GPIO_1, frequency, 0.5)
        # j.pwm_set_frequency(j.GPIO_1, frequency)

        print("\r                                 ", end="\r")
        print("Pad: " + str(pad) + " " + str(frequency) + " Hz", end="")
        j.oled_print(str(frequency) + " Hz")
        sustain_timer = time.ticks_ms() + sustain


    if time.ticks_ms() > sustain_timer:
        j.pwm_stop(j.GPIO_1)

    j.force_service("ProbeButton")
    button = j.probe_button(False)
    if button == j.BUTTON_CONNECT:
        sustain += 10
        j.oled_print("Sustain: " + str(sustain))
        time.sleep(0.1)

    if button == j.BUTTON_REMOVE:
        sustain -= 10 
        j.oled_print("Sustain: " + str(sustain))
        time.sleep(0.1)
