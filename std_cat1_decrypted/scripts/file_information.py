# Shows basic info about a file or directory (like Unix 'stat').
# Reports type, size in bytes, and last modified time.

import os
from pathlib import Path
from datetime import datetime
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
FILE INFORMATION
Usage:
  file_information {file} [flags]

Files:
  file: file to get information of

Flags
  -h: this help section

Notes:
  A program to make you more knowledgable regarding your files
        """)
        return
    for item in args:
        path = Path(item)
        if not path.exists():
            color_print.cprint(f"stat: '{item}' not found.", "DARKRED")
            continue
        s = path.stat()
        kind = "directory" if path.is_dir() else "file"
        size = s.st_size
        modified = datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"stat: {item}")
        print(f"  type:     {kind}")
        print(f"  size:     {size} bytes")
        print(f"  modified: {modified}")
