from pathlib import Path
import shutil

def main(args):
    if not args:
        print("remove: no arguments were given")
        return
    
    # Check for the -rf flag
    recursive = False
    if "-rf" in args:
        recursive = True
        args.remove("-rf") # Remove flag from list so only paths remain

    if args == ["-h"] or args == ["--help"]:
        print("""
REMOVE
Usage:
  remove ({files} ... {files}) [flags]

Files:
  files: files you want to delete. Can be one or multiple.

Flags:
  -h: this help section

Notes:
  It's time to take out the trash!
        """)
    else:
        for item in args:
            path = Path(item)
            
            if not path.exists():
                continue # 'force' usually means ignore non-existent files

            try:
                if path.is_dir():
                    if recursive:
                        shutil.rmtree(path) # This is the "recursive" part
                    else:
                        print(f"remove: cannot remove '{item}': Is a directory")
                else:
                    path.unlink() # Delete individual file
            except Exception as e:
                print(f"remove: error deleting {item}: {e}")