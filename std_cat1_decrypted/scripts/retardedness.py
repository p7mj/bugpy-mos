from pathlib import Path
from . import color_print

def main(args):
    # Setup paths relative to script location (up 1 to scripts folder, then up 1 to root, then config)
    base_dir = Path(__file__).resolve().parent.parent
    config_file = base_dir / "config" / "p7mj_retardedness.txt"

    if "--help" in args or "-h" in args or not args:
        print("""
RETARDEDNESS
Usage:
  retardedness (direction) [flags]

Choices:
  +: Increments retardedness by 1.
  -: Decrements retardedness by 1.

Flags:
  -h: this help section

Notes:
  To change P7MJ's retardedness value as displayed in p7mj_bio
""")
        return

    # Ensure the config file exists with a default value of 100
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text("100", encoding="utf-8")

    try:
        current_value = int(config_file.read_text(encoding="utf-8").strip())
    except ValueError:
        current_value = 100

    direction = args[0]

    if direction == "+":
        current_value += 1
    elif direction == "-":
        current_value -= 1
    else:
        color_print.cprint("retardedness: error: invalid choice. Choose '+' or '-'.", "DARKRED")
        return

    # Save the updated value back to the file
    config_file.write_text(str(current_value), encoding="utf-8")
    print(f"retardedness: P7MJ's retardedness updated to: {current_value}%")