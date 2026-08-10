from pathlib import Path
from . import color_print

def main(args):
    # Handle help menu strictly adhering to the requested format
    if "--help" in args or "-h" in args or not args:
        print("""
REPEAT COMMAND
Usage:
  repeat <times> <command_string>

Parameters:
  times           The number of times to loop and run the specified command. Must be an integer.
  command_string  The exact terminal instruction string you want the shell to execute recursively.

Flags:
  -h: this help section

Notes:
  Intended to repeat the retardedness command so that you can add or remove more values from P7MJ's retardeness value with ease.
  Unintended side effect: Can run other commands as well.
""")
        return

    # 1. Parse the loop count parameter
    try:
        times = int(args[0])
    except ValueError:
        color_print.cprint("repeat_command: error: First parameter must be an integer.", "DARKRED")
        return

    # 2. Reconstruct the complete command string from the remaining arguments
    command_to_run = " ".join(args[1:])
    if not command_to_run:
        color_print.cprint("repeat_command: error: No command string specified to repeat.", "DARKRED")
        return

    # 3. Dynamic import of cmdrun from the main shell to execute commands safely
    try:
        import sys
        root_dir = str(Path(__file__).resolve().parent.parent)
        if root_dir not in sys.path:
            sys.path.append(root_dir)
            
        from bush import cmdrun
        
    except ImportError as e:
        color_print.cprint(f"repeat_command: error: could not import cmdrun from BUSH. {e}", "DARKRED")
        return

    # 4. Loop execution core
    for i in range(times):
        success = cmdrun(command_to_run)
        if not success:
            color_print.cprint(f"repeat_command: aborting loop: '{command_to_run}' failed during cycle {i+1}.", "DARKRED")
            break