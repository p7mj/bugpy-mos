def main(args):
    if args == ["-h"] or args == ["--help"]:
        print("""
SAY GREETING
Usage:
  say_greeting [flags]

Flags:
  -h: this help section

Notes:
  Say hi!
        """)
    else:
        print("say_greeting: hi!")
