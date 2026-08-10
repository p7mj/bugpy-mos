# startup.py
# Manage a list of .bugscript files that run automatically when BUGPy boots.
# Entries stored in config/startup.txt, one path per line.
# bugpy-mos-1.py reads this on launch and runs each entry via bugscript().

import os
from pathlib import Path
from . import color_print

_STARTUP_FILE = Path(__file__).resolve().parent.parent / "config" / "startup.txt"


def _load():
    if not _STARTUP_FILE.exists():
        return []
    return [
        line.strip()
        for line in _STARTUP_FILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _save(entries):
    _STARTUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    _STARTUP_FILE.write_text("\n".join(entries) + ("\n" if entries else ""))


def run_all(bugscript_fn):
    """Called by bugpy-mos-1.py on boot. Runs each registered script in order."""
    entries = _load()
    if not entries:
        return
    for path in entries:
        if os.path.exists(path):
            print(f"startup: running {path}")
            bugscript_fn([path])
        else:
            color_print.cprint(f"startup: skipping missing script '{path}'", "ORANGE")


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
STARTUP
Usage:
  startup <params> {files} [flags]

Parameters:
  list              Show all registered startup scripts
  add               Add a script to run on boot
  remove            Remove a startup entry by number
  run               Manually run all startup scripts right now
  clear             Remove all startup entries

Files:
  files: path to the .bugscript file to register

Flags:
  -h: this help section

Notes:
  Like Startup Apps but scripts
""")
        return

    cmd = args[0]
    entries = _load()

    if cmd == "list":
        if not entries:
            print("startup: no startup scripts registered")
            return
        color_print.cprint("Startup scripts:", "EMPHASIS")
        for i, path in enumerate(entries, 1):
            exists = "ok" if os.path.exists(path) else "missing"
            color_print.cprint(f"  {i:>3}  ", "DARKBLUE", sameline=True)
            print(f"{path}  [{exists}]")

    elif cmd == "add":
        if len(args) < 2:
            color_print.cprint("startup: add requires a script path.", "DARKRED")
            return
        path = args[1]
        if path in entries:
            color_print.cprint(f"startup: '{path}' is already registered.", "ORANGE")
            return
        if not os.path.exists(path):
            color_print.cprint(
                f"startup: warning — '{path}' does not exist yet.", "ORANGE"
            )
        entries.append(path)
        _save(entries)
        color_print.cprint(f"startup: added '{path}'", "GREEN")

    elif cmd == "remove":
        if len(args) < 2 or not args[1].isdigit():
            color_print.cprint("startup remove: expected a number.", "DARKRED")
            return
        n = int(args[1]) - 1
        if n < 0 or n >= len(entries):
            color_print.cprint(f"startup: no entry {args[1]}.", "DARKRED")
            return
        removed = entries.pop(n)
        _save(entries)
        print(f"startup: removed '{removed}'")

    elif cmd == "run":
        if not entries:
            print("startup: nothing to run")
            return
        import importlib.util
        bush_path = Path(__file__).resolve().parent.parent / "bush.py"
        spec = importlib.util.spec_from_file_location("bush", bush_path)
        bush = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bush)
        run_all(bush.bugscript)

    elif cmd == "clear":
        if not entries:
            print("startup: nothing to clear")
            return
        confirm = input("startup: remove all startup scripts? (y/N) ").strip().lower()
        if confirm == "y":
            _save([])
            print("startup: cleared")
        else:
            print("startup: cancelled")

    else:
        color_print.cprint(f"startup: unknown command '{cmd}'", "DARKRED")