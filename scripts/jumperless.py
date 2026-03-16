#!/usr/bin/env python3
"""
Jumperless V5 host helper

- Detects the Jumperless V5 MicroPython REPL port
- Executes MicroPython code via the raw REPL protocol
- Provides simple helpers for state and filesystem operations

This script is designed to be called by an agent via shell.
"""

import argparse
import os
import sys
import time
from typing import Iterable, List, Optional, Tuple

try:
    import serial  # type: ignore
    from serial.tools import list_ports  # type: ignore
except ImportError:
    print("pyserial is required. Install with: pip install pyserial", file=sys.stderr)
    sys.exit(1)


JUMPERLESS_VID = 0x1D50
JUMPERLESS_PID = 0xACAB
CACHE_FILE = ".jumperless_port"


def iter_candidate_ports() -> Iterable[serial.tools.list_ports_common.ListPortInfo]:
    """Yield all serial ports that might plausibly be a Jumperless device."""
    for p in list_ports.comports():
        yield p


def looks_like_jumperless(port: serial.tools.list_ports_common.ListPortInfo) -> bool:
    vid = getattr(port, "vid", None)
    pid = getattr(port, "pid", None)
    desc = (port.description or "").lower()
    hwid = (port.hwid or "").lower()
    if vid == JUMPERLESS_VID and pid == JUMPERLESS_PID:
        return True
    if "jumperless" in desc or "jlv5" in desc or "jumperless" in hwid:
        return True
    return False


def preferred_order_key(port: serial.tools.list_ports_common.ListPortInfo) -> Tuple[int, str]:
    """
    On macOS, ports are typically /dev/cu.usbmodemJLV5port1,3,5,7.
    MicroPython REPL is on the 3rd CDC function (port5).
    Prefer ordering so that likely REPL ports come first.
    """
    name = port.device or ""
    # strong preference for explicit JLV5port5
    if "JLV5port5" in name or "jlv5port5" in name:
        return (0, name)
    # then other JLV5 ports
    if "JLV5port" in name or "jlv5port" in name:
        return (1, name)
    # then Jumperless-looking devices
    if looks_like_jumperless(port):
        return (2, name)
    # everything else last
    return (3, name)


def raw_repl_probe(port_path: str, timeout: float = 2.0) -> bool:
    """
    Try to see if a port speaks MicroPython REPL by:
    - Opening at 115200
    - Sending Ctrl-C twice and a newline
    - Looking for a >>> prompt
    """
    try:
        with serial.Serial(port_path, 115200, timeout=timeout) as ser:
            ser.reset_input_buffer()
            ser.write(b"\r\x03\x03\r")
            ser.flush()
            time.sleep(0.3)
            data = ser.read(512)
            if b">>> " in data:
                return True
            # Try once more with a plain newline
            ser.write(b"\r")
            ser.flush()
            time.sleep(0.3)
            data += ser.read(512)
            return b">>> " in data
    except Exception:
        return False


def detect_port(explicit: Optional[str] = None) -> str:
    """
    Detect the Jumperless MicroPython REPL port.
    Order of precedence:
      1. Explicit argument
      2. Cached value in .jumperless_port (if still present)
      3. Name/VID/PID heuristics + probing for >>> prompt
    """
    if explicit:
        return explicit

    # Cached port
    if os.path.exists(CACHE_FILE):
        cached = open(CACHE_FILE, "r", encoding="utf-8").read().strip()
        if cached:
            if any(p.device == cached for p in list_ports.comports()):
                return cached

    ports = list(iter_candidate_ports())
    if not ports:
        raise SystemExit("No serial ports found. Please connect the Jumperless and try again.")

    # Sort by preference: JLV5port5, other JLV5, other Jumperless, then everything else
    ports.sort(key=preferred_order_key)

    # First, accept any port that strongly looks like Jumperless and passes the REPL probe
    for p in ports:
        if looks_like_jumperless(p):
            if raw_repl_probe(p.device):
                _cache_port(p.device)
                return p.device

    # Next, probe the remaining ports in order
    for p in ports:
        if raw_repl_probe(p.device):
            _cache_port(p.device)
            return p.device

    # Nothing worked – print candidate list and exit
    print("Could not automatically find a Jumperless MicroPython REPL port.\n", file=sys.stderr)
    print("Detected serial ports:", file=sys.stderr)
    for p in ports:
        print(f"  {p.device}  [{p.description}]", file=sys.stderr)
    raise SystemExit(
        "Please run again with --port /path/to/port (e.g. /dev/cu.usbmodemJLV5port5 or COM7), "
        "or connect the Jumperless and try again."
    )


def _cache_port(port_path: str) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(port_path.strip() + "\n")
    except Exception:
        # Caching is a convenience; failure should not abort
        pass


def enter_raw_repl(ser: serial.Serial, soft_reboot: bool = False) -> None:
    """Enter raw REPL on an already-open serial connection."""
    ser.reset_input_buffer()
    ser.write(b"\r\x03\x03")  # interrupt any running code
    ser.flush()
    time.sleep(0.1)
    ser.write(b"\r\x01")  # Ctrl-A: raw REPL
    ser.flush()
    _read_until(ser, b"raw REPL; CTRL-B to exit\r\n", timeout=2.0)
    if soft_reboot:
        ser.write(b"\x04\x03")  # soft reboot in raw mode
        ser.flush()
        _read_until(ser, b"raw REPL; CTRL-B to exit\r\n", timeout=2.0)


def exit_raw_repl(ser: serial.Serial) -> None:
    """Exit raw REPL back to normal REPL."""
    try:
        ser.write(b"\x02")  # Ctrl-B
        ser.flush()
    except Exception:
        pass


def _read_until(ser: serial.Serial, marker: bytes, timeout: float = 5.0) -> bytes:
    """Read until marker appears or timeout expires."""
    end_time = time.time() + timeout
    buf = b""
    while time.time() < end_time:
        chunk = ser.read(64)
        if chunk:
            buf += chunk
            if marker in buf:
                return buf
        else:
            time.sleep(0.01)
    return buf


def _read_exact(ser: serial.Serial, n: int, timeout: float = 5.0) -> bytes:
    end_time = time.time() + timeout
    buf = b""
    while len(buf) < n and time.time() < end_time:
        chunk = ser.read(n - len(buf))
        if chunk:
            buf += chunk
        else:
            time.sleep(0.01)
    return buf


def _read_raw_block(ser: serial.Serial, timeout: float = 5.0) -> bytes:
    """Read one raw-REPL output block terminated by Ctrl-D."""
    end_time = time.time() + timeout
    buf = b""
    while time.time() < end_time:
        bch = ser.read(1)
        if not bch:
            time.sleep(0.01)
            continue
        if bch == b"\x04":
            return buf
        buf += bch
    raise TimeoutError("Timed out waiting for raw REPL block terminator")


def _normalize_code(code: str) -> str:
    normalized = code.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized


def raw_exec(ser: serial.Serial, code: str, timeout: float = 8.0) -> Tuple[str, str]:
    """
    Execute code in raw REPL and return (stdout, stderr) as strings.
    Mirrors the logic in JumperIDE's rawmode.js:
      - write code
      - send Ctrl-D
      - read 2-byte status (OK or error)
      - read stdout until Ctrl-D
      - read stderr until Ctrl-D
    """
    # Consume any pending prompt bytes before sending payload
    ser.write(b"\r")
    ser.flush()
    time.sleep(0.05)
    ser.reset_input_buffer()

    payload = _normalize_code(code).encode("utf-8")
    ser.write(payload + b"\x04")
    ser.flush()

    status = _read_exact(ser, 2, timeout=timeout)
    if len(status) < 2:
        raise TimeoutError("Timed out waiting for raw REPL status bytes")

    out = _read_raw_block(ser, timeout=timeout)
    err = _read_raw_block(ser, timeout=timeout)

    out_text = out.decode("utf-8", errors="ignore")
    err_text = err.decode("utf-8", errors="ignore")
    if status != b"OK" and not err_text.strip():
        err_text = "Device returned non-OK raw REPL status (possible syntax error)."
    return out_text, err_text


def _load_exec_code(args: argparse.Namespace) -> str:
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if args.stdin:
        return sys.stdin.read()
    if args.code is not None:
        return args.code
    raise SystemExit("No code provided. Use positional CODE, --file, or --stdin.")


def _read_step_lines(path: str) -> List[str]:
    """
    Read step lines for guided mode.
    - Each non-empty line is a step.
    - Lines starting with '#' are ignored.
    """
    steps: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            steps.append(line)
    if not steps:
        raise SystemExit("Guide file has no runnable steps. Add one step per non-empty line.")
    return steps


def _build_guide_script(steps: List[str], oled: bool = True) -> str:
    lines = [
        "def _jl_wait_for_continue():",
        "    # Prefer probe button (blocking). Fallback to clickwheel button polling.",
        "    try:",
        "        probe_button(True)",
        "        return",
        "    except Exception:",
        "        pass",
        "    try:",
        "        while True:",
        "            try:",
        "                if clickwheel_get_button():",
        "                    break",
        "            except Exception:",
        "                pass",
        "            sleep_ms(40)",
        "        # Debounce / wait for release if API supports it",
        "        for _ in range(25):",
        "            try:",
        "                if not clickwheel_get_button():",
        "                    break",
        "            except Exception:",
        "                break",
        "            sleep_ms(20)",
        "    except Exception:",
        "        # Last resort: don't block forever if no button API exists",
        "        sleep_ms(800)",
        "",
        f"_jl_steps = [{', '.join([repr(s) for s in steps])}]",
        "for _jl_i, _jl_msg in enumerate(_jl_steps):",
        "    _jl_header = 'STEP {}/{}: '.format(_jl_i + 1, len(_jl_steps))",
        "    print(_jl_header + _jl_msg)",
    ]
    if oled:
        lines.extend(
            [
                "    try:",
                "        oled_clear()",
                "        oled_print(_jl_header + _jl_msg)",
                "    except Exception:",
                "        pass",
            ]
        )
    lines.extend(
        [
            "    _jl_wait_for_continue()",
            "print('Guide complete')",
        ]
    )
    return "\n".join(lines) + "\n"


def cmd_detect(args: argparse.Namespace) -> None:
    port = detect_port(explicit=args.port)
    print(port)


def cmd_exec(args: argparse.Namespace) -> None:
    port = detect_port(explicit=args.port)
    with serial.Serial(port, 115200, timeout=1) as ser:
        enter_raw_repl(ser, soft_reboot=args.soft_reboot)
        try:
            code = _load_exec_code(args)
            try:
                out, err = raw_exec(ser, code, timeout=args.timeout)
            except TimeoutError as exc:
                print(f"Execution timed out: {exc}", file=sys.stderr)
                print("Tip: run multi-line scripts with --file to avoid malformed shell quoting.", file=sys.stderr)
                sys.exit(1)
        finally:
            exit_raw_repl(ser)
        if err:
            # Print stderr to stderr so the agent can distinguish
            print(err, file=sys.stderr)
            # Non-zero exit to signal failure
            sys.exit(1)
        if out:
            print(out, end="" if out.endswith("\n") else "\n")


def cmd_guide(args: argparse.Namespace) -> None:
    steps = _read_step_lines(args.file)
    code = _build_guide_script(steps, oled=not args.no_oled)
    port = detect_port(explicit=args.port)
    with serial.Serial(port, 115200, timeout=1) as ser:
        enter_raw_repl(ser, soft_reboot=False)
        try:
            try:
                out, err = raw_exec(ser, code, timeout=args.timeout)
            except TimeoutError as exc:
                print(f"Guide timed out: {exc}", file=sys.stderr)
                sys.exit(1)
        finally:
            exit_raw_repl(ser)
        if err:
            print(err, file=sys.stderr)
            sys.exit(1)
        if out:
            print(out, end="" if out.endswith("\n") else "\n")


def cmd_state(args: argparse.Namespace) -> None:
    port = detect_port(explicit=args.port)
    with serial.Serial(port, 115200, timeout=1) as ser:
        enter_raw_repl(ser, soft_reboot=False)
        try:
            out, err = raw_exec(ser, "import json\nprint(get_state())\n", timeout=args.timeout)
        finally:
            exit_raw_repl(ser)
        if err:
            print(err, file=sys.stderr)
            sys.exit(1)
        print(out, end="" if out.endswith("\n") else "\n")


def cmd_fs(args: argparse.Namespace) -> None:
    """
    Walk the filesystem and print lines of the form:
      f|/path/to/file|size
      d|/path/to/dir|size
    """
    port = detect_port(explicit=args.port)
    script = """
import os
def walk(p):
  for n in os.listdir(p if p else '/'):
    fn = p + '/' + n
    try:
      s = os.stat(fn)
    except:
      s = (0,)*7
    try:
      if s[0] & 0x4000 == 0:
        print('f|' + fn + '|' + str(s[6]))
      elif n not in ('.','..'):
        print('d|' + fn + '|' + str(s[6]))
        walk(fn)
    except:
      print('f|' + p + '/???|' + str(s[6]))
walk('')
"""
    with serial.Serial(port, 115200, timeout=1) as ser:
        enter_raw_repl(ser, soft_reboot=False)
        try:
            out, err = raw_exec(ser, script, timeout=args.timeout)
        finally:
            exit_raw_repl(ser)
        if err:
            print(err, file=sys.stderr)
            sys.exit(1)
        print(out, end="" if out.endswith("\n") else "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jumperless V5 host helper")
    parser.add_argument("--port", help="Override detected port path (e.g. /dev/cu.usbmodemJLV5port5, COM7)", default=None)

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_detect = sub.add_parser("detect", help="Detect and print the Jumperless MicroPython REPL port")
    p_detect.set_defaults(func=cmd_detect)

    p_exec = sub.add_parser("exec", help="Execute MicroPython via raw REPL")
    p_exec.add_argument("code", nargs="?", default=None, help="Inline Python code to execute on device")
    p_exec.add_argument("--file", help="Read Python code from file", default=None)
    p_exec.add_argument("--stdin", action="store_true", help="Read Python code from stdin")
    p_exec.add_argument("--soft-reboot", action="store_true", help="Soft reboot into raw REPL before executing")
    p_exec.add_argument("--timeout", type=float, default=8.0, help="Timeout in seconds for command execution")
    p_exec.set_defaults(func=cmd_exec)

    p_guide = sub.add_parser("guide", help="Run step-by-step guided instructions with button-gated continue")
    p_guide.add_argument("--file", required=True, help="Text file with one step per line")
    p_guide.add_argument("--no-oled", action="store_true", help="Do not render step text on OLED")
    p_guide.add_argument("--timeout", type=float, default=120.0, help="Timeout in seconds for guide execution")
    p_guide.set_defaults(func=cmd_guide)

    p_state = sub.add_parser("state", help="Print get_state() JSON from the device")
    p_state.add_argument("--timeout", type=float, default=5.0, help="Timeout in seconds for command execution")
    p_state.set_defaults(func=cmd_state)

    p_fs = sub.add_parser("fs", help="List filesystem contents on the device")
    p_fs.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds for command execution")
    p_fs.set_defaults(func=cmd_fs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

