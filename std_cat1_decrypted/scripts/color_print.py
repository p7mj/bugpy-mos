class Colors:
    PURPLE = '\033[95m'
    DARKBLUE = '\033[94m'
    DARKGREEN = '\033[96m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    DARKRED = '\033[91m'
    RESET = '\033[0m'
    EMPHASIS = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # --- New Colors Added Below ---
    # Standard 16-color / High-intensity ANSI
    CYAN = '\033[36m'
    BRIGHT_CYAN = '\033[96m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    DARK_GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'
    
    # 256-color Extended ANSI (Perfect for xterm/TTY styling)
    AQUA = '\033[38;5;50m'
    AQUA_GREEN = '\033[38;5;42m'
    MINT = '\033[38;5;85m'
    SEAFOAM = '\033[38;5;121m'
    DEEP_SKY = '\033[38;5;27m'
    ELECTRIC_BLUE = '\033[38;5;39m'
    HOT_PINK = '\033[38;5;198m'
    MAGENTA = '\033[38;5;201m'
    GOLD = '\033[38;5;214m'
    LIME = '\033[38;5;118m'
    BRIGHT_REDFU = '\033[38;5;196m'


def cprint(text, color, sameline=None):
    color = color.upper()
    newline = "\n"
    if sameline:
        newline = ""
    if color == "PURPLE":
        print(f"{Colors.PURPLE}{text}{Colors.RESET}", end = newline)
    elif color == "DARKGREEN":
        print(f"{Colors.DARKGREEN}{text}{Colors.RESET}", end = newline)
    elif color == "DARKBLUE":
        print(f"{Colors.DARKBLUE}{text}{Colors.RESET}", end = newline)
    elif color == "GREEN":
        print(f"{Colors.GREEN}{text}{Colors.RESET}", end = newline)
    elif color == "ORANGE":
        print(f"{Colors.ORANGE}{text}{Colors.RESET}", end = newline)
    elif color == "DARKRED":
        print(f"{Colors.DARKRED}{text}{Colors.RESET}", end = newline)
    elif color == "EMPHASIS":
        print(f"{Colors.EMPHASIS}{text}{Colors.RESET}", end = newline)
    elif color == "UNDERLINE":
        print(f"{Colors.UNDERLINE}{text}{Colors.RESET}", end = newline)
    elif color == "RESET":
        print(f"{Colors.RESET}{text}", end = newline)
        
    # --- New Color Elif Conditions Added Below ---
    elif color == "CYAN":
        print(f"{Colors.CYAN}{text}{Colors.RESET}", end = newline)
    elif color == "BRIGHT_CYAN":
        print(f"{Colors.BRIGHT_CYAN}{text}{Colors.RESET}", end = newline)
    elif color == "RED":
        print(f"{Colors.RED}{text}{Colors.RESET}", end = newline)
    elif color == "BLUE":
        print(f"{Colors.BLUE}{text}{Colors.RESET}", end = newline)
    elif color == "YELLOW":
        print(f"{Colors.YELLOW}{text}{Colors.RESET}", end = newline)
    elif color == "WHITE":
        print(f"{Colors.WHITE}{text}{Colors.RESET}", end = newline)
    elif color == "BLACK":
        print(f"{Colors.BLACK}{text}{Colors.RESET}", end = newline)
    elif color == "DARK_GRAY":
        print(f"{Colors.DARK_GRAY}{text}{Colors.RESET}", end = newline)
    elif color == "LIGHT_GRAY":
        print(f"{Colors.LIGHT_GRAY}{text}{Colors.RESET}", end = newline)
    elif color == "AQUA":
        print(f"{Colors.AQUA}{text}{Colors.RESET}", end = newline)
    elif color == "AQUA_GREEN":
        print(f"{Colors.AQUA_GREEN}{text}{Colors.RESET}", end = newline)
    elif color == "MINT":
        print(f"{Colors.MINT}{text}{Colors.RESET}", end = newline)
    elif color == "SEAFOAM":
        print(f"{Colors.SEAFOAM}{text}{Colors.RESET}", end = newline)
    elif color == "DEEP_SKY":
        print(f"{Colors.DEEP_SKY}{text}{Colors.RESET}", end = newline)
    elif color == "ELECTRIC_BLUE":
        print(f"{Colors.ELECTRIC_BLUE}{text}{Colors.RESET}", end = newline)
    elif color == "HOT_PINK":
        print(f"{Colors.HOT_PINK}{text}{Colors.RESET}", end = newline)
    elif color == "MAGENTA":
        print(f"{Colors.MAGENTA}{text}{Colors.RESET}", end = newline)
    elif color == "GOLD":
        print(f"{Colors.GOLD}{text}{Colors.RESET}", end = newline)
    elif color == "LIME":
        print(f"{Colors.LIME}{text}{Colors.RESET}", end = newline)
    elif color == "BRIGHT_RED":
        print(f"{Colors.BRIGHT_REDFU}{text}{Colors.RESET}", end = newline)

# print(f"{Colors.OKGREEN}Success:{Colors.ENDC} Build completed.")

# cprint("this is some text", "PURPLE")
