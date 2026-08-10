from pathlib import Path
from . import color_print

def main(args):
    # Set the directory path
    script_dir = Path(__file__).resolve().parent
    dir_path = Path("")

    # Use the current script's directory or specify a path
    base_path = Path(__file__).resolve().parent 
    if args == []:
        for entry in dir_path.iterdir():
            if entry.is_dir():
                color_print.cprint(f"[FOLDER] {entry.name}", "DARKBLUE")
            elif entry.is_file():
                print(f"[FILE]   {entry.name}")
        print()
    elif "--help" in args or "-h" in args:
        print("""
LIST FILES
Usage:
  list_files [flags]

Flags:
  -h: this help section

Notes:
  A program to list the folders and files in the current directory.
        """)
    else:
        print("list_files: Invalid arguments, try using none?")
