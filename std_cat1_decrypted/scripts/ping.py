# ping.py
# Pings a hostname or IP address and reports whether it's reachable.
# Calls the host OS ping command via subprocess — works on Windows, Linux, macOS.
#
# Examples:
#   ping google.com
#   ping 8.8.8.8
#   ping google.com 10     <- send 10 packets instead of default 4

import subprocess
import platform
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
PING [A-3-iii]
Usage:
  ping <params> <params>

Parameters:
  host    Hostname or IP address to ping
  count   Packets to send (optional, default 4)
""")
        return

    host  = args[0]
    count = args[1] if len(args) >= 2 and args[1].isdigit() else "4"

    # Flag differs between Windows (-n) and Unix (-c)
    flag = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", flag, count, host],
            capture_output=False  # Let output print directly to terminal
        )
        if result.returncode == 0:
            color_print.cprint(f"ping: {host} is reachable.", "GREEN")
        else:
            color_print.cprint(f"ping: {host} is unreachable.", "DARKRED")
    except FileNotFoundError:
        color_print.cprint("ping: 'ping' command not found on host system.", "DARKRED")
    except Exception as e:
        color_print.cprint(f"ping: error: {e}", "DARKRED")
