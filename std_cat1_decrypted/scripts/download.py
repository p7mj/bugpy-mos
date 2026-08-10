# download.py
# Downloads a file from a URL to the current directory (or a given path).
# Uses urllib from stdlib — no pip installs needed.
# Shows a simple progress indicator while downloading.
#
# Examples:
#   download https://example.com/file.txt
#   download https://example.com/pkg.zip mypackage.zip
#   download https://example.com/pkg.zip packages/mypackage.zip

import urllib.request
import os
from pathlib import Path
from . import color_print

def _progress(block_count, block_size, total_size):
    """
    Callback for urlretrieve — prints a simple progress bar.
    Called once per block downloaded. total_size is -1 if unknown.
    """
    downloaded = block_count * block_size
    if total_size > 0:
        pct = min(100, downloaded * 100 // total_size)
        filled = pct // 5  # 20-char bar
        bar = "[" + "#" * filled + "-" * (20 - filled) + "]"
        total_mb = total_size / (1024 * 1024)
        done_mb  = downloaded  / (1024 * 1024)
        print(f"\r  {bar} {pct:>3}%  {done_mb:.1f}/{total_mb:.1f} MB", end="", flush=True)
    else:
        # Unknown total size — just show bytes downloaded
        print(f"\r  downloaded {downloaded} bytes...", end="", flush=True)

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
DOWNLOAD [A-3-iii]
Usage:
  download <params> {files}

Parameters:
  url   The URL to download from

Files:
  Optional output path. Defaults to the filename from the URL.
""")
        return

    url = args[0]

    # Default output filename: the last segment of the URL path
    if len(args) >= 2:
        output = args[1]
    else:
        output = Path(url.split("?")[0]).name  # Strip query string first
        if not output:
            output = "downloaded_file"

    # Create parent directories if they don't exist
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"download: {url}")
    print(f"      to: {out_path}")

    try:
        urllib.request.urlretrieve(url, str(out_path), reporthook=_progress)
        print()  # Newline after progress bar
        size_kb = out_path.stat().st_size / 1024
        color_print.cprint(f"download: done ({size_kb:.1f} KB)", "GREEN")
    except urllib.error.URLError as e:
        print()
        color_print.cprint(f"download: failed — {e.reason}", "DARKRED")
    except Exception as e:
        print()
        color_print.cprint(f"download: error — {e}", "DARKRED")
        # Clean up a partially downloaded file so nothing broken is left on disk
        if out_path.exists():
            out_path.unlink()
