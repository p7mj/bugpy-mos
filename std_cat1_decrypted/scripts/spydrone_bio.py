def main(args):
    if "--help" in args or "-h" in args:
        print("""
SPYDRONE_BIO
Usage:
  spydrone_bio [flags]

Flags:
  -h: this help section

Notes:
  SpyDrone's bio
  """)
        return
        
    print(r"SpyDrone is a... spy drone. He contributed to 99.67% of changes in A-3-iii \"Drones Fly Overhead\".")
    print("He also made pyvi and 1/3 of the system utilities.")