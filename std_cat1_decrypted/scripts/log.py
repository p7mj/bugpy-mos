# log.py
# Appends timestamped entries to config/log.txt inside the encrypted drive.
# Designed for script automation and audit trails, not manual note-taking
# (use 'notes' for that). Every entry gets a UTC timestamp automatically.
#
# Commands:
#   log <message>         — append a timestamped entry
#   log list              — print the full log
#   log list <N>          — print the last N entries
#   log clear             — wipe the log (asks for confirmation)
#   log tail              — live-follow the log (Ctrl+C to stop)
#
# Log file format — one entry per line:
#   [2025-08-14 13:42:01]  started backup
#
# Example .bugscript usage:
#   log "backup started"
#   zip backup.zip mydata
#   log "backup complete"

from pathlib import Path
from datetime import datetime, timezone
import time
from . import color_print

_LOG_FILE = Path(__file__).resolve().parent.parent / "config" / "log.txt"

def _timestamp():
    """Return a UTC timestamp string for log entries."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def _load():
    if not _LOG_FILE.exists():
        return []
    return _LOG_FILE.read_text().splitlines()

def _append(message):
    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_LOG_FILE, "a") as f:
        f.write(f"[{_timestamp()}]  {message}\n")

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
LOG
Usage:
  log <params> [flags]

Parameters:
  <message> (add a message)
  list (list all logs)
  list <N> (list last n logs)
  clear (clear all logs)
  tail (follow logs live)

Flags:
  -h: this help section

Notes:
  Either a manual log, or automated script logging.
  Intended for dev.
        """)
        return

    cmd = args[0]

    if cmd == "list":
        lines = _load()
        if not lines:
            print("log: log is empty")
            return
        # Optional count argument: log list 20
        if len(args) >= 2 and args[1].isdigit():
            lines = lines[-int(args[1]):]
        for line in lines:
            # Highlight the timestamp bracket in orange for readability
            if line.startswith("["):
                end = line.find("]")
                if end != -1:
                    color_print.cprint(line[:end + 1], "ORANGE", sameline=True)
                    print(line[end + 1:])
                    continue
            print(line)

    elif cmd == "clear":
        if not _LOG_FILE.exists():
            print("log: log is already empty")
            return
        confirm = input("log: clear the entire log? (y/N) ").strip().lower()
        if confirm == "y":
            _LOG_FILE.write_text("")
            print("log: cleared")
        else:
            print("log: cancelled")

    elif cmd == "tail":
        # Print existing log first, then wait for new entries (Ctrl+C to exit)
        print("log: following log — Ctrl+C to stop")
        lines = _load()
        for line in lines:
            print(line)
        try:
            last_size = _LOG_FILE.stat().st_size if _LOG_FILE.exists() else 0
            while True:
                time.sleep(0.5)
                if not _LOG_FILE.exists():
                    continue
                new_size = _LOG_FILE.stat().st_size
                if new_size > last_size:
                    with open(_LOG_FILE) as f:
                        f.seek(last_size)
                        for line in f:
                            print(line, end="")
                    last_size = new_size
        except KeyboardInterrupt:
            print("\nlog: stopped.")

    else:
        # Everything is the message — join all args back together
        message = " ".join(args)
        _append(message)
        print(f"log: [{_timestamp()}]  {message}")
