# var.py
# Two-tier variable/environment system for BUGPy-mOS:
#
#   SESSION variables  — in-memory only, gone when the shell exits.
#                        Fast scratch storage for scripts and manual use.
#
#   ENV variables      — persisted to config/env.txt inside the encrypted
#                        drive. Survive across sessions. Think of them as
#                        permanent shell environment variables.
#
# Commands:
#   var set <key> <value>      — set a session variable
#   var get <key>              — get a session variable
#   var list                   — list all session variables
#   var del <key>              — delete a session variable
#   var clear                  — clear all session variables
#
#   var env set <key> <value>  — set a persistent env variable
#   var env get <key>          — get a persistent env variable
#   var env list               — list all persistent env variables
#   var env del <key>          — delete a persistent env variable
#   var env clear              — clear all persistent env variables
#
# ENV file format (config/env.txt) — one KEY=VALUE per line.
# Lines starting with # are comments and are preserved on write.
#
# Example uses:
#   var set scratch_dir /home/me/tmp
#   var get scratch_dir
#   var env set editor pyvi
#   var env get editor

from pathlib import Path
from . import color_print

# In-memory session store — module-level dict persists for the whole session
_session = {}

# Persistent env file path
_ENV_FILE = Path(__file__).resolve().parent.parent / "config" / "env.txt"


# --- Persistent ENV helpers ---

def _env_load():
    """
    Load all KEY=VALUE pairs from env.txt.
    Returns a dict. Comment lines and blanks are ignored for lookup
    but stored separately so we can preserve them on save.
    """
    pairs = {}
    if not _ENV_FILE.exists():
        return pairs
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            pairs[key.strip()] = value.strip()
    return pairs

def _env_save(pairs):
    """
    Write KEY=VALUE pairs back to env.txt.
    Preserves any comment lines that were already in the file.
    """
    # Keep comment/blank lines from the existing file
    comments = []
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "":
                comments.append(line)

    lines = comments + [f"{k}={v}" for k, v in sorted(pairs.items())]
    _ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    _ENV_FILE.write_text("\n".join(lines) + "\n")


# --- Subcommand handlers ---

def _cmd_session(args):
    """Handle 'var set/get/list/del/clear' (session scope)."""
    if not args:
        color_print.cprint("var: expected set/get/list/del/clear", "DARKRED")
        return

    sub = args[0]

    if sub == "set":
        if len(args) < 3:
            color_print.cprint("var set: usage: var set <key> <value>", "DARKRED")
            return
        key   = args[1]
        value = " ".join(args[2:])
        _session[key] = value
        print(f"var: {key} = {value}")

    elif sub == "get":
        if len(args) < 2:
            color_print.cprint("var get: usage: var get <key>", "DARKRED")
            return
        key = args[1]
        if key in _session:
            print(f"{key} = {_session[key]}")
        else:
            color_print.cprint(f"var: '{key}' not set", "ORANGE")

    elif sub == "list":
        if not _session:
            print("var: no session variables set")
            return
        color_print.cprint("Session variables:", "EMPHASIS")
        for k, v in sorted(_session.items()):
            print(f"  {k} = {v}")

    elif sub == "del":
        if len(args) < 2:
            color_print.cprint("var del: usage: var del <key>", "DARKRED")
            return
        key = args[1]
        if key in _session:
            del _session[key]
            print(f"var: deleted '{key}'")
        else:
            color_print.cprint(f"var: '{key}' not found", "ORANGE")

    elif sub == "clear":
        confirm = input("var: clear all session variables? (y/N) ").strip().lower()
        if confirm == "y":
            _session.clear()
            print("var: session cleared")
        else:
            print("var: cancelled")

    else:
        color_print.cprint(f"var: unknown subcommand '{sub}'", "DARKRED")


def _cmd_env(args):
    """Handle 'var env set/get/list/del/clear' (persistent scope)."""
    if not args:
        color_print.cprint("var env: expected set/get/list/del/clear", "DARKRED")
        return

    sub = args[0]
    pairs = _env_load()

    if sub == "set":
        if len(args) < 3:
            color_print.cprint("var env set: usage: var env set <key> <value>", "DARKRED")
            return
        key   = args[1]
        value = " ".join(args[2:])
        pairs[key] = value
        _env_save(pairs)
        color_print.cprint(f"env: {key} = {value}  (saved)", "GREEN")

    elif sub == "get":
        if len(args) < 2:
            color_print.cprint("var env get: usage: var env get <key>", "DARKRED")
            return
        key = args[1]
        if key in pairs:
            print(f"{key} = {pairs[key]}")
        else:
            color_print.cprint(f"env: '{key}' not set", "ORANGE")

    elif sub == "list":
        if not pairs:
            print("env: no persistent variables set")
            return
        color_print.cprint("Persistent env variables:", "EMPHASIS")
        for k, v in sorted(pairs.items()):
            print(f"  {k} = {v}")

    elif sub == "del":
        if len(args) < 2:
            color_print.cprint("var env del: usage: var env del <key>", "DARKRED")
            return
        key = args[1]
        if key in pairs:
            del pairs[key]
            _env_save(pairs)
            print(f"env: deleted '{key}'")
        else:
            color_print.cprint(f"env: '{key}' not found", "ORANGE")

    elif sub == "clear":
        confirm = input("var env: clear all persistent env variables? (y/N) ").strip().lower()
        if confirm == "y":
            _env_save({})
            print("env: cleared")
        else:
            print("env: cancelled")

    else:
        color_print.cprint(f"var env: unknown subcommand '{sub}'", "DARKRED")


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""VAR [A-3-iii]
Usage:
  var <params>

Parameters:
  set <key> <value>        Set a session variable
  get <key>                Get a session variable
  list                     List all session variables
  del <key>                Delete a session variable
  clear                    Clear all session variables
  env set <key> <value>    Set a persistent variable (saved to config/env.txt)
  env get <key>            Get a persistent variable
  env list                 List all persistent variables
  env del <key>            Delete a persistent variable
  env clear                Clear all persistent variables""")
        return

    # Route to env subcommands or session subcommands
    if args[0] == "env":
        _cmd_env(args[1:])
    else:
        _cmd_session(args)
