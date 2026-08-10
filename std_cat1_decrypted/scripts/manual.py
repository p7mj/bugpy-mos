from . import color_print
def main(args):
    if "-h" in args or "--help" in args:
        print("""
MANUAL
Usage:
  manual [flags]

Flags:
  -h: help section of the manual command

Notes:
  this manual section really needs help.
        """)
    else:
        # Title
        color_print.cprint("BUGPy Manual", "ORANGE")
        print("=" * 40)

        print("See the Universal Binder of Knowledge. Will attach link later.")
        # get files from help folder
        # List them
        # allow user to open them
        # maybe someday in the future
        # Maybe even make a sys folder

        # Newline
        print("")
