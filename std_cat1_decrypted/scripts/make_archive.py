import zipfile
from pathlib import Path

if_verbose = 0

def verbose(args):
    if if_verbose == 1:
        print(args)

def main(args):
    if len(args) < 2 or "-h" in args or "--help" in args:
        print("""
MAKE ARCHIVE
Usage:
  make_archive {output} ({files} ... {files}) [flags]

Files:
  output: the output zip file name
  files: the files to be zipped. Can be folders. Can be one or more.

Flags:
  -h: this help section

Note:
  A program to zip files... and to make pcs work.
        """)
        return
    output_zip = args[0]
    items = args[1:]
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in items:
                path = Path(item)
                if not path.exists():
                    print(f"zip: '{item}' not found, skipping.")
                    continue
                if path.is_file():
                    verbose(f"zip: adding file {path}")
                    zf.write(path, path.name)
                elif path.is_dir():
                    for file in path.rglob("*"):
                        if file.is_file():
                            verbose(f"zip: adding {file}")
                            zf.write(file, file.relative_to(path.parent))
                else:
                    print(f"zip: '{item}' is not a file or folder, skipping.")
    except Exception as e:
        print(f"zip: error! {e}")