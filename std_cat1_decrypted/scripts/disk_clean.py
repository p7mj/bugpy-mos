# disk_clean.py
# Find large, old, or empty files to help free up disk space.
# Reports only — never deletes anything automatically.
# Use 'rm' to remove files after reviewing the list.

import os
import re
import time
from pathlib import Path
from datetime import datetime
from . import color_print

DEFAULT_LARGE_BYTES = 10 * 1024 * 1024   # 10 MB
DEFAULT_OLD_DAYS    = 60


def _parse_size(s):
    s = s.strip().lower()
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(kb|mb|gb|b)?", s)
    if not match:
        return None
    value = float(match.group(1))
    unit  = match.group(2) or "b"
    return int(value * {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}[unit])


def _human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _find_large(root, min_bytes):
    for item in root.rglob("*"):
        if item.is_file():
            try:
                size = item.stat().st_size
                if size >= min_bytes:
                    yield item, size
            except (PermissionError, OSError):
                pass


def _find_old(root, max_age_days):
    cutoff = time.time() - max_age_days * 86400
    for item in root.rglob("*"):
        if item.is_file():
            try:
                mtime = item.stat().st_mtime
                if mtime < cutoff:
                    yield item, datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            except (PermissionError, OSError):
                pass


def _find_empty(root):
    for item in root.rglob("*"):
        try:
            if item.is_file() and item.stat().st_size == 0:
                yield item, "empty file"
            elif item.is_dir() and not any(item.iterdir()):
                yield item, "empty folder"
        except (PermissionError, OSError):
            pass


def _section(title):
    print("")
    color_print.cprint(title, "EMPHASIS")
    color_print.cprint("─" * len(title), "DARKBLUE")


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
DISK CLEAN
Usage:
  disk_clean [flags] <params>

Parameters:
  Size for --large, e.g. 10mb, 500kb, 1gb
  Days for --old, e.g. 30, 60, 90

Flags:
  --large   Find files larger than the given size
  --old     Find files not modified in the given number of days
  --empty   Find empty files and empty folders
  --all     Run all checks with defaults (10mb, 60 days)
  -h:       this help section

Note:
  disk_clean only reports — it never deletes anything.
  Use rm to remove files after reviewing.
""")
        return

    root = Path(os.getcwd())
    did_something = False

    run_large = "--large" in args
    run_old   = "--old"   in args
    run_empty = "--empty" in args
    run_all   = "--all"   in args

    if run_all:
        run_large = run_old = run_empty = True

    if run_large:
        did_something = True
        if run_all:
            min_bytes = DEFAULT_LARGE_BYTES
        else:
            idx = args.index("--large")
            if idx + 1 >= len(args):
                color_print.cprint("disk_clean: --large requires a size e.g. 10mb", "DARKRED")
                return
            min_bytes = _parse_size(args[idx + 1])
            if min_bytes is None:
                color_print.cprint(
                    f"disk_clean: unknown size '{args[idx+1]}'. Use e.g. 10mb, 500kb.",
                    "DARKRED"
                )
                return

        _section(f"Large files  (> {_human_size(min_bytes)})  in {root}")
        results = sorted(_find_large(root, min_bytes), key=lambda x: x[1], reverse=True)
        if not results:
            print("  None found.")
        else:
            for path, size in results:
                color_print.cprint(f"  {_human_size(size):>10}  ", "ORANGE", sameline=True)
                print(str(path))
            total = sum(s for _, s in results)
            print(f"\n  {len(results)} files  —  {_human_size(total)} total")

    if run_old:
        did_something = True
        if run_all:
            max_days = DEFAULT_OLD_DAYS
        else:
            idx = args.index("--old")
            if idx + 1 >= len(args) or not args[idx + 1].isdigit():
                color_print.cprint("disk_clean: --old requires a number of days", "DARKRED")
                return
            max_days = int(args[idx + 1])

        _section(f"Old files  (not modified in {max_days}+ days)  in {root}")
        results = sorted(_find_old(root, max_days), key=lambda x: x[1])
        if not results:
            print("  None found.")
        else:
            for path, date in results:
                color_print.cprint(f"  {date}  ", "ORANGE", sameline=True)
                print(str(path))
            print(f"\n  {len(results)} files")

    if run_empty:
        did_something = True
        _section(f"Empty files and folders  in {root}")
        results = list(_find_empty(root))
        if not results:
            print("  None found.")
        else:
            for path, kind in results:
                color_print.cprint(f"  [{kind}]  ", "ORANGE", sameline=True)
                print(str(path))
            print(f"\n  {len(results)} items")

    if not did_something:
        color_print.cprint(
            "disk_clean: no flag given. Use --large, --old, --empty, or --all.",
            "DARKRED"
        )

    print("")