import zipfile
from pathlib import Path

if_verbose = 0

def verbose(args):
    if if_verbose == 1:
        print(args)

def main(args):
    if not args or "-h" in args or "--help" in args:
        print("""
UNMAKE ARCHIVE
Usage:
  unmake_archive {file} <dest> [flags]

Parameters:
  dest: the name of the new folder to extract to

Files:
  file: the zip file to extract

Flags:
  -h: This help section

Notes:
  To unmake archives you made
        """)
        return
    archive = args[0]
    output = args[1] if len(args) >= 2 else "."
    if not Path(archive).is_file():
        print(f"unzip: '{archive}' not found.")
        return
    try:
        with zipfile.ZipFile(archive, 'r') as zf:
            verbose(f"unzip: extracting {archive} to {output}")
            zf.extractall(output)
    except Exception as e:
        print(f"unzip: error! {e}")