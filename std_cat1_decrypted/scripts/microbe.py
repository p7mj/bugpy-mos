import sys
import os
import curses
from pathlib import Path

# Fix escape sequence lag for snappy key detection
os.environ.setdefault('ESCDELAY', '25')

class Microbe:
    def __init__(self, stdscr, filename):
        self.stdscr = stdscr
        if isinstance(filename, list):
            self.filename = filename[0] if len(filename) > 0 else ""
        else:
            self.filename = filename if filename else ""

        self.lines = self._load_file()

        # State tracking engine
        self.row = 0
        self.col = 0
        self.top_row = 0
        self.left_col = 0
        self.dirty = False
        
        # Clipboard, Selection, and Search
        self.clipboard_buffer = ""
        self.select_all_active = False
        self.sel_start = None  
        
        # UI States
        self.show_help = False
        self.prompt_mode = None  # None, "quit_warn", "save_as", "find"
        self.prompt_buffer = ""
        self.status_message = ""
        self.status_is_error = False
        
        self._init_curses()

    def _init_curses(self):
        curses.use_default_colors()
        curses.start_color()
        self.stdscr.keypad(True)
        curses.raw()
        curses.noecho()
        
        # Color profile pairs
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        try:
            curses.init_pair(2, curses.COLOR_WHITE, 236)
        except Exception:
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)
        
        try:
            curses.init_pair(5, 247, 236)
        except Exception:
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        try:
            curses.init_pair(6, 247, -1)
        except Exception:
            curses.init_pair(6, curses.COLOR_WHITE, -1)

    def _load_file(self):
        if not self.filename:
            return [""]
        try:
            p = Path(self.filename)
            return p.read_text().splitlines() if p.exists() else [""]
        except Exception:
            return [""]

    def clamp_cursor(self):
        self.row = max(0, min(self.row, len(self.lines) - 1))
        self.col = max(0, min(self.col, len(self.lines[self.row])))

    def scroll_view(self, available_rows, gutter_width):
        _, w = self.stdscr.getmaxyx()
        usable_width = max(w - gutter_width, 1)

        if self.row < self.top_row:
            self.top_row = self.row
        elif self.row >= self.top_row + available_rows:
            self.top_row = self.row - available_rows + 1

        if self.col < self.left_col:
            self.left_col = self.col
        elif self.col >= self.left_col + usable_width:
            self.left_col = self.col - usable_width + 1

    def _get_selection_range(self):
        if self.select_all_active:
            return ((0, 0), (len(self.lines) - 1, len(self.lines[-1])))
        if self.sel_start is not None:
            p1 = self.sel_start
            p2 = (self.row, self.col)
            return (p1, p2) if p1 <= p2 else (p2, p1)
        return None

    def _is_char_selected(self, r, c):
        rng = self._get_selection_range()
        if not rng:
            return False
        return rng[0] <= (r, c) < rng[1]

    def _get_selected_text(self):
        rng = self._get_selection_range()
        if not rng:
            return ""
        (r1, c1), (r2, c2) = rng
        if r1 == r2:
            return self.lines[r1][c1:c2]
        
        chunks = [self.lines[r1][c1:]]
        for r in range(r1 + 1, r2):
            chunks.append(self.lines[r])
        chunks.append(self.lines[r2][:c2])
        return "\n".join(chunks)

    def _delete_selection(self):
        rng = self._get_selection_range()
        if not rng:
            return
        (r1, c1), (r2, c2) = rng
        
        left_intact = self.lines[r1][:c1]
        right_intact = self.lines[r2][c2:]
        
        self.lines[r1] = left_intact + right_intact
        for _ in range(r2 - r1):
            self.lines.pop(r1 + 1)
            
        self.row, self.col = r1, c1
        self.select_all_active = False
        self.sel_start = None
        self.dirty = True

    def _execute_search(self, direction=1, start_from_current=True):
        if not self.prompt_buffer:
            return
        total_lines = len(self.lines)
        curr_row, curr_col = self.row, (self.col + direction if start_from_current else self.col)

        for i in range(total_lines + 1):
            check_row = (curr_row + (i * direction)) % total_lines
            line = self.lines[check_row]
            
            if i == 0 and start_from_current:
                found_col = line.find(self.prompt_buffer, max(0, curr_col)) if direction == 1 else line.rfind(self.prompt_buffer, 0, max(0, curr_col))
            else:
                found_col = line.find(self.prompt_buffer, 0) if direction == 1 else line.rfind(self.prompt_buffer, 0)

            if found_col != -1:
                self.row, self.col = check_row, found_col
                break

    def render(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.erase()

        footer_rows = 1  
        if self.show_help: footer_rows += 2
        if self.prompt_mode or self.status_message: footer_rows += 1

        edit_space_rows = max(1, h - footer_rows)
        max_line_digits = len(str(len(self.lines)))
        gutter_width = max_line_digits + 1

        self.scroll_view(edit_space_rows, gutter_width)

        # Dynamic Hardware Cursor Visibility State
        if self._get_selection_range() and self.prompt_mode is None:
            curses.curs_set(0)  
        else:
            curses.curs_set(1)  

        # 1. RENDERING TEXT CANVAS
        for i in range(edit_space_rows):
            file_row_idx = self.top_row + i
            if file_row_idx < len(self.lines):
                num_str = str(file_row_idx + 1)
                padded_num = num_str.rjust(max_line_digits)
                gutter_text = f"{padded_num} "

                gutter_style = curses.color_pair(6) if file_row_idx == self.row else curses.color_pair(5)
                text_style = curses.color_pair(2) if file_row_idx == self.row else curses.color_pair(1)

                try:
                    self.stdscr.addstr(i, 0, gutter_text, gutter_style)
                except curses.error: pass

                line_content = self.lines[file_row_idx]
                max_slice_len = max(w - gutter_width, 0)

                search_match_col = self.col if (self.prompt_mode == "find" and self.prompt_buffer and file_row_idx == self.row) else -1

                col_x = gutter_width
                for char_idx in range(self.left_col, self.left_col + max_slice_len):
                    if char_idx >= len(line_content):
                        if file_row_idx == self.row:
                            try:
                                self.stdscr.addch(i, col_x, ' ', text_style)
                            except curses.error: pass
                            col_x += 1
                        continue

                    char = line_content[char_idx]
                    render_attr = text_style

                    if self._is_char_selected(file_row_idx, char_idx):
                        render_attr = render_attr | curses.A_REVERSE
                    
                    if search_match_col != -1 and (search_match_col <= char_idx < search_match_col + len(self.prompt_buffer)):
                        render_attr = render_attr | curses.A_BOLD | curses.A_UNDERLINE

                    try:
                        self.stdscr.addch(i, col_x, char, render_attr)
                    except curses.error: pass
                    col_x += 1

        # 2. RENDERING STATUS BAR
        display_name = self.filename if self.filename else "No name"
        dirty_flag = " *" if self.dirty else ""
        selection_flag = " [SELECTED]" if self._get_selection_range() else ""
        meta_left = f" {display_name}{dirty_flag}{selection_flag} ({self.row + 1},{self.col + 1}) | ft:text | unix | utf-8"
        meta_right = "Alt-g: bindings, Ctrl-g: help "
        
        fill_gap = w - len(meta_left) - len(meta_right)
        raw_bar_text = f"{meta_left}{' ' * max(0, fill_gap)}{meta_right}"
        
        try:
            self.stdscr.addnstr(edit_space_rows, 0, raw_bar_text.ljust(w), w, curses.color_pair(3))
        except curses.error: pass

        # 3. RENDERING DRAWER WINDOWS
        prompt_row_idx = edit_space_rows + 1
        if self.show_help:
            row1 = " ^Q Quit, ^S Save, ^F Find, ^A Select All, ^C Copy, ^X Cut, ^V Paste"
            row2 = " ^K Cut Line, ^D Duplicate Line | Alt-g Toggle Bindings Menu"
            try:
                self.stdscr.addnstr(prompt_row_idx, 0, row1.ljust(w), w, curses.color_pair(3))
                self.stdscr.addnstr(prompt_row_idx + 1, 0, row2.ljust(w), w, curses.color_pair(3))
            except curses.error: pass
        elif self.prompt_mode == "quit_warn":
            msg = f"Save changes to '{display_name}'? (y/n) [Esc to cancel]: "
            try:
                self.stdscr.addstr(prompt_row_idx, 0, msg, curses.color_pair(1) | curses.A_BOLD)
            except curses.error: pass
        elif self.prompt_mode == "save_as":
            msg = f"Write to: {self.prompt_buffer}"
            try:
                self.stdscr.addnstr(prompt_row_idx, 0, msg.ljust(w), w, curses.color_pair(1))
            except curses.error: pass
        elif self.prompt_mode == "find":
            msg = f"Find (Press Up/Down for next/prev): {self.prompt_buffer}"
            try:
                self.stdscr.addnstr(prompt_row_idx, 0, msg.ljust(w), w, curses.color_pair(1))
            except curses.error: pass
        elif self.status_message:
            pair = curses.color_pair(4) if self.status_is_error else curses.color_pair(1)
            try:
                self.stdscr.addnstr(prompt_row_idx, 0, self.status_message.ljust(w), w, pair)
            except curses.error: pass

        # 4. PLACING CURSOR
        if self.prompt_mode in ("save_as", "find"):
            label = "Write to: " if self.prompt_mode == "save_as" else "Find (Press Up/Down for next/prev): "
            self.stdscr.move(prompt_row_idx, min(len(label) + len(self.prompt_buffer), w - 1))
        elif self.prompt_mode == "quit_warn":
            self.stdscr.move(prompt_row_idx, min(len(f"Save changes to '{display_name}'? (y/n) [Esc to cancel]: "), w - 1))
        else:
            self.stdscr.move(self.row - self.top_row, min(gutter_width + (self.col - self.left_col), w - 1))
            
        self.stdscr.refresh()

    def handle_key(self, k):
        # Auto-collapse helper drawer on editing action execution
        if k in (17, 19, 1, 6, 3, 24, 22, 11, 4) and k != 7:
            self.show_help = False

        is_shifting = False
        if k in (curses.KEY_SR, curses.KEY_SF, curses.KEY_SLEFT, curses.KEY_SRIGHT):
            is_shifting = True
            if self.sel_start is None and not self.select_all_active:
                self.sel_start = (self.row, self.col)

        # 1. Dialog Loop Processing
        if self.prompt_mode == "quit_warn":
            if k in (ord('y'), ord('Y')):
                if self.filename:
                    try:
                        Path(self.filename).write_text("\n".join(self.lines) + "\n")
                        return True
                    except Exception as e:
                        self.status_message, self.status_is_error, self.prompt_mode = f"Write error: {e}", True, None
                else:
                    self.prompt_mode, self.prompt_buffer = "save_as", ""
            elif k in (ord('n'), ord('N')): return True
            elif k == 27: self.prompt_mode = None
            return False

        if self.prompt_mode in ("save_as", "find"):
            if k in (10, 13):  # Enter key confirmed
                if self.prompt_mode == "save_as":
                    target = self.prompt_buffer.strip()
                    if target:
                        self.filename = target
                        try:
                            Path(self.filename).write_text("\n".join(self.lines) + "\n")
                            self.dirty = False
                            self.status_message = f"Saved successfully to {self.filename}"
                            self.prompt_mode = None
                            # Explicitly prevent fallthrough on direct save confirmations
                            return False 
                        except Exception as e:
                            self.status_message, self.status_is_error = f"Write error: {e}", True
                    self.prompt_mode = None
                    return False
                else:
                    self.prompt_mode = None
                    return False
            elif k == curses.KEY_DOWN: self._execute_search(direction=1, start_from_current=True)
            elif k == curses.KEY_UP: self._execute_search(direction=-1, start_from_current=True)
            elif k in (curses.KEY_BACKSPACE, 127, 8):
                self.prompt_buffer = self.prompt_buffer[:-1]
                if self.prompt_mode == "find": self._execute_search(direction=1, start_from_current=False)
            elif k == 27: self.prompt_mode = None
            elif 32 <= k <= 126:
                self.prompt_buffer += chr(k)
                if self.prompt_mode == "find": self._execute_search(direction=1, start_from_current=False)
            return False

        if self.status_message:
            self.status_message, self.status_is_error = "", False

        # If selection exists, intercept terminal Backspace, Delete, or KEY_DC inputs immediately
        if self._get_selection_range() and k in (curses.KEY_BACKSPACE, 127, 8, curses.KEY_DC):
            self._delete_selection()
            self.status_message = "Selection wiped"
            self.clamp_cursor()
            return False

        # Reset selection states on regular movements/inputs if shift modifier is missing
        if not is_shifting and k not in (3, 24, 17, 19, curses.KEY_DC, curses.KEY_RESIZE):
            self.select_all_active = False
            self.sel_start = None

        # 2. Main Buffer Bindings Engine
        if k == 17:  # ^Q
            if self.dirty: self.prompt_mode = "quit_warn"
            else: return True
        elif k == 19:  # ^S
            if not self.filename:
                self.prompt_mode, self.prompt_buffer = "save_as", ""
            else:
                try:
                    Path(self.filename).write_text("\n".join(self.lines) + "\n")
                    self.dirty, self.status_message = False, f"Saved to {self.filename}"
                except Exception as e:
                    self.status_message, self.status_is_error = f"Write error: {e}", True
        elif k == 1:  # ^A (Select All)
            self.select_all_active = True
            self.row, self.col = len(self.lines) - 1, len(self.lines[-1])
            self.status_message = "Entire document highlighted"
        elif k == 6:  # ^F (Find)
            self.prompt_mode, self.prompt_buffer = "find", ""
        elif k == 3:  # ^C (Copy)
            if self._get_selection_range():
                self.clipboard_buffer = self._get_selected_text()
                self.status_message = "Selection copied successfully to clipboard"
            else:
                self.clipboard_buffer = self.lines[self.row]
                self.status_message = "Active row captured to clipboard buffer"
        elif k == 24:  # ^X (Cut)
            if self._get_selection_range():
                self.clipboard_buffer = self._get_selected_text()
                self._delete_selection()
                self.status_message = "Selection captured to clipboard"
            else:
                self.clipboard_buffer = self.lines[self.row]
                if len(self.lines) > 1:
                    self.lines.pop(self.row)
                    self.row = min(self.row, len(self.lines) - 1)
                else:
                    self.lines[self.row] = ""
                self.col = 0
                self.dirty = True
                self.status_message = "Active line cut to clipboard"
        elif k == curses.KEY_DC:  # Standard single char forward delete (no active selection)
            if self.col < len(self.lines[self.row]):
                line = self.lines[self.row]
                self.lines[self.row] = line[:self.col] + line[self.col + 1:]
                self.dirty = True
            elif self.row < len(self.lines) - 1:
                self.lines[self.row] += self.lines.pop(self.row + 1)
                self.dirty = True
        elif k == 22:  # ^V (Paste)
            if self.clipboard_buffer:
                if self._get_selection_range():
                    self._delete_selection()
                
                if "\n" in self.clipboard_buffer:
                    paste_lines = self.clipboard_buffer.split("\n")
                    left, right = self.lines[self.row][:self.col], self.lines[self.row][self.col:]
                    
                    self.lines[self.row] = left + paste_lines[0]
                    for idx in range(1, len(paste_lines) - 1):
                        self.lines.insert(self.row + idx, paste_lines[idx])
                    
                    insert_count = len(paste_lines) - 1
                    self.lines.insert(self.row + insert_count, paste_lines[-1] + right)
                    self.row += insert_count
                    self.col = len(paste_lines[-1])
                else:
                    line = self.lines[self.row]
                    self.lines[self.row] = line[:self.col] + self.clipboard_buffer + line[self.col:]
                    self.col += len(self.clipboard_buffer)
                self.dirty = True
        elif k == 11:  # ^K
            if len(self.lines) > 1:
                self.lines.pop(self.row)
                self.row, self.col = min(self.row, len(self.lines) - 1), 0
            else:
                self.lines[self.row], self.col = "", 0
            self.dirty = True
        elif k == 4:  # ^D
            self.lines.insert(self.row + 1, self.lines[self.row])
            self.row, self.dirty = self.row + 1, True
        elif k == 7:  # ^G
            self.show_help = not self.show_help

        # Navigation Vectors
        elif k in (curses.KEY_UP, curses.KEY_SR):
            if self.row > 0:
                self.row -= 1
                self.col = min(self.col, len(self.lines[self.row]))
        elif k in (curses.KEY_DOWN, curses.KEY_SF):
            if self.row < len(self.lines) - 1:
                self.row += 1
                self.col = min(self.col, len(self.lines[self.row]))
        elif k in (curses.KEY_LEFT, curses.KEY_SLEFT):
            if self.col > 0: self.col -= 1
            elif self.row > 0:
                self.row -= 1
                self.col = len(self.lines[self.row])
        elif k in (curses.KEY_RIGHT, curses.KEY_SRIGHT):
            if self.col < len(self.lines[self.row]): self.col += 1
            elif self.row < len(self.lines) - 1:
                self.row, self.col = self.row + 1, 0

        # Sequence Escape Parses
        elif k == 27:
            self.stdscr.nodelay(True)
            next_k = self.stdscr.getch()
            self.stdscr.nodelay(False)
            if next_k in (ord('g'), ord('G')): self.show_help = not self.show_help

        # Typing Pipeline Channels
        elif k in (10, 13):
            if self._get_selection_range(): self._delete_selection()
            left, right = self.lines[self.row][:self.col], self.lines[self.row][self.col:]
            self.lines[self.row] = left
            self.row += 1
            self.lines.insert(self.row, right)
            self.col, self.dirty = 0, True
        elif k in (curses.KEY_BACKSPACE, 127, 8):
            if self.col > 0:
                line = self.lines[self.row]
                self.lines[self.row] = line[:self.col - 1] + line[self.col:]
                self.col -= 1
                self.dirty = True
            elif self.row > 0:
                self.col = len(self.lines[self.row - 1])
                self.lines[self.row - 1] += self.lines.pop(self.row)
                self.row -= 1
                self.dirty = True
        elif 32 <= k <= 126:
            if self._get_selection_range(): self._delete_selection()
            line = self.lines[self.row]
            self.lines[self.row] = line[:self.col] + chr(k) + line[self.col:]
            self.col += 1
            self.dirty = True

        self.clamp_cursor()
        return False

    def run(self):
        while True:
            try:
                self.render()
                k = self.stdscr.getch()
                if k == curses.KEY_RESIZE: continue
                if self.handle_key(k): break
            except KeyboardInterrupt: break

def main(args=None):
    if args is None: args = sys.argv[1:]
    target_path = args[0] if (args and len(args) > 0) else ""
    curses.wrapper(lambda s: Microbe(s, target_path).run())

if __name__ == "__main__":
    main()
