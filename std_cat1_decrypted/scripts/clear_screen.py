def main(args):
    if "-h" in args or "--help" in args:
        print("""
CLEAR SCREEN
Usage:
  clear_screen [flags]

Flags:
  -h: this help section

Notes:
  A program to clear all the clutter existing on the screen
        """)
    else:
        print("\033[2J\033[H")