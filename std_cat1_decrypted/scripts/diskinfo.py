# diskinfo.py
# Shows disk space for the current drive (or a given path).
# Uses shutil.disk_usage from stdlib — no pip installs needed.
#
# Examples:
#   diskinfo
#   diskinfo C:\
#   diskinfo /home

import shutil
import os
from . import color_print

def _bar(used, total, width=30):
    """Return a simple ASCII progress bar for disk usage."""
    if total == 0:
        return "[" + "-" * width + "]"
    filled = int(width * used / total)
    return "[" + "#" * filled + "-" * (width - filled) + "]"

def main(args):
    if args in (["-h"], ["--help"]):
        print("""
DISKINFO
Usage:
  diskinfo <path> [flags]

Parameters:
  path: the path to scan. If none, uses current disk..

Flags:
  -h: this help section

Notes:
  It's time to take out the trash!
""")
        return

    path = args[0] if args else os.getcwd()

    try:
        usage = shutil.disk_usage(path)
    except Exception as e:
        color_print.cprint(f"diskinfo: {e}", "DARKRED")
        return

    total_gb = usage.total / (1024 ** 3)
    used_gb  = usage.used  / (1024 ** 3)
    free_gb  = usage.free  / (1024 ** 3)
    pct      = (usage.used / usage.total * 100) if usage.total else 0

    color_print.cprint("Disk Info", "EMPHASIS")
    print(f"  Path  : {path}")
    print(f"  Total : {total_gb:.2f} GB")
    print(f"  Used  : {used_gb:.2f} GB  ({pct:.1f}%)")
    print(f"  Free  : {free_gb:.2f} GB")
    print(f"  Usage : {_bar(usage.used, usage.total)} {pct:.0f}%")
