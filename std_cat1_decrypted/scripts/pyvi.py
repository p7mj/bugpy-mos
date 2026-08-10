import curses
import sys
import os
import re
from pathlib import Path

# Set ESC delay before importing/init curses to ensure it's picked up quickly
os.environ.setdefault('ESCDELAY', '25')

# =========================================================================
# STANDALONE MODULAR ACTIONS (No hardcoding!)
# =========================================================================

def move_left(editor, count=1):
    editor.col -= count

def move_right(editor, count=1):
    editor.col += count

def move_down(editor, count=1):
    editor.row += count

def move_up(editor, count=1):
    editor.row -= count

def jump_to_start(editor, count=1):
    editor.col = 0

def jump_to_end(editor, count=1):
    editor.col = len(editor.lines[editor.row])

def enter_insert_mode(editor, count=1):
    editor.mode = "INSERT"

def enter_insert_append(editor, count=1):
    editor.mode = "INSERT"
    editor.col += 1

def enter_visual_mode(editor, count=1):
    editor.mode = "VISUAL"
    editor.visual_start = (editor.row, editor.col)

def enter_command_mode(editor, count=1):
    editor.mode = "COMMAND"
    editor.command_buffer = ""

def delete_char_at_cursor(editor, count=1):
    editor.dirty = True
    for _ in range(count):
        if editor.col < len(editor.lines[editor.row]):
            line = editor.lines[editor.row]
            editor.lines[editor.row] = line[:editor.col] + line[editor.col+1:]

def yank_visual_selection(editor, count=1):
    if editor.mode == "VISUAL" and editor.visual_start:
        v_r, v_c = editor.visual_start
        (r1, c1), (r2, c2) = sorted([(v_r, v_c), (editor.row, editor.col)])
        if r1 == r2: 
            editor.clipboard = [editor.lines[r1][c1:c2+1]]
        else:
            editor.clipboard = [editor.lines[r1][c1:]] + editor.lines[r1+1:r2] + [editor.lines[r2][:c2+1]]
        editor.status_message = f"{len(editor.clipboard)} elements yanked"
        editor.mode = "NORMAL"

def paste_clipboard(editor, count=1):
    if editor.clipboard:
        editor.dirty = True
        if len(editor.clipboard) == 1:
            line = editor.lines[editor.row]
            editor.lines[editor.row] = line[:editor.col+1] + editor.clipboard[0] + line[editor.col+1:]
        else:
            rem = editor.lines[editor.row][editor.col+1:]
            editor.lines[editor.row] = editor.lines[editor.row][:editor.col+1] + editor.clipboard[0]
            for idx, clip_line in enumerate(editor.clipboard[1:]):
                editor.lines.insert(editor.row + 1 + idx, clip_line)
            editor.lines[editor.row + len(editor.clipboard) - 1] += rem


# =========================================================================
# REGISTRY MAPPINGS (Traffic Directors)
# =========================================================================

NORMAL_KEYMAP = {
    'h': move_left,
    'l': move_right,
    'j': move_down,
    'k': move_up,
    '0': jump_to_start,
    '$': jump_to_end,
    'i': enter_insert_mode,
    'a': enter_insert_append,
    'v': enter_visual_mode,
    ':': enter_command_mode,
    'x': delete_char_at_cursor,
    'p': paste_clipboard,
    'y': yank_visual_selection,
    # Arrow key bindings mapped seamlessly
    str(curses.KEY_LEFT): move_left,
    str(curses.KEY_RIGHT): move_right,
    str(curses.KEY_DOWN): move_down,
    str(curses.KEY_UP): move_up,
}


# =========================================================================
# CORE EDITOR INTERFACE ENGINE
# =========================================================================

class PyVi:
    def __init__(self, stdscr, filename):
        self.stdscr = stdscr
        self.filename = filename
        self.lines = self._load_file()

        self.mode = "NORMAL"
        self.row = 0
        self.col = 0
        self.top_row = 0
        self.left_col = 0
        self.command_buffer = ""
        self.status_message = ""
        self.multiplier = ""
        self.visual_start = None
        self.clipboard = []
        self.dirty = False

        self._init_curses()

    def _init_curses(self):
        curses.use_default_colors()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        self.stdscr.keypad(True)
        curses.raw()
        curses.noecho()
        self.update_cursor_shape()

    def _load_file(self):
        try:
            p = Path(self.filename)
            if p.exists():
                content = p.read_text().splitlines()
                return content if content else [""]
            return [""]
        except Exception as e:
            return [f"Error loading file: {e}"]

    def update_cursor_shape(self):
        try:
            sys.stdout.write("\x1b[5 q" if self.mode == "INSERT" else "\x1b[2 q")
            sys.stdout.flush()
        except: pass

    def is_selected(self, r, c):
        if self.mode != "VISUAL" or not self.visual_start:
            return False
        v_r, v_c = self.visual_start
        (r1, c1), (r2, c2) = sorted([(v_r, v_c), (self.row, self.col)])
        if r < r1 or r > r2: return False
        if r1 == r2: return c1 <= c <= c2
        if r == r1: return c >= c1
        if r == r2: return c <= c2
        return True

    def clamp_cursor(self):
        self.row = max(0, min(self.row, len(self.lines) - 1))
        l_len = len(self.lines[self.row])
        if self.mode == "INSERT":
            self.col = max(0, min(self.col, l_len))
        else:
            self.col = max(0, min(self.col, l_len - 1 if l_len > 0 else 0))

    def scroll_view(self):
        h, w = self.stdscr.getmaxyx()
        if self.row < self.top_row:
            self.top_row = self.row
        elif self.row >= self.top_row + h - 2:
            self.top_row = self.row - (h - 3)

        if self.col < self.left_col:
            self.left_col = self.col
        elif self.col >= self.left_col + w - 1:
            self.left_col = self.col - (w - 2)

    def render(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.erase()
        self.scroll_view()

        for i in range(h - 2):
            idx = self.top_row + i
            if idx < len(self.lines):
                line = self.lines[idx][self.left_col : self.left_col + w]
                for char_idx, char in enumerate(line):
                    real_col = self.left_col + char_idx
                    attr = curses.color_pair(1) if self.is_selected(idx, real_col) else curses.A_NORMAL
                    try: self.stdscr.addch(i, char_idx, char, attr)
                    except curses.error: pass
            else:
                try: self.stdscr.addstr(i, 0, "~", curses.A_DIM)
                except curses.error: pass

        mult_text = f" {self.multiplier}" if self.multiplier else ""
        dirty_flag = "[+]" if self.dirty else ""
        status = f" -- {self.mode} --{mult_text} | {self.filename}{dirty_flag} | {self.row+1}:{self.col+1}"
        try: self.stdscr.addstr(h-2, 0, status[:w-1].ljust(w-1), curses.A_REVERSE)
        except curses.error: pass

        footer = self.status_message if self.status_message else (":" if self.mode == "COMMAND" else "") + self.command_buffer
        try: self.stdscr.addstr(h-1, 0, footer[:w-1].ljust(w-1))
        except curses.error: pass

        self.stdscr.move(self.row - self.top_row, min(self.col - self.left_col, w - 1))
        self.stdscr.refresh()
        self.update_cursor_shape()

    def handle_normal(self, k):
        self.status_message = ""
        try: char = chr(k)
        except: char = str(k)

        # Global fast exit shortcut bypass
        if char == 'Z':
            next_k = self.stdscr.getch()
            if chr(next_k) == 'Z':
                Path(self.filename).write_text("\n".join(self.lines))
                return True # Signal breakout flag to loop handler

        # Process multiplier tracking bounds (e.g. '12j')
        if char.isdigit() and (char != '0' or self.multiplier):
            self.multiplier += char
            return False

        count = int(self.multiplier) if self.multiplier else 1
        self.multiplier = ""

        # DYNAMIC LOOKUP: Checks keymap directly
        if char in NORMAL_KEYMAP:
            NORMAL_KEYMAP[char](self, count)
        else:
            # Multi-Key Structural Sequences
            if char == 'g':
                next_k = self.stdscr.getch()
                if chr(next_k) == 'g':
                    self.row = 0
                    self.col = 0
            elif char == 'G':
                self.row = len(self.lines) - 1
                self.col = 0
            elif char == 'd':
                next_k = self.stdscr.getch()
                next_char = chr(next_k)
                if next_char == 'dd':
                    self.dirty = True
                    for _ in range(count):
                        if len(self.lines) > 1: self.lines.pop(self.row)
                        else: self.lines = [""]
                    self.row = max(0, min(self.row, len(self.lines)-1))
                elif next_char == 'G':
                    self.dirty = True
                    self.lines = self.lines[:self.row]
                    if not self.lines: self.lines = [""]
                    self.row = len(self.lines) - 1
                    self.col = 0

        self.clamp_cursor()
        return False

    def handle_insert(self, k):
        if k == 27:
            self.mode = "NORMAL"
            self.clamp_cursor()
            return

        if k == curses.KEY_LEFT: self.col -= 1
        elif k == curses.KEY_RIGHT: self.col += 1
        elif k == curses.KEY_UP: self.row -= 1
        elif k == curses.KEY_DOWN: self.row += 1

        elif k in (10, 13):
            self.dirty = True
            rem = self.lines[self.row][self.col:]
            self.lines[self.row] = self.lines[self.row][:self.col]
            self.row += 1
            self.lines.insert(self.row, rem)
            self.col = 0
        elif k in (curses.KEY_BACKSPACE, 127, 8):
            self.dirty = True
            if self.col > 0:
                line = self.lines[self.row]
                self.lines[self.row] = line[:self.col-1] + line[self.col:]
                self.col -= 1
            elif self.row > 0:
                self.col = len(self.lines[self.row-1])
                self.lines[self.row-1] += self.lines.pop(self.row)
                self.row -= 1
        elif 32 <= k <= 126:
            self.dirty = True
            line = self.lines[self.row]
            self.lines[self.row] = line[:self.col] + chr(k) + line[self.col:]
            self.col += 1

        self.clamp_cursor()

    def execute_colon_command(self, cmd):
        cmd = cmd.strip()
        if not cmd: return False

        # Dynamic Regex Substitution Logic: %s/find/replace/g
        if cmd.startswith("%s/") or cmd.startswith("%s"):
            parts = cmd.split('/')
            if len(parts) >= 4 and parts[0] == "%s":
                find_str, replace_str, flags = parts[1], parts[2], parts[3]
                count_changes = 0
                for idx in range(len(self.lines)):
                    if find_str in self.lines[idx]:
                        self.dirty = True
                        limit = 0 if 'g' in flags else 1
                        updated, num = re.subn(re.escape(find_str), replace_str, self.lines[idx], count=limit)
                        self.lines[idx] = updated
                        count_changes += num
                self.status_message = f"Substituted {count_changes} occurrences of '{find_str}'"
                return False

        if cmd in ("wq", "w"):
            try:
                Path(self.filename).write_text("\n".join(self.lines))
                self.dirty = False
                self.status_message = f'"{self.filename}" written'
            except Exception as e:
                self.status_message = f"Write Error: {e}"
        if cmd in ("wq", "q"):
            if self.dirty and cmd == "q":
                self.status_message = "No write since last change (add ! to override)"
                return False
            else: 
                return True # Return true breakout signal safely
        elif cmd == "q!": 
            return True # Return true breakout signal safely
            
        return False

    def run(self):
        while True:
            try:
                self.render()
                k = self.stdscr.getch()
                if k == curses.KEY_RESIZE: continue

                if self.mode == "INSERT": 
                    self.handle_insert(k)
                elif self.mode in ("NORMAL", "VISUAL"): 
                    if self.handle_normal(k): 
                        break
                elif self.mode == "COMMAND":
                    if k in (10, 13):
                        cmd = self.command_buffer
                        self.mode = "NORMAL"
                        self.command_buffer = ""
                        if self.execute_colon_command(cmd): 
                            break
                    elif k == 27:
                        self.mode = "NORMAL"; self.command_buffer = ""
                    elif k in (curses.KEY_BACKSPACE, 127, 8):
                        self.command_buffer = self.command_buffer[:-1]
                    else:
                        try: self.command_buffer += chr(k)
                        except: pass
            except KeyboardInterrupt: 
                break

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Handle help or empty list
    if not args or args[0] in ("--help", "-h"):
        print("PyVi: A lightweight Python Vi-clone.")
        print("Usage: pyvi <filename>")
        print("""
Python-Vi
Usage:
  pyvi {files}

Files:
  files: the text-based file you want to open

Notes:
  An expanded clone of vi made by SpyDrone.
  MODIFICATION NOTICE: This version has been fully rewritten from the original
  monolithic framework to run on an extensible, dynamic Keymap Command Registry.
        """)
        return

    filename = args[0]
    if not isinstance(filename, str):
        print(f"Error: Expected filename as string, got {type(filename).__name__}")
        return

    try:
        curses.wrapper(lambda s: PyVi(s, filename).run())
    except Exception as e:
        print(f"PyVi error: {e}")
