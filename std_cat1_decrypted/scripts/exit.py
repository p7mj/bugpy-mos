import sys
from . import color_print
def main(args):
    if "-h" in args or "--help" in args:
        print("""
EXIT
Usage:
  exit [flags]

Flags:
  A program to exit BUGPy.

Notes:
  Why are you exiting BUGPy?
  Well... it's unreasonable NOT to allow you to. This is why this command exists.
  This is P7MJ. Out.
        """)
    else:
        color_print.cprint("Exiting BUGPy!", "GREEN")
        sys.exit(0)
