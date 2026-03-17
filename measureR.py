"""
Scratch helpers for measuring resistors on Jumperless V5.

These functions are intended to be copied into exec/--stdin runs while
we iterate on different measurement strategies (INA- and ADC-based).
"""

import time


def _cleanup_nodes(nodes):
    """Best-effort disconnect of a list of nodes."""
    for n in nodes:
        try:
            disconnect(n, -1)
        except Exception:
            pass


def measure_R_ina(node_a, node_b, label, v_set=2.0, sensor=0, samples=8):
    """
    Measure resistance between node_a and node_b using DAC1 + INA sensor.

    Topology:
        DAC1 -> ISENSE_PLUS -> shunt -> ISENSE_MINUS -> node_a -> R_unknown -> node_b -> GND
    """
    print("---", label, "(INA", sensor, ") ---")
    try:
        dac_set(1, v_set)
    except Exception as e:
        print("dac_set failed", e)
        return

    try:
        connect(DAC1, ISENSE_PLUS)
        connect(ISENSE_MINUS, node_a)
        connect(node_b, GND)
    except Exception as e:
        print("connect failed", e)
        _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, node_a, node_b])
        return

    try:
        time.sleep(0.05)
    except Exception:
        pass

    vs, is_ = [], []
    for idx in range(samples):
        try:
            v = ina_get_bus_voltage(sensor)
            i = ina_get_current(sensor)
        except Exception as e:
            print("INA read failed", e)
            break
        vs.append(v)
        is_.append(i)
        print("sample", idx, ": v=", v, "i=", i)
        try:
            time.sleep(0.02)
        except Exception:
            pass

    _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, node_a, node_b])

    if not vs or not is_:
        print(label, "R? (no valid INA samples)")
        return

    v_avg = sum(vs) / len(vs)
    i_avg = sum(is_) / len(is_)
    if i_avg == 0:
        print(label, "R? (i_avg=0)")
        return

    r = v_avg / i_avg
    print(label, "R≈", r, "ohms (v_avg=", v_avg, ", i_avg=", i_avg, ")")


def measure_R_adc(node_a, node_b, label, v_set=2.0, shunt_ohms=2.0, samples=8):
    """
    Measure resistance between node_a and node_b using DAC1 + ISENSE shunt + ADC0/ADC1.

    Topology:
        DAC1 -> ISENSE_PLUS --(shunt)--> ISENSE_MINUS -> node_a -> R_unknown -> node_b -> GND
        ADC0 senses ISENSE_PLUS, ADC1 senses ISENSE_MINUS.
    """
    print("---", label, "(ADC-based) ---")
    try:
        dac_set(1, v_set)
    except Exception as e:
        print("dac_set failed", e)
        return

    try:
        connect(DAC1, ISENSE_PLUS)
        connect(ISENSE_MINUS, node_a)
        connect(node_b, GND)
        connect(ADC0, ISENSE_PLUS)
        connect(ADC1, ISENSE_MINUS)
    except Exception as e:
        print("connect failed", e)
        _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, node_a, node_b, ADC0, ADC1])
        return

    try:
        time.sleep(0.05)
    except Exception:
        pass

    vplus_list, vminus_list = [], []
    for idx in range(samples):
        try:
            v_plus = adc_get(0)
            v_minus = adc_get(1)
        except Exception as e:
            print("adc_get failed", e)
            break
        vplus_list.append(v_plus)
        vminus_list.append(v_minus)
        print("sample", idx, ": v_plus=", v_plus, "v_minus=", v_minus)
        try:
            time.sleep(0.02)
        except Exception:
            pass

    _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, node_a, node_b, ADC0, ADC1])

    if not vplus_list or not vminus_list:
        print(label, "R? (no valid ADC samples)")
        return

    v_plus_avg = sum(vplus_list) / len(vplus_list)
    v_minus_avg = sum(vminus_list) / len(vminus_list)
    v_shunt = v_plus_avg - v_minus_avg
    if v_shunt <= 0:
        print(
            label,
            "R? (v_shunt <= 0, v_plus_avg=",
            v_plus_avg,
            ", v_minus_avg=",
            v_minus_avg,
            ")",
        )
        return

    i = v_shunt / shunt_ohms
    if i == 0:
        print(label, "R? (i=0)")
        return

    r_est = v_minus_avg / i
    print(
        label,
        "R≈",
        r_est,
        "ohms (v_plus_avg=",
        v_plus_avg,
        ", v_minus_avg=",
        v_minus_avg,
        ", i=",
        i,
        ", shunt_ohms=",
        shunt_ohms,
        ")",
    )


def measure_R_mixed(node_a, node_b, label, v_set=2.0, sensor=0, samples=8):
    """
    Measure resistance using a "mixed" method:

    - DAC1 drives the series chain through ISENSE (as before)
    - ADC0 / ADC1 read the voltage at node_a / node_b
    - INA sensor (default 0) provides current through the shunt
    """
    print("---", label, "(mixed ADC+INA", sensor, ") ---")
    try:
        dac_set(1, v_set)
    except Exception as e:
        print("dac_set failed", e)
        return

    try:
        # DAC1 -> ISENSE_PLUS -> shunt -> ISENSE_MINUS -> node_a -> R_unknown -> node_b -> GND
        connect(DAC1, ISENSE_PLUS)
        connect(ISENSE_MINUS, node_a)
        connect(node_b, GND)
        # Measure node_a and node_b voltages directly
        connect(ADC0, node_a)
        connect(ADC1, node_b)
    except Exception as e:
        print("connect failed", e)
        _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, node_a, node_b, ADC0, ADC1])
        return

    try:
        time.sleep(0.05)
    except Exception:
        pass

    va_list, vb_list, i_list = [], [], []
    for idx in range(samples):
        try:
            va = adc_get(0)
            vb = adc_get(1)
            i = ina_get_current(sensor)
        except Exception as e:
            print("mixed read failed", e)
            break
        va_list.append(va)
        vb_list.append(vb)
        i_list.append(i)
        print("sample", idx, ": va=", va, "vb=", vb, "i=", i)
        try:
            time.sleep(0.02)
        except Exception:
            pass

    _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, node_a, node_b, ADC0, ADC1])

    if not va_list or not vb_list or not i_list:
        print(label, "R? (no valid mixed samples)")
        return

    va_avg = sum(va_list) / len(va_list)
    vb_avg = sum(vb_list) / len(vb_list)
    i_avg = sum(i_list) / len(i_list)
    if i_avg == 0:
        print(label, "R? (i_avg=0)")
        return

    # Voltage across the unknown resistor is (va - vb)
    v_r = va_avg - vb_avg
    if v_r <= 0:
        print(
            label,
            "R? (v_r <= 0, va_avg=",
            va_avg,
            ", vb_avg=",
            vb_avg,
            ", i_avg=",
            i_avg,
            ")",
        )
        return

    r_est = v_r / i_avg
    print(
        label,
        "R≈",
        r_est,
        "ohms (va_avg=",
        va_avg,
        ", vb_avg=",
        vb_avg,
        ", i_avg=",
        i_avg,
        ")",
    )


if __name__ == "__main__":
    # Continuous monitor: use the baseline-corrected INA0 algorithm
    # (the one that tracked ~1.8k/20k reasonably) on a resistor
    # placed between rows 1 and 31.

    SAMPLES = 18
    _last_r_est = None

    def measure_once_and_show():
        label = "R_1_31_CONT_INA0_BASE"
        print("---", label, "---")

        global _last_r_est

        try:
            nodes_clear()
        except Exception:
            pass

        # Choose DAC voltage based on last measured resistance to keep
        # current in a comfortable range for the INA.
        if _last_r_est is None:
            v_set = 2.0
        elif _last_r_est < 200.0:
            v_set = 0.5
        elif _last_r_est < 1000.0:
            v_set = 1.5
        elif _last_r_est < 5000.0:
            v_set = 2.5
        else:
            v_set = 4.0

        print("using v_set=", v_set, "based on last R=", _last_r_est)

        try:
            dac_set(1, v_set)
        except Exception as e:
            print("dac_set failed", e)
            return

        # 1) Baseline leakage: 31 floating
        try:
            connect(DAC1, ISENSE_PLUS)
            connect(ISENSE_MINUS, 1)
        except Exception as e:
            print("baseline connect failed", e)
            _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, 1])
            return

        try:
            time.sleep(0.05)
        except Exception:
            pass

        i0_list = []
        for idx in range(SAMPLES):
            try:
                i0 = ina_get_current(0)
            except Exception as e:
                print("baseline INA read failed", e)
                break
            i0_list.append(i0)
            print("baseline sample", idx, ": i0=", i0)
            try:
                time.sleep(0.02)
            except Exception:
                pass

        _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, 1])

        if not i0_list:
            print(label, "R? (no baseline samples)")
            return

        i0_avg = sum(i0_list) / len(i0_list)

        # 2) Actual measurement: 31 tied to GND, sense voltage at node 1 via ADC0
        try:
            connect(DAC1, ISENSE_PLUS)
            connect(ISENSE_MINUS, 1)
            connect(31, GND)
            connect(ADC0, 1)
        except Exception as e:
            print("measure connect failed", e)
            _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, 1, 31, ADC0])
            return

        try:
            time.sleep(0.05)
        except Exception:
            pass

        v_list = []
        i1_list = []
        for idx in range(SAMPLES):
            try:
                v = adc_get(0)
                i1 = ina_get_current(0)
            except Exception as e:
                print("measure read failed", e)
                break
            v_list.append(v)
            i1_list.append(i1)
            print("measure sample", idx, ": v=", v, "i1=", i1)
            try:
                time.sleep(0.02)
            except Exception:
                pass

        _cleanup_nodes([DAC1, ISENSE_PLUS, ISENSE_MINUS, 1, 31, ADC0])

        if not v_list or not i1_list:
            print(label, "R? (no measure samples)")
            return

        v_avg = sum(v_list) / len(v_list)
        i1_avg = sum(i1_list) / len(i1_list)
        i_net = i1_avg - i0_avg
        print("v_avg=", v_avg, "i0_avg=", i0_avg, "i1_avg=", i1_avg, "i_net=", i_net)

        if i_net <= 0:
            print(label, "R? (i_net<=0)")
            return

        r_est = v_avg / i_net
        if r_est < 1.0 or r_est > 1e7:
            print(label, "R? (out of range)", r_est)
            return

        msg = "R≈{:.0f}Ω".format(r_est)
        print(label, msg)
        _last_r_est = r_est
        try:
            oled_clear()
            oled_print("Row 1-31:")
            oled_print(msg)
        except Exception:
            pass

    print("Starting continuous R(1,31) baseline-INA monitor. Press reset to stop.")
    while True:
        measure_once_and_show()
        try:
            time.sleep(0.7)
        except Exception:
            pass


