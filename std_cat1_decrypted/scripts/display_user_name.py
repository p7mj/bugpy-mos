from pathlib import Path

def main(args):
    if "-h" in args or "--help" in args:
        print("""
DISPLAY_USER_NAME
Usage:
  display_user_name [flags]

Flags:
  -h: this help section

Notes:
  This prints the username. To change your username, go to cat1/config/username.txt.
        """)
        return
    
    current_script_dir = Path(__file__).resolve().parent
    
    file_path = current_script_dir.parent / "config" / "username.txt"

    try:
        print(file_path.read_text(encoding="utf-8").strip())
    except FileNotFoundError:
        print(f"Error: Could not find config file at {file_path}")