# tar.py
# Create and extract tar archives with optional compression.
# Supports .tar, .tar.gz (.tgz), and .tar.bz2 formats.
# Pure stdlib tarfile module — no external tools needed.
# Works on Windows and Linux.
#
# On Linux, .tar.gz is the standard archive format for most projects,
# packages, and source distributions. This complements the existing
# zip/unzip commands which are more common on Windows.

import tarfile
import os
from pathlib import Path
from . import color_print

# Map file extensions to tarfile open modes
_MODES = {
    ".tar":     ("", ""),
    ".tgz":     (":gz", ":gz"),
    ".tar.gz":  (":gz", ":gz"),
    ".tar.bz2": (":bz2", ":bz2"),
    ".tbz2":    (":bz2", ":bz2"),
}


def _detect_mode(filename):
    """
    Return the tarfile write/read mode suffix for a given filename.
    e.g. 'archive.tar.gz' -> ':gz'
    Returns '' for plain .tar, None if unrecognised.
    """
    name = filename.lower()
    for ext, (write_suffix, read_suffix) in _MODES.items():
        if name.endswith(ext):
            return write_suffix
    return None


def _human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _cmd_create(archive_path, sources, verbose):
    """
    Create a tar archive containing one or more files/folders.
    source paths are added preserving their names (not full paths).
    """
    mode_suffix = _detect_mode(archive_path)
    if mode_suffix is None:
        color_print.cprint(
            f"tar: unrecognised format for '{archive_path}'.\n"
            f"     Use .tar, .tar.gz, .tgz, .tar.bz2, or .tbz2",
            "DARKRED"
        )
        return

    mode = "w" + mode_suffix

    # Check all sources exist before starting
    missing = [s for s in sources if not Path(s).exists()]
    if missing:
        for m in missing:
            color_print.cprint(f"tar: '{m}' not found.", "DARKRED")
        return

    try:
        with tarfile.open(archive_path, mode) as tf:
            for source in sources:
                p = Path(source)
                if verbose:
                    if p.is_dir():
                        # Count files in dir for feedback
                        count = sum(1 for _ in p.rglob("*") if _.is_file())
                        color_print.cprint(
                            f"  adding  {p.name}/  ({count} files)",
                            "DARKBLUE"
                        )
                    else:
                        size = _human_size(p.stat().st_size)
                        color_print.cprint(
                            f"  adding  {p.name}  ({size})",
                            "DARKBLUE"
                        )
                # arcname=p.name keeps just the basename in the archive
                tf.add(str(p), arcname=p.name)

        archive_size = _human_size(Path(archive_path).stat().st_size)
        color_print.cprint(
            f"tar: created '{archive_path}'  ({archive_size})",
            "GREEN"
        )

    except PermissionError:
        color_print.cprint(
            f"tar: permission denied writing '{archive_path}'", "DARKRED"
        )
    except Exception as e:
        color_print.cprint(f"tar: create failed — {e}", "DARKRED")


def _cmd_extract(archive_path, dest, verbose):
    """Extract a tar archive to a destination directory."""
    if not Path(archive_path).exists():
        color_print.cprint(f"tar: '{archive_path}' not found.", "DARKRED")
        return

    # Auto-detect format from file header (more reliable than extension)
    try:
        if not tarfile.is_tarfile(archive_path):
            color_print.cprint(
                f"tar: '{archive_path}' is not a valid tar archive.", "DARKRED"
            )
            return
    except Exception:
        pass

    dest_path = Path(dest) if dest else Path(".")
    dest_path.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(archive_path, "r:*") as tf:
            members = tf.getmembers()

            if verbose:
                for m in members:
                    size = _human_size(m.size)
                    color_print.cprint(
                        f"  extracting  {m.name}  ({size})",
                        "DARKBLUE"
                    )

            # Security: skip members with absolute paths or path traversal
            safe_members = []
            skipped      = 0
            for m in members:
                # Reject absolute paths and .. traversal
                if m.name.startswith('/') or '..' in m.name:
                    skipped += 1
                    continue
                safe_members.append(m)

            tf.extractall(path=str(dest_path), members=safe_members)

        total_size = sum(m.size for m in safe_members)
        msg = f"tar: extracted {len(safe_members)} item(s) to '{dest_path}'"
        msg += f"  ({_human_size(total_size)})"
        if skipped:
            msg += f"  [{skipped} unsafe path(s) skipped]"
        color_print.cprint(msg, "GREEN")

    except tarfile.TarError as e:
        color_print.cprint(f"tar: extract failed — {e}", "DARKRED")
    except PermissionError:
        color_print.cprint(
            f"tar: permission denied writing to '{dest_path}'", "DARKRED"
        )
    except Exception as e:
        color_print.cprint(f"tar: extract failed — {e}", "DARKRED")


def _cmd_list(archive_path):
    """List contents of a tar archive without extracting."""
    if not Path(archive_path).exists():
        color_print.cprint(f"tar: '{archive_path}' not found.", "DARKRED")
        return

    try:
        with tarfile.open(archive_path, "r:*") as tf:
            members = tf.getmembers()

        color_print.cprint(f"Contents of '{archive_path}':", "EMPHASIS")
        color_print.cprint(
            f"  {'SIZE':>10}  {'TYPE':<6}  NAME",
            "DARKBLUE"
        )
        color_print.cprint("  " + "─" * 50, "DARKBLUE")

        total_size  = 0
        file_count  = 0
        dir_count   = 0

        for m in members:
            if m.isdir():
                kind = "dir"
                dir_count += 1
                size_str = ""
            elif m.issym():
                kind     = "link"
                size_str = ""
            else:
                kind      = "file"
                file_count += 1
                total_size += m.size
                size_str   = _human_size(m.size)

            print(f"  {size_str:>10}  {kind:<6}  {m.name}")

        print()
        print(
            f"  {file_count} file(s),  {dir_count} folder(s)  —  "
            f"{_human_size(total_size)} uncompressed"
        )

    except tarfile.TarError as e:
        color_print.cprint(f"tar: list failed — {e}", "DARKRED")
    except Exception as e:
        color_print.cprint(f"tar: list failed — {e}", "DARKRED")


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""\
TAR [A-3-iii]
Usage:
  tar <params> {files} ({files} ... {files}) [flags]

Parameters:
  create    Create a new archive
  extract   Extract an archive
  list      List archive contents without extracting

Files:
  create:   archive_name  file_or_folder  [more files...]
  extract:  archive_name  [destination_folder]
  list:     archive_name

Flags:
  -v   Verbose — show each file as it is added or extracted

Choices:
  Formats: .tar  .tar.gz  .tgz  .tar.bz2  .tbz2""")
        return

    cmd  = args[0].lower()
    rest = args[1:]

    # Parse -v flag
    verbose = "-v" in rest
    rest    = [a for a in rest if a != "-v"]

    if cmd == "create":
        if len(rest) < 2:
            color_print.cprint(
                "tar create: expected an archive name and at least one source.",
                "DARKRED"
            )
            return
        _cmd_create(rest[0], rest[1:], verbose)

    elif cmd == "extract":
        if not rest:
            color_print.cprint(
                "tar extract: expected an archive name.", "DARKRED"
            )
            return
        archive = rest[0]
        dest    = rest[1] if len(rest) > 1 else "."
        _cmd_extract(archive, dest, verbose)

    elif cmd == "list":
        if not rest:
            color_print.cprint(
                "tar list: expected an archive name.", "DARKRED"
            )
            return
        _cmd_list(rest[0])

    else:
        color_print.cprint(
            f"tar: unknown command '{cmd}'. Use create, extract, or list.",
            "DARKRED"
        )
