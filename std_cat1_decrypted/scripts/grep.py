# grep.py
# Searches for a text pattern inside one or more files (like Unix 'grep').
# Prints matching lines with the filename and line number prefixed.
#
# Flags:
#   -i   case-insensitive matching
#   -n   show line numbers (on by default, use -N to hide)
#   -r   search recursively inside a directory
#   -l   only print filenames that have at least one match (no line content)
#
# Examples:
#   grep hello myfile.txt
#   grep -i hello myfile.txt
#   grep -r def .
#   grep -rl import .

import os
import re
from pathlib import Path
from . import color_print

def search_file(path, pattern, flags, show_lines, names_only):
    """
    Search a single file for lines matching pattern.
    Returns True if at least one match was found.
    """
    try:
        text = path.read_text(errors="replace")
    except Exception as e:
        color_print.cprint(f"grep: cannot read '{path}': {e}", "DARKRED")
        return False

    found = False
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line, flags):
            found = True
            if names_only:
                # -l mode: just print the filename once and stop
                print(str(path))
                return True
            if show_lines:
                color_print.cprint(str(path), "DARKBLUE", sameline=True)
                print(f":{i}: ", end="")
            else:
                color_print.cprint(str(path), "DARKBLUE", sameline=True)
                print(": ", end="")
            print(line)
    return found

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
GREP
Usage:
  grep [flags] <pattern> ({files} ... {files})

Parameters:
  pattern: what to search for, usually a string without quotes.

Files:
  files: files and folders. Can take one or multiple

Flags:
    -i: case-insensitive
    -r: recursive (searches directories)
    -l: list matching filenames only
    -h: this help section

Notes:
  SpyDrone made this.
  It's a command to make your life easier.
        """)
        return

    # Parse flags
    case_insensitive = "-i" in args
    recursive        = "-r" in args
    names_only       = "-l" in args

    # Strip all flags from args
    positional = [a for a in args if not a.startswith("-")]

    if len(positional) < 2:
        color_print.cprint("grep: expected <pattern> and at least one <file/dir>.", "DARKRED")
        return

    pattern   = positional[0]
    targets   = positional[1:]
    re_flags  = re.IGNORECASE if case_insensitive else 0

    # Validate the pattern before scanning any files
    try:
        re.compile(pattern, re_flags)
    except re.error as e:
        color_print.cprint(f"grep: invalid pattern '{pattern}': {e}", "DARKRED")
        return

    for target in targets:
        path = Path(target)

        if path.is_file():
            search_file(path, pattern, re_flags, show_lines=True, names_only=names_only)

        elif path.is_dir():
            if not recursive:
                color_print.cprint(f"grep: '{target}' is a directory. Use -r to search recursively.", "DARKRED")
                continue
            # Walk the directory tree and search every file
            for file in sorted(path.rglob("*")):
                if file.is_file():
                    search_file(file, pattern, re_flags, show_lines=True, names_only=names_only)

        else:
            color_print.cprint(f"grep: '{target}' not found.", "DARKRED")
