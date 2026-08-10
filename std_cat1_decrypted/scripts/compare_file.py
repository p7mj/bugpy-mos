# diff.py
# Shows line-by-line differences between two text files (like Unix 'diff').
# Uses Python's built-in difflib — no external dependencies.
#
# Output format (unified-style, colour-coded):
#   Lines only in file A  shown in RED   with  -
#   Lines only in file B  shown in GREEN with  +
#   Shared context lines  shown plain    with  (space)
#
# Flags:
#   -u   unified diff (default — context around changes)
#   -s   simple diff  (only changed lines, no context)
#   -c N set context line count (default 3), e.g: diff -c 5 a.txt b.txt
#
# Examples:
#   diff old.txt new.txt
#   diff -s old.txt new.txt
#   diff -c 1 old.txt new.txt

import difflib
from pathlib import Path
from . import color_print

def _read(path):
    """Read a file and return its lines. Returns None on error."""
    try:
        return Path(path).read_text(errors="replace").splitlines(keepends=True)
    except Exception as e:
        color_print.cprint(f"diff: cannot read '{path}': {e}", "DARKRED")
        return None

def _print_unified(lines_a, lines_b, name_a, name_b, context):
    """Print a unified diff with colour-coded +/- lines."""
    diff = difflib.unified_diff(lines_a, lines_b, fromfile=name_a, tofile=name_b, n=context)
    found_any = False
    for line in diff:
        found_any = True
        line = line.rstrip("\n")
        if line.startswith("---") or line.startswith("+++"):
            color_print.cprint(line, "EMPHASIS")
        elif line.startswith("@@"):
            color_print.cprint(line, "ORANGE")
        elif line.startswith("-"):
            color_print.cprint(line, "DARKRED")
        elif line.startswith("+"):
            color_print.cprint(line, "GREEN")
        else:
            print(line)
    if not found_any:
        print("diff: files are identical")

def _print_simple(lines_a, lines_b, name_a, name_b):
    """Print only changed lines — no context, no headers."""
    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    found_any = False
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        found_any = True
        # Show removed lines in red
        for line in lines_a[i1:i2]:
            color_print.cprint(f"- {line.rstrip()}", "DARKRED")
        # Show added lines in green
        for line in lines_b[j1:j2]:
            color_print.cprint(f"+ {line.rstrip()}", "GREEN")
    if not found_any:
        print("diff: files are identical")

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
COMPARE FILE
Usage:
  compare_file [flags] {file_1} {file_2}

Files:
  file_1: the first file to compare
  file_2: the second file to compare

Flags:
  -s: simple mode. Changed lines only, no context.
  -c N: context lines for unified mode, default 3.
  -h: this help section

Notes:
  Makes life easier
""")
        return

    simple  = "-s" in args
    context = 3  # default context lines for unified diff

    # Parse optional -c N context count
    if "-c" in args:
        idx = args.index("-c")
        if idx + 1 < len(args) and args[idx + 1].isdigit():
            context = int(args[idx + 1])
            # Remove -c and its value so positional parsing stays clean
            args = args[:idx] + args[idx + 2:]
        else:
            color_print.cprint("diff: -c requires a number, e.g. -c 5", "DARKRED")
            return

    # Strip remaining flags to get positional file arguments
    positional = [a for a in args if not a.startswith("-")]

    if len(positional) != 2:
        color_print.cprint("diff: expected exactly 2 file arguments.", "DARKRED")
        return

    name_a, name_b = positional[0], positional[1]
    lines_a = _read(name_a)
    lines_b = _read(name_b)

    if lines_a is None or lines_b is None:
        return  # Error already printed by _read()

    if simple:
        _print_simple(lines_a, lines_b, name_a, name_b)
    else:
        _print_unified(lines_a, lines_b, name_a, name_b, context)
