# Counts lines, words, and characters in a file (like Unix 'wc').

from pathlib import Path
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
WC
Usage:
  wc {file} [flags]

Files:
  file: a text or text-like file to count words in.

Flags:
  -h: this help section

Notes:
  Word count. Writer's dream.
        """)
        return
    for item in args:
        path = Path(item)
        if not path.is_file():
            color_print.cprint(f"wc: '{item}' not found.", "DARKRED")
            continue
        try:
            text = path.read_text()
            lines = text.count("\n")
            words = len(text.split())
            chars = len(text)
            print(f"wc: {item}  lines:{lines}  words:{words}  chars:{chars}")
        except Exception as e:
            color_print.cprint(f"wc: {e}", "DARKRED")
