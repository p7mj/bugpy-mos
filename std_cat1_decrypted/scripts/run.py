# run.py
# Passes a command directly to the host system shell and prints its output.
# Useful for running external programs that aren't BUGPy packages.
#
# The entire args list is joined into one command string and passed to the
# host OS via subprocess. stdout and stderr both print to the terminal live.
#
# Example:
#   run python --version
#   run pip install cryptography
#   run ipconfig       (Windows)
#   run uname -a       (Unix)
#
# Note: this runs on the HOST system, not inside the BUGPy shell environment.
# It does NOT affect the BUGPy shell's current directory.

import subprocess
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
RUN
Usage:
  run <bash> [flags]

Parameters:
  bash: a bash command

Flags:
  -h: this help section

Notes:
  run a unix command outside of bugpy
        """)
        return

    # Join all arguments into a single command string
    command = " ".join(args)

    try:
        # shell=True lets the host OS parse the command naturally
        # (handles pipes, redirection, etc. if the host supports it)
        result = subprocess.run(command, shell=True)
        # Non-zero exit code means the command reported an error
        if result.returncode != 0:
            color_print.cprint(f"run: command exited with code {result.returncode}", "ORANGE")
    except Exception as e:
        color_print.cprint(f"run: failed to execute '{command}': {e}", "DARKRED")
