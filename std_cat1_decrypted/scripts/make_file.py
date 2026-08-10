from pathlib import Path

def main(args):
    if args == []:
        print("make_file: no arguments were given.")
    elif args == ["-h"] or args == ["--help"]:
        print("""
MAKE FILE
Usage:
  make_file (<file> ... <file>) [flags]

Parameters:
  file: filenames to create. Can take one or multiple.

Flags:
  -h: this help section

Notes:
  To make files
        """)
    else:
        for target in args:
            path = Path(target)
            if path.exists():
                print(f'make_file: "{target}" already exists.')
                continue
            path.write_text("")