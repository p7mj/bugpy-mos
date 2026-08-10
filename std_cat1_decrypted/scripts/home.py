from pathlib import Path
import os

def main(args):
    if "-h" in args or "--help" in args:
        print("""
HOME
Usage:
  home [flags]

Flags:
  -h: this help section

Notes:
  A program for you to return to the embrace of cat1.
  Originally developed so that my proof of concept BUGPy virus "pvirus" would work.
        """)
        return
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent.parent
    os.chdir(script_dir)