from pathlib import Path

def main(args):
    if args == []:
        print("touch_file: no arguments were given")
    elif args == ["-h"] or args == ["--help"]:
        print("""
TOUCH FILE
Usage:
  touch_file {files} [flags]

Files:
  Files you want to update timestamps to / create

Flags:
  -h: this help section

Notes:
  This is not a sus command.
  This command is used to update file timestamps or create new files.
        """)
    else:
        for target in args:
            path = Path(target)
            path.touch(exist_ok=True)