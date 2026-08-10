import shutil
from pathlib import Path

def main(args):
    """
    Command to copy files or directories.
    """
    if "--help" in args or "-h" in args:
        print("""
COPY OBJECT
Usage:
  copy_object {init} {dest} [flags]

Files:
  init: what file to copy
  dest: destination file name (will create if not exist)

Flags:
  -h: this help section

Note:
  copies a file
        """)
        return

    if len(args) != 2:
        print("cp: Error. Expected exactly 2 arguments (source and destination).")
        return

    source = Path(args[0])
    destination = Path(args[1])

    if not source.exists():
        print(f"cp: Error! Source '{source}' does not exist.")
        return

    try:
        if source.is_dir():
            # Copy whole directory tree
            shutil.copytree(source, destination)
            print(f"cp: Successfully copied folder '{source.name}' to '{destination}'")
        else:
            # Copy single file
            shutil.copy2(source, destination)
            print(f"cp: Successfully copied file '{source.name}' to '{destination}'")
    except Exception as e:
        print(f"cp: Failed to copy. Error: {e}")