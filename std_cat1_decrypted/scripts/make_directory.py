from pathlib import Path
import os

def main(args):
    if not args:
        print("make_directory: no arguments were given")
        return
    if "-h" in args or "--help" in args:
        print("""
MAKE DIRECTORY
Usage:
  make_directory (<directory> ... <directory>) [flags]

Parameters:
  directory: the directory name, can take one or multiple.

Flags:
  -h: this help section

Notes:
  To make you organized. Because you really need folders.
        """)
    else:
        for item in args:
            # Get the ABSOLUTE path to be 100% sure where it's going
            dir_path = Path(item).resolve()
            
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                # This line is key: it tells you EXACTLY where it went
            except Exception as e:
                print(f"make_directory: error creating directory {item}: {e}")
