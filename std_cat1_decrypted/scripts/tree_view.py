# tree_view.py
# Displays a directory tree with branch characters (like Unix 'tree').
# Directories are shown in blue; files in default color.

import os
from pathlib import Path
from . import color_print

def _tree(path, prefix=""):
    """Recursively print the directory tree with box-drawing characters."""
    entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        if entry.is_dir():
            color_print.cprint(f"{prefix}{connector}{entry.name}/", "DARKBLUE")
            # Extend the prefix for children: space under last entry, bar otherwise
            extension = "    " if i == len(entries) - 1 else "│   "
            _tree(entry, prefix + extension)
        else:
            print(f"{prefix}{connector}{entry.name}")

def main(args):
    if args in (["-h"], ["--help"]):
        print("""
TREE VIEW
Usage:
  tree_view <path> [flags]

Parameters:
  If none, creates a tree diagram of the current path.
  path: what path to tree

Notes:
  It's not a real tree!

Flags:
  -h: this help section
""")
        return
    target = Path(args[0]) if args else Path(os.getcwd())
    if not target.is_dir():
        color_print.cprint(f"tree: '{target}' is not a directory.", "DARKRED")
        return
    color_print.cprint(f"{target}/", "DARKBLUE")
    _tree(target)
    print()
