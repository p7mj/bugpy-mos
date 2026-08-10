# sysinfo.py
# Prints information about the host system.
# Uses only Python stdlib — platform, os, sys. No pip installs needed.
#
# Shows: OS name, hostname, Python version, CPU count, RAM (if available).
#
# Example:
#   sysinfo

import platform
import os
import sys
from . import color_print

def main(args):
    if args in (["-h"], ["--help"]):
        print("""
SYSINFO
Usage:
  sysinfo [flags]

Flags:
  -h: this help section

Notes:
  Displays host information
        """)
        return

    color_print.cprint("System Info", "EMPHASIS")
    print(f"  OS        : {platform.system()} {platform.release()} ({platform.version()})")
    print(f"  Machine   : {platform.machine()}")
    print(f"  Hostname  : {platform.node()}")
    print(f"  Python    : {sys.version.split()[0]}")
    print(f"  CPU cores : {os.cpu_count()}")

    # RAM is available on most platforms via psutil, but we don't want
    # a hard dependency. Try it, and silently skip if not installed.
    try:
        import psutil
        ram = psutil.virtual_memory()
        total_gb = ram.total / (1024 ** 3)
        used_gb  = ram.used  / (1024 ** 3)
        print(f"  RAM       : {used_gb:.1f} GB used / {total_gb:.1f} GB total")
    except ImportError:
        pass  # psutil not available — skip RAM line rather than erroring
