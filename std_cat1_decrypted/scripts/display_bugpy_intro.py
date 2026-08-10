def main(args):
    if "--help" in args or "-h" in args:
        print("""
DISPLAY_BUGPY_INTRO
Usage:
  display_bugpy_intro [flags]

Flags:
  -h: this help section

Notes:
  This is a script that prints the introduction of BUGPy, in an unhelpful way.
""")
        return
        
    print("BUGPy-mOS is a... huge, huge insect-shaped OS-like Python program.")
    print("Don't ask me why, type whyami for more.")