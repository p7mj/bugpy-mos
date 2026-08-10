# drone.py
# Terminal drone shooter game — runs inside BUGPy using curses.
# Survive waves of enemy drones. WASD/arrows to move, Space to shoot.

import curses
import time
import random
import math

# ── timing ─────────────────────────────────────────────────────────────────
TICK     = 0.05    # seconds per frame (~20 fps)
HEAT_MAX = 100

# ── difficulty presets ──────────────────────────────────────────────────────
DIFFICULTIES = {
    'easy': {
        'label':       'EASY',
        'desc':        '20 armor · slow enemies · no shooters until wave 4',
        'armor':       20,
        'shoot_cd':    2,
        'heat_shot':   4,
        'heat_cool':   8.0,
        'bullet_spd':  0.85,
        'enemy_spd':   0.06,
        'ebullet_spd': 0.20,
        'spawn_rate':  {1:5.0, 2:4.2, 3:3.5, 4:3.0, 5:2.5},
        'wave_goal':   {1:6,   2:8,   3:10,  4:12,  5:99},
        'wave_types':  {1:['fast'],
                        2:['fast','fast','fast','tank'],
                        3:['fast','tank'],
                        4:['fast','tank','shooter'],
                        5:['fast','tank','shooter','shooter']},
        'drop_r':      0.20, 
        'inv_frames':  50,
    },
    'normal': {
        'label':       'NORMAL',
        'desc':        '10 armor · moderate pace · shooters from wave 2',
        'armor':       10,
        'shoot_cd':    3,
        'heat_shot':   6,
        'heat_cool':   6.0,
        'bullet_spd':  0.90,
        'enemy_spd':   0.09,
        'ebullet_spd': 0.28,
        'spawn_rate':  {1:4.0, 2:3.2, 3:2.6, 4:2.1, 5:1.7},
        'wave_goal':   {1:8,   2:12,  3:16,  4:20,  5:99},
        'wave_types':  {1:['fast'],
                        2:['fast','fast','shooter'],
                        3:['fast','tank','shooter'],
                        4:['fast','tank','shooter','shooter'],
                        5:['tank','shooter','shooter']},
        'drop_r':      0.10,
        'inv_frames':  35,
    },
    'hard': {
        'label':       'HARD',
        'desc':        '6 armor · fast enemies · shooters from wave 1',
        'armor':       6,
        'shoot_cd':    3,
        'heat_shot':   7,
        'heat_cool':   5.0,
        'bullet_spd':  0.92,
        'enemy_spd':   0.14,
        'ebullet_spd': 0.36,
        'spawn_rate':  {1:2.8, 2:2.2, 3:1.8, 4:1.4, 5:1.1},
        'wave_goal':   {1:10,  2:14,  3:18,  4:22,  5:99},
        'wave_types':  {1:['fast','fast','shooter'],
                        2:['fast','tank','shooter'],
                        3:['tank','shooter','shooter'],
                        4:['tank','tank','shooter','shooter'],
                        5:['tank','shooter','shooter','shooter']},
        'drop_r':      0.06,
        'inv_frames':  25,
    },
    'impossible': {
        'label':       'IMPOSSIBLE',
        'desc':        '4 armor · breakneck speed · barely any drops',
        'armor':       4,
        'shoot_cd':    4,
        'heat_shot':   8,
        'heat_cool':   4.0,
        'bullet_spd':  0.95,
        'enemy_spd':   0.22,
        'ebullet_spd': 0.50,
        'spawn_rate':  {1:1.8, 2:1.4, 3:1.1, 4:0.9, 5:0.7},
        'wave_goal':   {1:8,   2:12,  3:16,  4:20,  5:99},
        'wave_types':  {1:['fast','fast','shooter'],
                        2:['fast','tank','shooter','shooter'],
                        3:['tank','tank','shooter','shooter'],
                        4:['tank','shooter','shooter','shooter'],
                        5:['tank','tank','shooter','shooter','shooter']},
        'drop_r':      0.03,
        'inv_frames':  18,
    },
}

DIFF_ORDER = ['easy', 'normal', 'hard', 'impossible']

# ── enemy base stats ────────────────────────────────────────────────────────
ENEMY_TYPES = {
    'fast':    ('_  _', 1,  10, False, 1.6,  True),
    'tank':    (' ___ ', 8,  50, True,  0.50, False), # Tanks are tougher now
    'shooter': ('◉',    2,  20, True,  1.0,  True),
}

# ── color pair IDs ─────────────────────────────────────────────────────────
C_PLAYER, C_ENEMY_F, C_ENEMY_T, C_ENEMY_S, C_BULLET, C_HUD, C_WARN, C_DANGER, \
C_DROP_C, C_DROP_R, C_TITLE, C_DIM, C_EBULLET, C_WAVE, C_EASY, C_HARD = range(1, 17)

def _init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_PLAYER,  curses.COLOR_CYAN,    -1)
    curses.init_pair(C_ENEMY_F, curses.COLOR_BLUE,    -1)
    curses.init_pair(C_ENEMY_T, curses.COLOR_GREEN,   -1)
    curses.init_pair(C_ENEMY_S, curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_BULLET,  curses.COLOR_CYAN,    -1)
    curses.init_pair(C_HUD,     curses.COLOR_WHITE,   -1)
    curses.init_pair(C_WARN,    curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_DANGER,  curses.COLOR_RED,     -1)
    curses.init_pair(C_DROP_C,  curses.COLOR_CYAN,    -1)
    curses.init_pair(C_DROP_R,  curses.COLOR_GREEN,   -1)
    curses.init_pair(C_TITLE,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_DIM,     curses.COLOR_BLACK,   -1)
    curses.init_pair(C_EBULLET, curses.COLOR_RED,     -1)
    curses.init_pair(C_WAVE,    curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_EASY,    curses.COLOR_GREEN,   -1)
    curses.init_pair(C_HARD,    curses.COLOR_RED,     -1)

ENEMY_COL_MAP = {'fast': C_ENEMY_F, 'tank': C_ENEMY_T, 'shooter': C_ENEMY_S}
DIFF_COL_MAP  = {'easy': C_EASY, 'normal': C_HUD, 'hard': C_WARN, 'impossible': C_HARD}

# ── safe draw ──────────────────────────────────────────────────────────────
def _draw(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0:
        return
    if x + len(text) > w:
        text = text[:w - x]
    if not text:
        return
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass

# ── game objects ───────────────────────────────────────────────────────────
class Player:
    def __init__(self, cx, cy, armor):
        self.x, self.y = float(cx), float(cy)
        self.hp, self.heat, self.shoot_cd, self.inv = armor, 0.0, 0, 0

class Bullet:
    def __init__(self, x, y, dy, dx=0.0, friendly=True, char='•'):
        self.x, self.y, self.dy, self.dx, self.friendly, self.char = float(x), float(y), dy, dx, friendly, char

class Enemy:
    def __init__(self, x, h, etype, base_spd_frac):
        sym, hp, pts, shoots, spd_mul, drifts = ENEMY_TYPES[etype]
        self.x, self.y = float(x), 2.0
        self.type, self.hp, self.max_hp, self.pts, self.sym, self.shoots = etype, hp, hp, pts, sym, shoots
        self.spd = base_spd_frac * h * spd_mul
        self.shoot_timer = random.uniform(1.5, 4.0)
        self.mg_timer = 0.5 # Tank machine gun timer
        self.drift_v = random.uniform(-0.3, 0.3) if drifts else 0.0
        self.drift_timer = random.uniform(1.0, 3.0)

class Drop:
    def __init__(self, x, y, kind):
        self.x, self.y, self.kind = float(x), float(y), kind
        self.life = 6.0 
        self.on_ground = False

# ── UI ──
def _diff_screen(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    sel = 1
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        header = ["╔══════════════════════════════════╗", "║       DRONE  ASSAULT   v1.3      ║", "╚══════════════════════════════════╝"]
        sy = max(0, h // 2 - 10)
        for i, line in enumerate(header):
            _draw(stdscr, sy + i, max(0, w // 2 - len(line) // 2), line, curses.color_pair(C_TITLE) | curses.A_BOLD)
        
        oy = sy + 5
        for i, key in enumerate(DIFF_ORDER):
            d, col = DIFFICULTIES[key], DIFF_COL_MAP[key]
            mark = '►' if i == sel else ' '
            _draw(stdscr, oy + i*3, max(0, w//2 - 20), f'{mark} {d["label"]}', curses.color_pair(col) | (curses.A_BOLD if i == sel else 0))
            _draw(stdscr, oy + i*3 + 1, max(0, w//2 - 20), f"  {d['desc']}", curses.color_pair(C_DIM if i != sel else C_HUD))
            
        stdscr.refresh()
        k = stdscr.getch()
        if k in (curses.KEY_UP, ord('w')): sel = (sel - 1) % len(DIFF_ORDER)
        elif k in (curses.KEY_DOWN, ord('s')): sel = (sel + 1) % len(DIFF_ORDER)
        elif k in (ord(' '), ord('\n'), curses.KEY_ENTER): return DIFF_ORDER[sel]
        elif k in (ord('q'), 27): return None

def _game_over_screen(stdscr, score, wave, diff_label):
    stdscr.nodelay(False)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    lines = ["GAME OVER", f"Diff: {diff_label}", f"Wave: {wave}", f"Score: {score}", "", "R: Replay", "Q: Quit"]
    for i, line in enumerate(lines):
        _draw(stdscr, h//2 - 3 + i, max(0, w//2 - len(line)//2), line, curses.color_pair(C_HUD))
    stdscr.refresh()
    while True:
        k = stdscr.getch()
        if k in (ord('r'), ord('R')): return 'replay'
        if k in (ord('q'), ord('Q')): return 'quit'

def _draw_hud(win, score, wave, heat, hp, max_hp, wk, wg, diff_key, gun_locked):
    h, w = win.getmaxyx()
    _draw(win, 0, 0, '─' * w, curses.color_pair(C_DIM))
    _draw(win, 0, 1, f' SCORE:{score} ', curses.color_pair(C_HUD))
    _draw(win, 0, w//2 - 5, f' WAVE:{wave} ', curses.color_pair(C_WAVE))
    
    filled = int(10 * heat / HEAT_MAX)
    h_bar = '█' * filled + '░' * (10 - filled)
    h_col = C_DANGER if (heat > 75 or gun_locked) else C_WARN if heat > 45 else C_HUD
    _draw(win, 0, w - 25, f' HEAT: [{h_bar}]', curses.color_pair(h_col))

    _draw(win, h-1, 0, '─' * w, curses.color_pair(C_DIM))
    _draw(win, h-1, 1, ' HP: ' + '♥' * hp + ' ' * (max_hp - hp), curses.color_pair(C_DANGER))

# ── Game ──
def _run_game(stdscr, start_diff=None):
    _init_colors()
    diff_key = start_diff
    while True:
        if not diff_key:
            diff_key = _diff_screen(stdscr)
            if not diff_key: return

        cfg = DIFFICULTIES[diff_key]
        stdscr.nodelay(True)
        h, w = stdscr.getmaxyx()
        player = Player(w//2, h-3, cfg['armor'])
        bullets, enemies, drops = [], [], []
        score, wave, wave_kills, last_ts = 0, 1, 0, time.time()
        gun_locked = False

        while True:
            now = time.time()
            dt = min(now - last_ts, 0.1)
            last_ts = now
            h, w = stdscr.getmaxyx()

            key = stdscr.getch()
            if key == ord('q'): return

            # Player Logic
            mx = (1 if key in (curses.KEY_RIGHT, ord('d')) else -1 if key in (curses.KEY_LEFT, ord('a')) else 0)
            my = (1 if key in (curses.KEY_DOWN, ord('s')) else -1 if key in (curses.KEY_UP, ord('w')) else 0)
            player.x = max(2, min(w-3, player.x + mx * 0.5 * w * dt))
            player.y = max(h//2, min(h-3, player.y + my * 0.5 * h * dt))

            if key == ord(' ') and not gun_locked and player.shoot_cd <= 0:
                bullets.append(Bullet(player.x, player.y - 1, -cfg['bullet_spd'] * h * 1.5, char='|'))
                player.heat = min(HEAT_MAX, player.heat + cfg['heat_shot'])
                player.shoot_cd = cfg['shoot_cd']
            
            player.heat = max(0, player.heat - cfg['heat_cool'] * dt)
            if player.heat >= HEAT_MAX: gun_locked = True
            elif player.heat <= 0: gun_locked = False
            player.shoot_cd -= 1
            player.inv -= 1

            # Spawning
            wave_goal = cfg['wave_goal'].get(wave, 99)
            wave_types = cfg['wave_types'].get(wave, cfg['wave_types'][max(cfg['wave_types'].keys())])
            if random.random() < (dt / cfg['spawn_rate'].get(wave, 1)):
                enemies.append(Enemy(random.randint(5, w-6), h, random.choice(wave_types), cfg['enemy_spd']))

            # Update Enemies
            for e in enemies[:]:
                e.y += e.spd * dt
                if e.shoots:
                    if e.type == 'tank':
                        # Tank Heavy Shell
                        e.shoot_timer -= dt
                        if e.shoot_timer <= 0:
                            bullets.append(Bullet(e.x, e.y+1, 20, friendly=False, char='█'))
                            e.shoot_timer = random.uniform(3.0, 5.0)
                        # Tank Machine Gun
                        e.mg_timer -= dt
                        if e.mg_timer <= 0:
                            bullets.append(Bullet(e.x + random.uniform(-1, 1), e.y+1, 12, friendly=False, char='·'))
                            e.mg_timer = 0.2
                    else:
                        # Standard Shooter
                        e.shoot_timer -= dt
                        if e.shoot_timer <= 0:
                            bullets.append(Bullet(e.x, e.y+1, 15, friendly=False, char='•'))
                            e.shoot_timer = random.uniform(2, 4)

                if e.y >= h-2:
                    if e in enemies: enemies.remove(e)
                    if player.inv <= 0: player.hp -= 1; player.inv = cfg['inv_frames']

            # Update Drops (FIXED PHYSICS)
            for d in drops[:]:
                if not d.on_ground:
                    d.y += 0.2 # Fall speed
                    if d.y >= h-2:
                        d.y = h-2
                        d.on_ground = True
                else:
                    d.life -= dt # Only tick life when on ground
                
                if d.life <= 0:
                    drops.remove(d)
                elif abs(d.x - player.x) < 2 and abs(d.y - player.y) < 1.5:
                    if d.kind == 'R': 
                        player.hp = min(cfg['armor'], player.hp + 1)
                    drops.remove(d)

            # Update Bullets
            for b in bullets[:]:
                b.y += b.dy * dt
                if not (0 < b.y < h-1): 
                    if b in bullets: bullets.remove(b)
                    continue
                
                if b.friendly:
                    for e in enemies[:]:
                        h_dist, v_dist = (3, 2) if e.type == 'tank' else (2, 1)
                        if abs(b.x - e.x) <= h_dist and abs(b.y - e.y) <= v_dist:
                            e.hp -= 1
                            if b in bullets: bullets.remove(b)
                            if e.hp <= 0: 
                                if e in enemies: enemies.remove(e)
                                score += e.pts; wave_kills += 1
                                if random.random() < cfg['drop_r']: drops.append(Drop(e.x, e.y, 'R'))
                            break
                elif abs(b.y - player.y) < 1 and abs(b.x - player.x) < 1:
                    if player.inv <= 0: player.hp -= 1; player.inv = cfg['inv_frames']
                    if b in bullets: bullets.remove(b)

            if wave_kills >= wave_goal: wave += 1; wave_kills = 0
            if player.hp <= 0: break

            # Render
            stdscr.erase()
            
            for d in drops:
                _draw(stdscr, int(d.y), int(d.x), "✚", curses.color_pair(C_DROP_R))

            for b in bullets: 
                col = C_BULLET if b.friendly else C_EBULLET
                _draw(stdscr, int(b.y), int(b.x), b.char, curses.color_pair(col))
            
            for e in enemies:
                ey, ex, attr = int(e.y), int(e.x), curses.color_pair(ENEMY_COL_MAP[e.type])
                if e.type == 'fast':
                    _draw(stdscr, ey, ex-2, "_  _", attr)
                    _draw(stdscr, ey+1, ex-2, "└▀▀┘", attr)
                elif e.type == 'tank':
                    _draw(stdscr, ey-2, ex-2, " ___ ", attr)
                    _draw(stdscr, ey-1, ex-2, "║▛▀▜║", attr)
                    _draw(stdscr, ey,   ex-2, "║▌ ▐║", attr)
                    _draw(stdscr, ey+1, ex-2, "║▙▬▟║", attr)
                    _draw(stdscr, ey+2, ex-1, " ❙ ",  attr)
                else: 
                    _draw(stdscr, ey, ex, e.sym, attr)
            
            if player.inv <= 0 or (player.inv // 3) % 2 == 0:
                _draw(stdscr, int(player.y), int(player.x), '⊕', curses.color_pair(C_PLAYER))
            
            _draw_hud(stdscr, score, wave, player.heat, player.hp, cfg['armor'], wave_kills, wave_goal, diff_key, gun_locked)
            stdscr.refresh()
            time.sleep(max(0, TICK - (time.time() - now)))

        if _game_over_screen(stdscr, score, wave, cfg['label']) != 'replay': break

def main(args):
    if not args:
        start_diff = args[0].lower() if args and args[0].lower() in DIFFICULTIES else None
        curses.wrapper(_run_game, start_diff)
    elif "-h" in args or "--help" in args:
        print("""
DRONE GAME
Usage:
  drone_game [flags]

Flags:
  -h: this help section

Notes:
  A sad story about a modern soldier trapped by drones, enemies, and tanks
        """)
    else:
        print("drone_game: invalid parameters. See drone_game -h.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])