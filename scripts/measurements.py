"""
Device-side measurement helpers for Jumperless V5.

Upload this file to the Jumperless filesystem (for example as
`/python_scripts/lib/measurements.py` or similar), then import it:

    from measurements import *

All functions assume the standard `jumperless` module APIs are available
globally (connect, disconnect, dac_set, adc_get, ina_get_current, etc.).
"""

try:
    import math
except ImportError:
    math = None

try:
    import time
except ImportError:
    time = None


def _safe_disconnect(node):
    """Disconnect a node from everything, ignoring errors."""
    try:
        disconnect(node, -1)
    except Exception:
        pass


def _settle(seconds=0.01):
    """Wait for crossbar/DAC to settle after routing or voltage changes."""
    if time is not None:
        time.sleep(seconds)


def _inter_sample_delay():
    """Small delay between repeated ADC/INA samples."""
    if time is not None:
        time.sleep(0.01)


def measure_voltage(node, adc_channel=0, disconnect_after=True):
    """
    Measure the DC voltage at a node using an ADC channel.

    Args:
        node: Node name/number (e.g. 5, 'D13', TOP_RAIL).
        adc_channel: ADC channel index (0-4, or 7 for PROBE).
        disconnect_after: If True, disconnect the ADC from the node when done.

    Returns:
        Measured voltage (float), or None on error.
    """
    adc_node = {
        0: "ADC0",
        1: "ADC1",
        2: "ADC2",
        3: "ADC3",
        4: "ADC4",
        7: "ADC7",
    }.get(adc_channel, "ADC0")

    try:
        connect(adc_node, node)
    except Exception as e:
        print("measure_voltage: could not connect ADC:", e)
        return None

    _settle(0.01)

    try:
        v = adc_get(adc_channel)
    except Exception as e:
        print("measure_voltage: adc_get failed:", e)
        v = None

    if disconnect_after:
        _safe_disconnect(adc_node)

    return v


def measure_current_series(high_node, low_node, sensor=0, disconnect_after=True):
    """
    Measure current between two nodes by inserting the ISENSE shunt in series.

    Wiring:
        connect(ISENSE_PLUS, high_node)
        connect(ISENSE_MINUS, low_node)

    Args:
        high_node: Node on the "high" side (closer to supply).
        low_node: Node on the "low" side (closer to load).
        sensor: INA sensor index (0 or 1).
        disconnect_after: If True, disconnect ISENSE nodes afterwards.

    Returns:
        (current_amps, bus_voltage) tuple, or (None, None) on error.
    """
    try:
        connect("ISENSE_PLUS", high_node)
        connect("ISENSE_MINUS", low_node)
    except Exception as e:
        print("measure_current_series: connect failed:", e)
        return None, None

    _settle(0.01)

    try:
        i = ina_get_current(sensor)
        v = ina_get_bus_voltage(sensor)
    except Exception as e:
        print("measure_current_series: INA read failed:", e)
        i, v = None, None

    if disconnect_after:
        _safe_disconnect("ISENSE_PLUS")
        _safe_disconnect("ISENSE_MINUS")

    return i, v


def measure_resistance(node_a, node_b, dac_channel=1, sensor=0, set_voltage=3.0, disconnect_after=True):
    """
    Estimate resistance between node_a and node_b using DAC + INA.

    Method:
      1. Configure DAC channel to set_voltage.
      2. Insert ISENSE shunt in series with the unknown resistance.
      3. Measure bus voltage and current.
      4. Compute R ≈ V / I, adjusting for the 2Ω shunt if desired.

    This helper is a starting point; it does not attempt to perfectly
    model crossbar resistance or parasitics, so results are approximate.

    Args:
        node_a: One end of the unknown resistor.
        node_b: The other end of the unknown resistor.
        dac_channel: DAC channel index (0 or 1).
        sensor: INA sensor index associated with that path (0 or 1).
        set_voltage: DAC voltage to apply across the network.
        disconnect_after: If True, restore ISENSE and DAC connections.

    Returns:
        Approximate resistance in ohms (float), or None on error.
    """
    # Map DAC channel to node name
    dac_node = "DAC0" if dac_channel == 0 else "DAC1"

    # Simplest wiring: DAC -> ISENSE_PLUS -> node_a -> unknown R -> node_b -> GND
    # For now we assume node_b is referenced to GND; more complex topologies
    # can be built up by the calling code.
    try:
        dac_set(dac_channel, set_voltage)
    except Exception as e:
        print("measure_resistance: dac_set failed:", e)
        return None

    try:
        connect(dac_node, "ISENSE_PLUS")
        connect("ISENSE_MINUS", node_a)
        connect(node_b, GND)
    except Exception as e:
        print("measure_resistance: connect failed:", e)
        return None

    _settle(0.01)

    try:
        v_bus = ina_get_bus_voltage(sensor)
        i = ina_get_current(sensor)
    except Exception as e:
        print("measure_resistance: INA read failed:", e)
        v_bus, i = None, None

    if disconnect_after:
        _safe_disconnect(dac_node)
        _safe_disconnect("ISENSE_PLUS")
        _safe_disconnect("ISENSE_MINUS")
        _safe_disconnect(node_a)
        _safe_disconnect(node_b)

    if v_bus is None or i is None or i == 0:
        return None

    # Basic Ohm's law estimate; shunt and crossbar resistance mean this is approximate.
    r = v_bus / i
    return r


def sweep_voltage(node, start_v, end_v, steps, dac_channel=1, adc_channel=0, disconnect_after=True):
    """
    Sweep DAC voltage and measure the voltage at a node for each step.

    Args:
        node: Node whose voltage should be measured.
        start_v: Start DAC voltage.
        end_v: End DAC voltage.
        steps: Number of steps (>= 2).
        dac_channel: DAC channel index to use.
        adc_channel: ADC channel index to use for measurement.
        disconnect_after: If True, disconnect ADC and DAC after sweep.

    Returns:
        List of (set_v, measured_v) tuples.
    """
    if steps < 2:
        raise ValueError("steps must be >= 2")

    dac_node = "DAC0" if dac_channel == 0 else "DAC1"
    adc_node = {
        0: "ADC0",
        1: "ADC1",
        2: "ADC2",
        3: "ADC3",
        4: "ADC4",
        7: "ADC7",
    }.get(adc_channel, "ADC0")

    results = []

    try:
        connect(dac_node, node)
        connect(adc_node, node)
    except Exception as e:
        print("sweep_voltage: connect failed:", e)
        return results

    _settle(0.01)

    try:
        for i in range(steps):
            if steps == 1:
                v_set = start_v
            else:
                frac = float(i) / float(steps - 1)
                v_set = start_v + (end_v - start_v) * frac
            try:
                dac_set(dac_channel, v_set)
            except Exception as e:
                print("sweep_voltage: dac_set failed:", e)
                break
            _settle(0.01)
            try:
                v_meas = adc_get(adc_channel)
            except Exception as e:
                print("sweep_voltage: adc_get failed:", e)
                v_meas = None
            results.append((v_set, v_meas))
    finally:
        if disconnect_after:
            _safe_disconnect(dac_node)
            _safe_disconnect(adc_node)

    return results

