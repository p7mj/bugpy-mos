import threading
import time
import re
import sys
from . import color_print

# Registry of active timers: { id: (threading.Timer, message, end_time, flags) }
_active_timers = {}
_timer_id_counter = [0]
_lock = threading.Lock()

# Global state for the ringer
_is_ringing = threading.Event()

def _next_id():
    """Generate a simple incrementing timer ID."""
    with _lock:
        _timer_id_counter[0] += 1
        return _timer_id_counter[0]

def _parse_duration(s):
    """Parse duration strings like '5m' into seconds."""
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([smh])", s.strip().lower())
    if not match:
        return None
    value, unit = float(match.group(1)), match.group(2)
    return value * {"s": 1, "m": 60, "h": 3600}[unit]

def _ring_forever():
    """Loop that prints the ANSI bell character until _is_ringing is cleared."""
    while _is_ringing.is_set():
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(1) # Ring once per second

def _fire(timer_id, message, flags):
    """Called when countdown ends. Handles notifications and ringing logic."""
    
    # 1. Handle Notifications
    if "--no-notif" not in flags:
        print()
        color_print.cprint(f"[timer #{timer_id}] ", "ORANGE", sameline=True)
        color_print.cprint(message, "EMPHASIS")
        print()

    # 2. Handle Ringing
    if "--ding" in flags or "--ring" in flags:
        if not _is_ringing.is_set():
            _is_ringing.set()
            ring_thread = threading.Thread(target=_ring_forever, daemon=True)
            ring_thread.start()

    with _lock:
        _active_timers.pop(timer_id, None)

def main(args):
    if not args or args[0] in ("-h", "--help"):
        print("""
TIMER
Usage:
  timer <time> <message> [flags]

Parameters:
  time: number of time + a unit, e.g. 1s, 1m or 1h
  message: message to be displayed when done

Flags:
  --stop: stop the bell
  --no-notif: no terminal notification
  --ring: ring bell until ur brain explodes when timer is up (good when ur in vi)
  --ding: ring but ding, same lol.
  -h: this help section

Notes:
  This is a timer!
  Use --no-notif and --ding if you expect it to ring while in pyvi.
  --ding is really really loud on a raw TTY as it buzzes the motherboard...
        """)
        return

    # --- stop ringing ---
    if "--stop" in args:
        if _is_ringing.is_set():
            _is_ringing.clear()
            print("timer: ringer stopped")
        else:
            print("timer: nothing is ringing")
        return

    cmd = args[0]

    # --- list ---
    if cmd == "list":
        with _lock:
            if not _active_timers:
                print("timer: no active timers")
            else:
                print("timer: active timers")
                for tid, (t, msg, end_time, _) in _active_timers.items():
                    remaining = max(0, end_time - time.time())
                    secs = int(remaining)
                    print(f"  #{tid}  {secs}s remaining  — \"{msg}\"")
        return

    # --- cancel ---
    if cmd == "cancel":
        if len(args) < 2 or not args[1].isdigit():
            color_print.cprint("timer: provide a timer ID", "DARKRED")
            return
        tid = int(args[1])
        with _lock:
            entry = _active_timers.pop(tid, None)
        if entry:
            entry[0].cancel()
            print(f"timer: #{tid} cancelled")
        return

    # --- start a new timer ---
    # Extract flags from args
    flags = [a for a in args if a in ("--no-notif", "--ding", "--ring")]
    clean_args = [a for a in args if a not in flags]

    duration_str = clean_args[0]
    seconds = _parse_duration(duration_str)

    if seconds is None:
        color_print.cprint(f"timer: invalid duration '{duration_str}'", "DARKRED")
        return

    message = " ".join(clean_args[1:]) if len(clean_args) > 1 else "Time's up!"

    tid = _next_id()
    end_time = time.time() + seconds
    
    # Pass flags to the _fire function
    t = threading.Timer(seconds, _fire, args=[tid, message, flags])
    t.daemon = True

    with _lock:
        _active_timers[tid] = (t, message, end_time, flags)

    t.start()

    color_print.cprint(f"timer #{tid}", "ORANGE", sameline=True)
    print(f" set for {int(seconds)}s — \"{message}\"")