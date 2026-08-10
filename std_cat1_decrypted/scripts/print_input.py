# CONTINUE HELP HERE

def main(args):
    if "-h" in args or "--help" in args:
        print("""
PRINT INPUT
Usage:
  print_input <printout> [flags]

Parameters:
  printout: What you want to print. No quotes. Spaces are allowed.

Flags
  -h: this help section

Notes:
  To make debugging easier in .BUG scripts
        """)
    else:
        buffer = ""
        for item in args:
            buffer += f"{item} "
        print(buffer)