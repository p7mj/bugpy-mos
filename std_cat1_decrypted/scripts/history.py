from pathlib import Path
from collections import deque

BASE_DIR = Path(__file__).parent.parent

def print_log_tail(n):

    try:
        with open(BASE_DIR / "history" / "history.txt", "r") as f:
            last_lines = deque(f, maxlen=n)
            print(f"COMMAND HISTORY (last {n} entries)", end="")
            for line in last_lines:
                print(line.rstrip())
    except Exception as e:
        print(f"history: could not read file: {e}")

def main(args):
    if not args:
        print("COMMAND HISTORY", end="")
        with open(BASE_DIR / "history" / "history.txt", 'r') as f:
            for line in f:
                print(line.rstrip())

    elif len(args) == 1 and args[0].isdigit():
        try:
            print_log_tail(int(args[0]))
        except:
            print("history: incorrect parameters.")
    elif args == ["--wipe"] or args == ["-w"] or args == ["--clear"] or args == ["-c"]:
        with open(BASE_DIR / "history" / "history.txt", 'w') as f:
            pass
    elif "-h" in args or "--help" in args:
        print("""
HISTORY
Usage:
  history <N> [flags]

Parameters:
  If none, will print entire command history.
  N: last N lines to print. Integer. Optional.

Flags:
  -w: wipe history
  -c: wipe history
  -h: this help section
        """)
    else:
        print("history: invalid parameters.")