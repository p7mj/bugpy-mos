import os
def main(args):
    if "-h" in args or "--help" in args:
        print("""
CURRENT WORKING DIRECTORY
Usage:
  current_working_directory [flags]

Flags:
  -h: this help section

Note:
  Displays where you are at in the filesystem
        """)
    else:
        print(os.getcwd())