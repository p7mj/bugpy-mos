# cat_file.py
# Prints the contents of one or more text files to the terminal (like Unix 'cat').

from pathlib import Path
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
CAT (concatenate)
Usage:
  cat {file} [flags]

Files:
  file: the file to print out

Flags:
  -h: this help section

Notes:
  A program to print out a text-like file
        """)
        return
    for item in args:
        path = Path(item)
        if not path.is_file():
            color_print.cprint(f"cat: '{item}' not found.", "DARKRED")
            continue
        try:
            print(path.read_text())
        except Exception as e:
            color_print.cprint(f"cat: {e}", "DARKRED")
