# browse.py
# Interactive text-mode browser for BUGPy-mOS.
# Fetches web pages, strips HTML to readable text, numbers links so you
# can follow them by typing their number.
#
# Runs as an interactive session inside the BUGPy shell.
# Type 'q' or 'quit' to return to the shell.
#
# Navigation commands (typed at the browse> prompt):
#   <number>          Follow link N from the current page
#   b / back          Go back one page
#   f / forward       Go forward one page
#   r / reload        Reload the current page
#   h / history       Show browsing history for this session
#   bm / bookmark     Bookmark the current page
#   bm list           List all bookmarks
#   bm go <N>         Go to bookmark N
#   bm del <N>        Delete bookmark N
#   url / u           Show the current page URL
#   open <url>        Navigate to a URL directly
#   find <text>       Find text on the current page
#   save <file>       Save the current page text to a file
#   q / quit          Exit the browser
#
# No JavaScript, no CSS rendering, no images (shown as [image: alt]).
# Forms are not supported in this version.

import urllib.request
import urllib.error
import urllib.parse
import html.parser
import textwrap
import os
import sys
from pathlib import Path
from . import color_print

# Terminal width — used for text reflowing
try:
    _WIDTH = min(os.get_terminal_size().columns, 100)
except (OSError, AttributeError):
    _WIDTH = 80

# Bookmarks file inside the encrypted drive
_BM_FILE = Path(__file__).resolve().parent.parent / "config" / "bookmarks.txt"

# Tags whose content we skip entirely
_SKIP_TAGS = {
    'script', 'style', 'noscript', 'head', 'meta', 'link',
    'svg', 'path', 'iframe', 'object', 'embed', 'canvas',
    'template', 'nav', 'footer', 'aside',
}

# Block-level tags that cause a line break
_BLOCK_TAGS = {
    'p', 'div', 'section', 'article', 'main', 'header',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'dt', 'dd', 'blockquote', 'pre', 'br',
    'tr', 'th', 'td', 'caption', 'figure', 'figcaption',
}

# Heading tags for emphasis
_HEADING_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


# ---------------------------------------------------------------------------
# HTML Parser
# ---------------------------------------------------------------------------

class _Parser(html.parser.HTMLParser):
    """
    Converts HTML into a list of (type, content) tokens:
      ('text',    string)         — plain text
      ('heading', (level, text))  — h1-h6
      ('link',    (href, text))   — anchor
      ('image',   alt_text)       — img
      ('break',   None)           — block boundary
      ('hr',      None)           — horizontal rule
      ('bullet',  text)           — list item
      ('pre',     text)           — preformatted block
    """

    def __init__(self, base_url=""):
        super().__init__()
        self._base_url    = base_url
        self.tokens       = []
        self._skip_depth  = 0
        self._in_pre      = False
        self._pre_buf     = []
        self._link_href   = None
        self._link_buf    = []
        self._in_link     = False
        self._in_heading  = False
        self._heading_tag = None
        self._heading_buf = []
        self._in_li       = False
        self._li_buf      = []
        self._tag_stack   = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._tag_stack.append(tag)

        if tag in _SKIP_TAGS:
            self._skip_depth += 1
            return

        if self._skip_depth > 0:
            return

        attrs_dict = dict(attrs)

        if tag == 'pre':
            self._in_pre  = True
            self._pre_buf = []
            return

        if tag in _HEADING_TAGS:
            self._in_heading  = True
            self._heading_tag = tag
            self._heading_buf = []
            return

        if tag == 'a':
            href = attrs_dict.get('href', '')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                # Resolve relative URLs
                if href.startswith('//'):
                    href = 'https:' + href
                elif not href.startswith('http'):
                    href = urllib.parse.urljoin(self._base_url, href)
                self._link_href = href
                self._link_buf  = []
                self._in_link   = True
            return

        if tag == 'img':
            alt = attrs_dict.get('alt', '').strip()
            if alt:
                self.tokens.append(('image', alt))
            return

        if tag == 'hr':
            self.tokens.append(('hr', None))
            return

        if tag == 'li':
            self._in_li  = True
            self._li_buf = []
            return

        if tag in _BLOCK_TAGS:
            self.tokens.append(('break', None))

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in _SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return

        if self._skip_depth > 0:
            return

        if tag == 'pre':
            text = ''.join(self._pre_buf).strip()
            if text:
                self.tokens.append(('pre', text))
            self._in_pre = False
            return

        if tag in _HEADING_TAGS and self._in_heading and tag == self._heading_tag:
            text = ''.join(self._heading_buf).strip()
            if text:
                level = int(tag[1])
                self.tokens.append(('heading', (level, text)))
            self._in_heading  = False
            self._heading_tag = None
            return

        if tag == 'a' and self._in_link:
            text = ''.join(self._link_buf).strip()
            if text and self._link_href:
                self.tokens.append(('link', (self._link_href, text)))
            self._in_link   = False
            self._link_href = None
            return

        if tag == 'li' and self._in_li:
            text = ''.join(self._li_buf).strip()
            if text:
                self.tokens.append(('bullet', text))
            self._in_li = False
            return

        if tag in _BLOCK_TAGS:
            self.tokens.append(('break', None))

    def handle_data(self, data):
        if self._skip_depth > 0:
            return

        text = data  # keep original spacing for pre blocks

        if self._in_pre:
            self._pre_buf.append(text)
            return

        # Collapse whitespace for normal text
        text = ' '.join(data.split())
        if not text:
            return

        if self._in_heading:
            self._heading_buf.append(text)
            return

        if self._in_link:
            self._link_buf.append(text)
            return

        if self._in_li:
            self._li_buf.append(text)
            return

        self.tokens.append(('text', text))

    def handle_entityref(self, name):
        entities = {
            'amp': '&', 'lt': '<', 'gt': '>',
            'quot': '"', 'apos': "'", 'nbsp': ' ',
            'mdash': '—', 'ndash': '–', 'hellip': '…',
            'laquo': '«', 'raquo': '»',
        }
        char = entities.get(name, '')
        if char:
            self.handle_data(char)

    def handle_charref(self, name):
        try:
            if name.startswith('x'):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            self.handle_data(char)
        except (ValueError, OverflowError):
            pass


# ---------------------------------------------------------------------------
# Renderer — converts tokens to display lines + link table
# ---------------------------------------------------------------------------

def _render(tokens, width=_WIDTH):
    """
    Convert token list to (lines, links) where:
      lines — list of strings ready to print
      links — list of (url, label) in order of appearance
    """
    lines  = []
    links  = []
    buf    = []    # current paragraph text buffer

    def flush_buf():
        text = ' '.join(buf).strip()
        if text:
            for line in textwrap.wrap(text, width - 2):
                lines.append('  ' + line)
        buf.clear()

    for token_type, content in tokens:

        if token_type == 'break':
            flush_buf()
            if lines and lines[-1] != '':
                lines.append('')

        elif token_type == 'text':
            buf.append(content)

        elif token_type == 'heading':
            flush_buf()
            lines.append('')
            level, text = content
            if level == 1:
                bar = '═' * min(len(text) + 4, width - 2)
                lines.append('  ' + bar)
                lines.append('  ' + text.upper())
                lines.append('  ' + bar)
            elif level == 2:
                lines.append('  ── ' + text + ' ──')
            elif level == 3:
                lines.append('  • ' + text)
            else:
                lines.append('  ' + text)
            lines.append('')

        elif token_type == 'link':
            href, text = content
            idx = len(links) + 1
            links.append((href, text))
            buf.append(f"{text} [{idx}]")

        elif token_type == 'image':
            flush_buf()
            lines.append(f"  [image: {content}]")

        elif token_type == 'bullet':
            flush_buf()
            for i, line in enumerate(textwrap.wrap(content, width - 6)):
                prefix = '  • ' if i == 0 else '    '
                lines.append(prefix + line)

        elif token_type == 'pre':
            flush_buf()
            lines.append('')
            for line in content.splitlines():
                lines.append('  ' + line[:width - 2])
            lines.append('')

        elif token_type == 'hr':
            flush_buf()
            lines.append('  ' + '─' * (width - 4))

    flush_buf()

    # Collapse runs of more than 2 blank lines
    result = []
    blank_count = 0
    for line in lines:
        if line == '':
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)

    return result, links


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------

def _fetch(url):
    """
    Fetch a URL and return (final_url, title, lines, links) or raise.
    Follows redirects, handles encoding, strips HTML.
    """
    # Add scheme if missing
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'BUGPy-browse/1.0 (text browser)',
            'Accept': 'text/html,text/plain',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        final_url   = resp.geturl()
        content_type = resp.headers.get('Content-Type', 'text/html')
        raw         = resp.read()

    # Detect encoding
    encoding = 'utf-8'
    if 'charset=' in content_type:
        encoding = content_type.split('charset=')[-1].split(';')[0].strip()

    try:
        html_text = raw.decode(encoding, errors='replace')
    except (LookupError, UnicodeDecodeError):
        html_text = raw.decode('utf-8', errors='replace')

    # Extract title
    title = final_url
    import re
    m = re.search(r'<title[^>]*>(.*?)</title>', html_text, re.IGNORECASE | re.DOTALL)
    if m:
        title = ' '.join(m.group(1).split())

    # Parse and render
    parser = _Parser(base_url=final_url)
    try:
        parser.feed(html_text)
    except Exception:
        pass

    lines, links = _render(parser.tokens)

    return final_url, title, lines, links


# ---------------------------------------------------------------------------
# Bookmark manager
# ---------------------------------------------------------------------------

def _bm_load():
    if not _BM_FILE.exists():
        return []
    return [
        line.strip()
        for line in _BM_FILE.read_text().splitlines()
        if line.strip()
    ]


def _bm_save(entries):
    _BM_FILE.parent.mkdir(parents=True, exist_ok=True)
    _BM_FILE.write_text('\n'.join(entries) + '\n')


def _bm_add(url, title):
    entries = _bm_load()
    entry   = f"{url}  |  {title}"
    if entry not in entries:
        entries.append(entry)
        _bm_save(entries)
        return True
    return False


def _bm_list():
    entries = _bm_load()
    if not entries:
        print("  No bookmarks saved.")
        return
    color_print.cprint("  Bookmarks:", "EMPHASIS")
    for i, e in enumerate(entries, 1):
        parts = e.split('  |  ', 1)
        url   = parts[0]
        title = parts[1] if len(parts) > 1 else ''
        print(f"  {i:>3}  {title or url}")
        if title:
            color_print.cprint(f"       {url}", "DARKBLUE")


def _bm_go(n):
    entries = _bm_load()
    if n < 1 or n > len(entries):
        color_print.cprint(f"  No bookmark {n}.", "DARKRED")
        return None
    return entries[n - 1].split('  |  ', 1)[0]


def _bm_del(n):
    entries = _bm_load()
    if n < 1 or n > len(entries):
        color_print.cprint(f"  No bookmark {n}.", "DARKRED")
        return
    removed = entries.pop(n - 1)
    _bm_save(entries)
    print(f"  Removed: {removed}")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _display_page(title, lines, links, url):
    """Print the rendered page with a header and link index at the bottom."""
    # Clear and print header
    print("\033[2J\033[H", end="")   # clear screen

    color_print.cprint("─" * _WIDTH, "DARKBLUE")
    color_print.cprint(f"  {title}", "EMPHASIS")
    color_print.cprint(f"  {url}", "DARKBLUE")
    color_print.cprint("─" * _WIDTH, "DARKBLUE")
    print()

    # Page content
    for line in lines:
        print(line)

    # Link index
    if links:
        print()
        color_print.cprint("─" * _WIDTH, "DARKBLUE")
        color_print.cprint("  Links:", "ORANGE")
        for i, (href, label) in enumerate(links, 1):
            label_trunc = label[:40] + '…' if len(label) > 40 else label
            href_trunc  = href[:_WIDTH - 50] if len(href) > _WIDTH - 50 else href
            print(f"  [{i:>3}]  {label_trunc:<42}  {href_trunc}")

    print()
    color_print.cprint("─" * _WIDTH, "DARKBLUE")


def _show_help():
    print("""
  Browse commands:
    <number>         Follow link N
    open <url>       Navigate to a URL
    b / back         Go back
    f / forward      Go forward
    r / reload       Reload current page
    find <text>      Find text on this page
    save <file>      Save page text to a file
    url / u          Show current URL
    h / history      Show session history
    bm               Bookmark current page
    bm list          List bookmarks
    bm go <N>        Go to bookmark N
    bm del <N>       Delete bookmark N
    q / quit         Exit browser
""")


# ---------------------------------------------------------------------------
# Main browser loop
# ---------------------------------------------------------------------------

def _browser_loop(start_url):
    history      = []   # list of (url, title, lines, links)
    hist_pos     = -1
    current_url  = None
    current_data = None   # (title, lines, links)

    def load(url, push=True):
        nonlocal hist_pos, current_url, current_data
        color_print.cprint(f"  Loading {url} ...", "DARKBLUE")
        try:
            final_url, title, lines, links = _fetch(url)
            current_url  = final_url
            current_data = (title, lines, links)
            if push:
                # Truncate forward history on new navigation
                del history[hist_pos + 1:]
                history.append((final_url, title, lines, links))
                hist_pos = len(history) - 1
            _display_page(title, lines, links, final_url)
        except urllib.error.URLError as e:
            color_print.cprint(f"  Error: {e.reason}", "DARKRED")
        except urllib.error.HTTPError as e:
            color_print.cprint(f"  HTTP {e.code}: {e.reason}", "DARKRED")
        except Exception as e:
            color_print.cprint(f"  Failed to load: {e}", "DARKRED")

    # Load the starting URL
    load(start_url)

    while True:
        try:
            color_print.cprint("browse> ", "GREEN", sameline=True)
            cmd = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        parts = cmd.split(None, 1)
        verb  = parts[0].lower()
        rest  = parts[1] if len(parts) > 1 else ''

        # --- Quit ---
        if verb in ('q', 'quit', 'exit'):
            break

        # --- Follow a numbered link ---
        elif verb.isdigit():
            if current_data:
                _, _, links = current_data
                n = int(verb)
                if 1 <= n <= len(links):
                    load(links[n - 1][0])
                else:
                    color_print.cprint(f"  No link {n} on this page.", "DARKRED")

        # --- Open URL ---
        elif verb in ('open', 'go', 'o'):
            if rest:
                load(rest)
            else:
                color_print.cprint("  Usage: open <url>", "DARKRED")

        # --- Back ---
        elif verb in ('b', 'back'):
            if hist_pos > 0:
                hist_pos -= 1
                url, title, lines, links = history[hist_pos]
                current_url  = url
                current_data = (title, lines, links)
                _display_page(title, lines, links, url)
            else:
                color_print.cprint("  Nothing to go back to.", "ORANGE")

        # --- Forward ---
        elif verb in ('f', 'forward'):
            if hist_pos < len(history) - 1:
                hist_pos += 1
                url, title, lines, links = history[hist_pos]
                current_url  = url
                current_data = (title, lines, links)
                _display_page(title, lines, links, url)
            else:
                color_print.cprint("  Nothing to go forward to.", "ORANGE")

        # --- Reload ---
        elif verb in ('r', 'reload'):
            if current_url:
                load(current_url, push=False)
                _display_page(*current_data, current_url)
            else:
                color_print.cprint("  No page loaded.", "ORANGE")

        # --- Show URL ---
        elif verb in ('url', 'u'):
            if current_url:
                color_print.cprint(f"  {current_url}", "DARKBLUE")
            else:
                print("  No page loaded.")

        # --- Find text ---
        elif verb == 'find':
            if not rest:
                color_print.cprint("  Usage: find <text>", "DARKRED")
            elif current_data:
                _, lines, _ = current_data
                query   = rest.lower()
                matches = [(i+1, l) for i, l in enumerate(lines) if query in l.lower()]
                if matches:
                    color_print.cprint(f"  {len(matches)} match(es) for '{rest}':", "ORANGE")
                    for lineno, line in matches[:20]:
                        # Highlight the match
                        lo  = line.lower()
                        idx = lo.find(query)
                        before = line[:idx]
                        match  = line[idx:idx+len(rest)]
                        after  = line[idx+len(rest):]
                        print(f"  L{lineno:<4} {before}", end="")
                        color_print.cprint(match, "ORANGE", sameline=True)
                        print(after)
                    if len(matches) > 20:
                        print(f"  ... and {len(matches)-20} more")
                else:
                    color_print.cprint(f"  '{rest}' not found on this page.", "ORANGE")

        # --- History ---
        elif verb in ('h', 'history'):
            if not history:
                print("  No history yet.")
            else:
                color_print.cprint("  Session history:", "EMPHASIS")
                for i, (url, title, _, _) in enumerate(history):
                    marker = "►" if i == hist_pos else " "
                    print(f"  {marker} {i+1:>3}  {title or url}")

        # --- Save page ---
        elif verb == 'save':
            if not rest:
                color_print.cprint("  Usage: save <filename>", "DARKRED")
            elif current_data:
                title, lines, _ = current_data
                try:
                    Path(rest).write_text('\n'.join(lines))
                    color_print.cprint(f"  Saved to {rest}", "GREEN")
                except Exception as e:
                    color_print.cprint(f"  Save failed: {e}", "DARKRED")

        # --- Bookmarks ---
        elif verb == 'bm':
            sub = rest.split(None, 1)
            sub_cmd = sub[0].lower() if sub else ''
            sub_arg = sub[1] if len(sub) > 1 else ''

            if not sub_cmd:
                # Bookmark current page
                if current_url and current_data:
                    title = current_data[0]
                    if _bm_add(current_url, title):
                        color_print.cprint(f"  Bookmarked: {title}", "GREEN")
                    else:
                        color_print.cprint("  Already bookmarked.", "ORANGE")
                else:
                    color_print.cprint("  No page loaded.", "ORANGE")
            elif sub_cmd == 'list':
                _bm_list()
            elif sub_cmd == 'go':
                if sub_arg.isdigit():
                    url = _bm_go(int(sub_arg))
                    if url:
                        load(url)
                else:
                    color_print.cprint("  Usage: bm go <N>", "DARKRED")
            elif sub_cmd == 'del':
                if sub_arg.isdigit():
                    _bm_del(int(sub_arg))
                else:
                    color_print.cprint("  Usage: bm del <N>", "DARKRED")
            else:
                color_print.cprint(f"  Unknown bm command '{sub_cmd}'", "DARKRED")

        # --- Help ---
        elif verb in ('?', 'help'):
            _show_help()

        else:
            # If it looks like a URL, try to load it directly
            if '.' in verb and ' ' not in cmd:
                load(cmd)
            else:
                color_print.cprint(
                    f"  Unknown command '{verb}'. Type ? for help.", "ORANGE"
                )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""\
BROWSE [A-3-iii]
Usage:
  browse <params>

Parameters:
  url   The URL to open (http:// or https:// — scheme optional)
        If no URL given, opens the BUGPy start page

Commands inside the browser:
  <N>            Follow link number N
  open <url>     Navigate to a URL
  b / f          Back / Forward
  r              Reload
  find <text>    Search for text on the page
  save <file>    Save page text to a file
  bm             Bookmark current page
  bm list        List bookmarks
  bm go <N>      Go to bookmark N
  h              Session history
  q              Quit browser""")
        return

    url = args[0] if args else "https://lite.duckduckgo.com/lite"

    color_print.cprint("BUGPy Browser", "GREEN", sameline=True)
    color_print.cprint(" — text mode  (type ? for help, q to quit)", "DARKBLUE")
    print()

    try:
        _browser_loop(url)
    except Exception as e:
        color_print.cprint(f"browse: unexpected error: {e}", "DARKRED")

    print()
    color_print.cprint("browse: returned to BUGPy shell.", "DARKBLUE")
