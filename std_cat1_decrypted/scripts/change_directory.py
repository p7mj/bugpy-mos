import os
from . import color_print

def main(args):
    if len(args) == 0:
        # Default to home or just stay put if no path is provided
        return

    if "-h" in args or "--help" in args:
        print("""
CHANGE DIRECTORY
Usage:
  change_directory <folder> [flags]

Parameters:
  folder: the folder to change the current working directory to

Flags:
  -h: this help section

Notes:
  A program to change your position in the file structure
        """)
    else:
        target_dir = args[0]
        
        try:
            os.chdir(target_dir)
        except FileNotFoundError:
            color_print.cprint(f"cd: error: directory '{target_dir}' not found.", "DARKRED")
        except NotADirectoryError:
            color_print.cprint(f"cd: error: '{target_dir}' is not a directory.", "DARKRED")
        except PermissionError:
            color_print.cprint(f"cd: error: permission denied.", "DARKRED")