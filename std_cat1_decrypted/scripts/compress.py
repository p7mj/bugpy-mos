# compress.py
# Compress or decompress individual files using gzip.
# Pure stdlib gzip module — no external tools needed.
# Works on Windows and Linux.
#
# Compressing a file creates filename.gz and by default removes the original
# (matching gzip behaviour). Decompressing restores the original.
#
# For compressing multiple files or whole directories, use 'tar' instead.
# tar creates a .tar.gz which handles directories.
# compress/decompress is for single files only.
#
# Why gzip over zip for single files?
#   gzip is smaller and faster for single files.
#   .gz is the standard on Linux — scripts, logs, and backups commonly use it.
#   zip wraps files in a container; gzip just compresses the stream directly.

import gzip
import os
import shutil
from pathlib import Path
from . import color_print

_CHUNK = 65536   # read/write in 64KB chunks to handle large files efficiently


def _human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _compress(source_path, dest_path, keep, level):
    """
    Compress source_path to dest_path using gzip.
    level: 1 (fastest) to 9 (best compression), default 6.
    keep:  if True, keep the original file after compression.
    """
    src  = Path(source_path)
    dest = Path(dest_path)

    if not src.exists():
        color_print.cprint(f"compress: '{source_path}' not found.", "DARKRED")
        return False

    if src.is_dir():
        color_print.cprint(
            f"compress: '{source_path}' is a directory. Use 'tar' for directories.",
            "DARKRED"
        )
        return False

    original_size = src.stat().st_size

    try:
        with open(src, 'rb') as f_in:
            with gzip.open(str(dest), 'wb', compresslevel=level) as f_out:
                while True:
                    chunk = f_in.read(_CHUNK)
                    if not chunk:
                        break
                    f_out.write(chunk)

        compressed_size = dest.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100 if original_size else 0

        color_print.cprint(
            f"compress: '{src.name}'  →  '{dest.name}'", "GREEN"
        )
        print(
            f"  {_human_size(original_size)}  →  {_human_size(compressed_size)}"
            f"  ({ratio:.1f}% smaller)"
        )

        if not keep:
            src.unlink()

        return True

    except PermissionError:
        color_print.cprint(
            f"compress: permission denied writing '{dest}'", "DARKRED"
        )
        return False
    except Exception as e:
        color_print.cprint(f"compress: failed — {e}", "DARKRED")
        # Clean up partial output file
        if dest.exists():
            dest.unlink()
        return False


def _decompress(source_path, dest_path, keep):
    """
    Decompress a .gz file to dest_path.
    keep: if True, keep the .gz file after decompression.
    """
    src = Path(source_path)

    if not src.exists():
        color_print.cprint(f"compress: '{source_path}' not found.", "DARKRED")
        return False

    # Verify it's actually a gzip file before trying
    try:
        with gzip.open(str(src), 'rb') as test:
            test.read(1)   # read one byte to trigger format check
    except gzip.BadGzipFile:
        color_print.cprint(
            f"compress: '{source_path}' is not a valid gzip file.", "DARKRED"
        )
        return False
    except Exception:
        pass

    dest = Path(dest_path)

    try:
        with gzip.open(str(src), 'rb') as f_in:
            with open(str(dest), 'wb') as f_out:
                while True:
                    chunk = f_in.read(_CHUNK)
                    if not chunk:
                        break
                    f_out.write(chunk)

        compressed_size   = src.stat().st_size
        decompressed_size = dest.stat().st_size
        ratio = (decompressed_size / compressed_size) if compressed_size else 0

        color_print.cprint(
            f"compress: '{src.name}'  →  '{dest.name}'", "GREEN"
        )
        print(
            f"  {_human_size(compressed_size)}  →  {_human_size(decompressed_size)}"
            f"  ({ratio:.1f}x expansion)"
        )

        if not keep:
            src.unlink()

        return True

    except PermissionError:
        color_print.cprint(
            f"compress: permission denied writing '{dest}'", "DARKRED"
        )
        return False
    except Exception as e:
        color_print.cprint(f"compress: failed — {e}", "DARKRED")
        if dest.exists():
            dest.unlink()
        return False


def _cmd_compress(args, keep, level):
    """Handle the compress direction — one or more files."""
    if not args:
        color_print.cprint(
            "compress: expected at least one file.", "DARKRED"
        )
        return

    for source in args:
        src  = Path(source)
        dest = src.with_suffix(src.suffix + ".gz")

        # Don't overwrite an existing .gz without asking
        if dest.exists():
            confirm = input(
                f"compress: '{dest}' already exists. Overwrite? (y/N) "
            ).strip().lower()
            if confirm != "y":
                print(f"compress: skipped '{source}'")
                continue

        _compress(source, str(dest), keep, level)


def _cmd_decompress(args, keep):
    """Handle the decompress direction — one or more .gz files."""
    if not args:
        color_print.cprint(
            "compress: expected at least one .gz file.", "DARKRED"
        )
        return

    for source in args:
        src = Path(source)

        # Determine output filename — strip the .gz
        if src.name.endswith(".gz"):
            dest = src.with_name(src.name[:-3])
        else:
            # Not a .gz extension — still try, output to same name + .out
            color_print.cprint(
                f"compress: '{source}' doesn't end in .gz — trying anyway.",
                "ORANGE"
            )
            dest = src.with_name(src.name + ".out")

        # Don't overwrite existing file without asking
        if dest.exists():
            confirm = input(
                f"compress: '{dest}' already exists. Overwrite? (y/N) "
            ).strip().lower()
            if confirm != "y":
                print(f"compress: skipped '{source}'")
                continue

        _decompress(source, str(dest), keep)


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""\
COMPRESS [A-3-iii]
Usage:
  compress {files} [flags]
  compress -d {files} [flags]

Files:
  One or more files to compress (or .gz files to decompress with -d)
  Directories are not supported — use tar for directories

Flags:
  -d        Decompress instead of compress
  -k        Keep the original file (default: removes it after)
  -1 to -9  Compression level. -1 fastest, -9 smallest (default: -6)

Note: compress works on single files only.
      For directories use: tar create archive.tar.gz folder/""")
        return

    # Parse flags
    decompress = "-d" in args
    keep       = "-k" in args
    level      = 6   # default

    # Check for -1 through -9 level flags
    for a in args:
        if len(a) == 2 and a[0] == '-' and a[1].isdigit():
            level = int(a[1])
            break

    # Strip all flags leaving only file paths
    files = [
        a for a in args
        if not (a.startswith('-') and len(a) <= 3)
    ]

    if decompress:
        _cmd_decompress(files, keep)
    else:
        _cmd_compress(files, keep, level)
