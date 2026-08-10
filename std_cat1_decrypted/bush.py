# BUGS SHELL (BU-SH) 1 - DYNAMIC FISH TERMINAL EDITION (INTEGRATED RUNTIME)
from scripts import *
from scripts import color_print

import os
import sys
import time
from pathlib import Path
import tty
import termios

bugpy_version = "BUGPy-mOS 1"
bugpy_version_codename = "\"Expansion\""
bugs_version = "Release A-4-i"
version_nickname = "\"Graphical Upgrades\""
distro = "Standard"

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "history" / "history.txt"

if_verbose = 0

def verbose(strings):
    if if_verbose == 1:
        print(str(strings))

try:
    with open("config/username.txt", "r") as f:
        username = f.readline().strip()
except:
    username = "BUGGED_USER"

# =========================================================================
# POINTERFILE MEMORY CACHE ARCHITECTURE
# =========================================================================
_pointer_cache = {} # Dict lookup mapping: alias -> target_script

def reload_pointerfile():
    """Populates or refreshes the internal memory cache dictionary from disk."""
    global _pointer_cache
    _pointer_cache = {}
    config_file = BASE_DIR / "config" / "pointerfile.txt"

    if not config_file.exists():
        color_print.cprint("bush: critical error: pointerfile not found", "DARKRED")
        return

    with config_file.open("r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ": " in stripped:
                alias, target = stripped.split(": ", 1)
                _pointer_cache[alias.strip()] = target.strip()

# Initialize cache memory pool on application boot
reload_pointerfile()

def get_config_line(keyword):
    """Parses pointerfile variables strictly out of lightning-fast cache memory."""
    target = _pointer_cache.get(keyword)
    if target:
        return [keyword, target]
    return None 

def get_all_pointerfile_aliases():
    """Retrieves all active validation routes loaded inside memory workspace."""
    aliases = ["cd", "clear", "exit"] # Built-in defaults
    for alias in _pointer_cache.keys():
        if alias not in aliases:
            aliases.append(alias)
    return aliases

def match_command(command, args_list):
    if command in globals():
        cmd_func = globals()[command]
        cmd_func(args_list)
    else:
        color_print.cprint(f"bush: error: '{command}' not found.", "DARKRED")

def cmdrun(keyword, timed=False):
    if not keyword.strip():
        return False
    parsed = keyword.split()
    verbose(parsed)
    get_config_result = get_config_line(parsed[0])
    verbose(get_config_result)
    
    if get_config_result is not None:
        t0 = time.perf_counter() if timed else None
        match_command(get_config_result[1], parsed[1:])
        if timed:
            elapsed = time.perf_counter() - t0
            color_print.cprint(f"  time: {elapsed:.4f}s", "DARKBLUE")
        return True
    return False

def execute_command(inputs):
    """Executes the validated command structure and shifts directory states if needed."""
    parsed = inputs.split()
    if not parsed:
        return
        
    # Check for systemic execution timer flags
    timed = "--time" in parsed
    if timed:
        parsed.remove("--time")
        if not parsed:
            return
        
    if parsed[0] == "cd":
        if len(parsed) > 1:
            try: os.chdir(parsed[1])
            except Exception as e: print(e)
        return
    elif parsed[0] == "clear":
        print("\033[2J\033[H")
        return
    elif parsed[0] == "exit":
        print("Exiting BUSH...")
        sys.exit(0)

    get_config_result = get_config_line(parsed[0])
    if get_config_result is not None:
        t0 = time.perf_counter() if timed else None
        match_command(get_config_result[1], parsed[1:])
        if timed:
            elapsed = time.perf_counter() - t0
            color_print.cprint(f"  time: {elapsed:.4f}s", "DARKBLUE")
    else:
        color_print.cprint("bush: error: command not found.", "DARKRED")

def bugscript(args):
    if not args:
        color_print.cprint("bush: error: no script file provided.", "DARKRED")
        return
        
    file_path = args[0]
    if not os.path.exists(file_path):
        color_print.cprint(f"bush: error: {file_path} not found.", "DARKRED")
        return

    with open(file_path, "r") as f:
        for line in f:
            command = line.strip()
            if command == "" or command.startswith("#"):
                continue
            
            timed = "--time" in command.split()
            cleaned_cmd = command.replace("--time", "").strip()
            
            if not cmdrun(cleaned_cmd, timed=timed):
                color_print.cprint(f"bush: error: {command}", "DARKRED")

# =========================================================================
# FISH-LIKE TERMINAL ENGINE ENGINE (LINUX SPECIFIC)
# =========================================================================

def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            seen = set()
            unique_history = []
            for item in lines:
                if item not in seen:
                    seen.add(item)
                    unique_history.append(item)
            return unique_history
    except:
        return []

def get_char_linux():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                return f"ESC[{ch3}"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def fish_input_loop(prompt_prefix, history_list):
    """Character reader driving real-time highlighting and autocomplete suggestions."""
    current_str = ""
    cursor_pos = 0
    
    # Track the active offset during history traversal
    history_index = None
    saved_search_str = ""
    
    # Pre-fetch system commands directly out of accelerated memory cache pool
    registered_commands = get_all_pointerfile_aliases()
    
    while True:
        suggestion = ""
        
        # 1. GENERATE AUTOCOMPLETE SUGGESTION
        if current_str.strip():
            if " " not in current_str:
                for cmd in registered_commands:
                    if cmd.startswith(current_str) and cmd != current_str:
                        suggestion = cmd[len(current_str):]
                        break
            
            if not suggestion:
                for hist_cmd in reversed(history_list):
                    if hist_cmd.startswith(current_str) and hist_cmd != current_str:
                        suggestion = hist_cmd[len(current_str):]
                        break

        # 2. COMPUTE SYNTAX COLORS (Isolate first word from parameters)
        input_tokens = current_str.split(" ", 1)
        first_word = input_tokens[0] if input_tokens else ""
        arguments_part = f" {input_tokens[1]}" if len(input_tokens) > 1 else ""

        if not first_word:
            syntax_color = "\033[0m" 
        elif first_word in ["cd", "clear", "exit"]:
            syntax_color = "\033[38;5;10m" # Core System Built-in (CRT Green)
        elif first_word in registered_commands:
            syntax_color = "\033[38;5;10m" # Valid registered script (CRT Green)
        else:
            syntax_color = "\033[31m"      # Typo / Unregistered error (Red)

        # 3. RENDER INPUT BLOCK WITH COLOR ISOLATION AND TRAIL SUGGESTION
        sys.stdout.write("\r\033[K" + prompt_prefix)
        sys.stdout.write(f"{syntax_color}{first_word}\033[0m{arguments_part}")
        
        if suggestion:
            sys.stdout.write(f"\033[38;5;244m{suggestion}\033[0m") # Muted Light Gray
            
        # Reposition editing space relative to execution cursor lengths
        move_back = len(current_str) - cursor_pos + len(suggestion)
        if move_back > 0:
            sys.stdout.write(f"\033[{move_back}D")
        sys.stdout.flush()

        # 4. CAPTURE & PROCESS KEYSTROKES
        char = get_char_linux()

        if char in ('\r', '\n'):
            sys.stdout.write("\033[K\n")
            sys.stdout.flush()
            return current_str

        elif char in ('\x7f', '\x08'):
            history_index = None # Reset historical state on edit
            if cursor_pos > 0:
                current_str = current_str[:cursor_pos-1] + current_str[cursor_pos:]
                cursor_pos -= 1

        # Tab Completion Action Handler
        elif char == '\t':
            if suggestion:
                current_str += suggestion
                cursor_pos = len(current_str)
                history_index = None

        # Right arrow navigation accepts prediction
        elif char == 'ESC[C':
            if cursor_pos < len(current_str):
                cursor_pos += 1
            elif suggestion:
                current_str += suggestion
                cursor_pos = len(current_str)
                history_index = None

        # Left arrow navigation
        elif char == 'ESC[D':
            if cursor_pos > 0:
                cursor_pos -= 1

        # Up arrow command history selection (Multi-step backward cycle)
        elif char == 'ESC[A':
            if history_index is None:
                saved_search_str = current_str
                matched_indices = [i for i, h in enumerate(history_list) if h.startswith(saved_search_str)]
                if matched_indices:
                    history_index = len(matched_indices) - 1
            else:
                history_index = max(0, history_index - 1)
                
            if history_index is not None and matched_indices:
                current_str = history_list[matched_indices[history_index]]
                cursor_pos = len(current_str)

        # Down arrow command history selection (Multi-step forward cycle)
        elif char == 'ESC[B':
            if history_index is not None:
                matched_indices = [i for i, h in enumerate(history_list) if h.startswith(saved_search_str)]
                if history_index < len(matched_indices) - 1:
                    history_index += 1
                    current_str = history_list[matched_indices[history_index]]
                else:
                    # Returned to original baseline text entry
                    history_index = None
                    current_str = saved_search_str
                cursor_pos = len(current_str)

        elif len(char) == 1 and char.isprintable():
            current_str = current_str[:cursor_pos] + char + current_str[cursor_pos:]
            cursor_pos += 1
            history_index = None # Break historical index locking when actively typing

def cli():
    print("\033[2J\033[H")
    color_print.cprint(f"{bugpy_version} ", "GREEN", sameline=True); print(f"{bugpy_version_codename}", end=" "); color_print.cprint(f"{bugs_version} {version_nickname} {distro}", "EMPHASIS")
    
    history_list = load_history()

    while True:
        try:
            current_path = os.getcwd()
            print("┌ ", end=""); color_print.cprint(f"{username}@BUGS", "GREEN", sameline=True); color_print.cprint(f" [{current_path}]", "ORANGE")
            prompt_line_prefix = "└─ > "
            
            inputs = fish_input_loop(prompt_line_prefix, history_list)
            
            if inputs.strip() != "":
                execute_command(inputs)

                try:
                    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(HISTORY_FILE, "a") as file:
                        file.write(f"\n{inputs}")
                except Exception:
                    color_print.cprint("bush: error: history logging error", "DARKRED")
                
                if inputs.strip() not in history_list:
                    history_list.append(inputs.strip())

            print("")

        except KeyboardInterrupt:
            color_print.cprint("\n^C\n", "GREEN")
        except Exception as e:
            color_print.cprint(f"bush: error: {e}", "DARKRED")

if __name__ == "__main__":
    cli()
