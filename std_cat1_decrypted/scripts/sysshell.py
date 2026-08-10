import os
import subprocess

def main(args):
	if not args or args in (["-h"], ["--help"]):
		print("""
SYSSHELL
Usage:
	sysshell [flags]

Flags:
	-h: this help section

Notes:
	For that one guy who wants to escape the BUGPy matrix and be a faithful Linux user
""")
		return

	# Use user's default shell or fallback to bash.
	# What if they don't have bash? Well user problem isn't it?
	user_shell = os.environ.get("SHELL", "/bin/bash")

	subprocess.run([user_shell])
