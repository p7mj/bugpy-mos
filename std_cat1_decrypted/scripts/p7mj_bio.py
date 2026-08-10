from pathlib import Path

def main(args):
    if "--help" in args or "-h" in args:
        print("""
P7MJ_BIO
Usage:
  p7mj_bio [flags]

Flags:
  -h: this help section

Notes:
  This is P7MJ's autobiography
""")
        return
    
    # 1. Resolve path relative to the script location 
    # (__file__ is in cat1/scripts/, .parent is cat1/, then into config/)
    base_dir = Path(__file__).resolve().parent.parent
    config_file = base_dir / "config" / "p7mj_retardedness.txt"

    # 2. Safely read the value, falling back to 100 if the file isn't found or is corrupt
    try:
        retardedness_val = config_file.read_text(encoding="utf-8").strip()
        # Double check it's actually an integer string
        retardedness_val = f"{int(retardedness_val)}%"
    except (FileNotFoundError, ValueError):
        retardedness_val = "100% (There's something wrong with the file)"
    
    print("P7MJ is the creator and one of the active developers of BUGPy.")
    print("He made all versions from BUGPy-mOS-0 to BUGPy-mOS-1 A-3-ii.")
    print("Currently, he feels retarded. There's not much we or he can do about that.")
    print(f"His retardedness is currently at: {retardedness_val}")