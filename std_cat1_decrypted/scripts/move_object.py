import shutil
from pathlib import Path

def main(args):
    """
    Command to move or rename files or directories.
    """
    if "--help" in args or "-h" in args:
        print("""
MOVE OBJECT
Usage:
  move_object {init} {whereto} [flags]

Files:
  init: original file or folder;
  whereto: the file or folder to move to.

Flags:
  -h: this help section

Note:
  For you to, again, organize.
        """)
        return

    if len(args) != 2:
        print("mv: Error. Expected exactly 2 arguments (source and destination).")
        return

    source = Path(args[0])
    destination = Path(args[1])

    if not source.exists():
        print(f"mv: Error! Source '{source}' does not exist.")
        return

    try:
        shutil.move(str(source), str(destination))
        print(f"mv: Successfully moved '{source.name}' to '{destination}'")
    except Exception as e:
        print(f"mv: Failed to move. Error: {e}")