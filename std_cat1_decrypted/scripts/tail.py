# tail_file.py
# Prints the last N lines of a file (like Unix 'tail').
# Defaults to 10 lines if N is not specified.

from pathlib import Path
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
TAIL
Usage:
  tail {file} <count> [flags]

Parameters:
  count: Last <count> lines to print

Files:
  file: what file to print

Flags:
  -h: this help section

Notes:
  Prints last N lines of a text-like document
        """)
        return
    path = Path(args[0])
    n = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 10
    if not path.is_file():
        color_print.cprint(f"tail: '{args[0]}' not found.", "DARKRED")
        return
    try:
        lines = path.read_text().splitlines()
        print("\n".join(lines[-n:]))
    except Exception as e:
        color_print.cprint(f"tail: {e}", "DARKRED")
