#!/usr/bin/env python3
"""
octuple: making your bugpy terminal fun since 2026
..which is really not very impressive considering it is currently 2026
"""

import curses
import random
import time
from collections import deque

# defining colors for curses

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1,  curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.init_pair(2,  curses.COLOR_WHITE,   -1)
    curses.init_pair(3,  curses.COLOR_GREEN,   -1)
    curses.init_pair(4,  curses.COLOR_RED,     -1)
    curses.init_pair(5,  curses.COLOR_YELLOW,  -1)
    curses.init_pair(6,  curses.COLOR_CYAN,    -1)
    curses.init_pair(7,  curses.COLOR_MAGENTA, -1)
    curses.init_pair(8,  curses.COLOR_WHITE,   curses.COLOR_BLUE)
    curses.init_pair(9,  curses.COLOR_BLACK,   curses.COLOR_YELLOW)
    curses.init_pair(10, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(11, curses.COLOR_BLACK,   curses.COLOR_RED)
    curses.init_pair(12, curses.COLOR_WHITE,   curses.COLOR_MAGENTA)
    curses.init_pair(13, curses.COLOR_BLACK,   curses.COLOR_CYAN)

# ─────────────────────────────────────────────────
# Cross-game utility functions
# ─────────────────────────────────────────────────

def center(win, row, text, attr=0):
    h, w = win.getmaxyx()
    col = max(0, (w - len(text)) // 2)
    try: win.addstr(row, col, text, attr)
    except curses.error: pass

def put(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try: win.addstr(y, x, text[:w - x], attr)
        except curses.error: pass

def wait_key(win, msg="Press any key…"):
    center(win, win.getmaxyx()[0] - 2, msg, curses.color_pair(5))
    win.refresh()
    win.nodelay(False)
    win.getch()

def game_over(win, score, msg="GAME OVER"):
    win.clear()
    h, w = win.getmaxyx()
    center(win, h // 2 - 2, msg,            curses.color_pair(4) | curses.A_BOLD)
    center(win, h // 2,     f"Score: {score}", curses.color_pair(5) | curses.A_BOLD)
    wait_key(win)

# ─────────────────────────────────────────────────
# 2048
# ─────────────────────────────────────────────────

def run_2048(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.keypad(True); stdscr.nodelay(False)

    def new_board():
        b = [[0]*4 for _ in range(4)]
        add_tile(b); add_tile(b); return b

    def add_tile(b):
        empty = [(r,c) for r in range(4) for c in range(4) if not b[r][c]]
        if empty:
            r,c = random.choice(empty)
            b[r][c] = 4 if random.random() < 0.1 else 2

    def compress(row):
        lst = [x for x in row if x]; s = 0; i = 0; out = []
        while i < len(lst):
            if i+1 < len(lst) and lst[i] == lst[i+1]:
                v = lst[i]*2; out.append(v); s += v; i += 2
            else: out.append(lst[i]); i += 1
        return out + [0]*(4-len(out)), s

    def move(b, d):
        total = 0; changed = False
        if d in ('left','right'):
            for r in range(4):
                row = b[r] if d=='left' else b[r][::-1]
                new, s = compress(row)
                if d=='right': new = new[::-1]
                if new != b[r]: changed = True
                b[r] = new; total += s
        else:
            for c in range(4):
                col = [b[r][c] for r in range(4)]
                if d=='down': col = col[::-1]
                new, s = compress(col)
                if d=='down': new = new[::-1]
                for r in range(4):
                    if b[r][c] != new[r]: changed = True
                    b[r][c] = new[r]
                total += s
        return changed, total

    def tcolor(v):
        if v >= 2048: return curses.color_pair(11)|curses.A_BOLD
        if v >= 256:  return curses.color_pair(8) |curses.A_BOLD
        if v >= 32:   return curses.color_pair(9)
        return curses.color_pair(10)

    def draw(b, score, best):
        stdscr.clear(); h,w = stdscr.getmaxyx()
        cw = 7; bw = 4*cw+1
        ox = max(0,(w-bw)//2); oy = max(0,(h-16)//2)
        put(stdscr, oy, ox, f" 2048  Score:{score:6d}  Best:{best:6d} ", curses.color_pair(12)|curses.A_BOLD)
        oy += 1
        for r in range(4):
            put(stdscr, oy+r*3, ox, "+"+("─"*(cw-1)+"+")*4, curses.color_pair(1))
            for c in range(4):
                v = b[r][c]
                cell = str(v).center(cw-1) if v else " "*(cw-1)
                put(stdscr, oy+r*3+1, ox+c*cw, "|", curses.color_pair(1))
                put(stdscr, oy+r*3+1, ox+c*cw+1, cell, tcolor(v) if v else curses.color_pair(1))
            put(stdscr, oy+r*3+1, ox+4*cw, "|", curses.color_pair(1))
        put(stdscr, oy+12, ox, "+"+("─"*(cw-1)+"+")*4, curses.color_pair(1))
        put(stdscr, oy+13, ox, "  ←↑↓→ move   R restart   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

    board = new_board(); score = 0; best = 0
    km = {curses.KEY_LEFT:'left', curses.KEY_RIGHT:'right',
          curses.KEY_UP:'up', curses.KEY_DOWN:'down',
          ord('a'):'left', ord('d'):'right', ord('w'):'up', ord('s'):'down'}
    while True:
        draw(board, score, best)
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (ord('r'),ord('R')): best=max(best,score); board=new_board(); score=0; continue
        if k in km:
            changed, pts = move(board, km[k])
            if changed:
                score += pts; add_tile(board)
                if not any(board[r][c]==0 for r in range(4) for c in range(4)):
                    can = any((r+1<4 and board[r+1][c]==board[r][c]) or
                              (c+1<4 and board[r][c+1]==board[r][c])
                              for r in range(4) for c in range(4))
                    if not can:
                        best=max(best,score); draw(board,score,best)
                        game_over(stdscr, score, "NO MOVES LEFT"); return

# ─────────────────────────────────────────────────
# SNAKE
# ─────────────────────────────────────────────────

def run_snake(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(True); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()
    bh, bw = h-4, min(w-2, 60)
    ox, oy = (w-bw)//2, 2

    def place_food(ss):
        while True:
            f = (random.randint(1,bh-2), random.randint(1,bw-2))
            if f not in ss: return f

    snake = deque([(bh//2, bw//2)]); sset = set(snake)
    direction = (0,1); pending = direction
    food = place_food(sset); score = 0; speed = 0.12
    kd = {curses.KEY_UP:(-1,0), curses.KEY_DOWN:(1,0),
          curses.KEY_LEFT:(0,-1), curses.KEY_RIGHT:(0,1),
          ord('w'):(-1,0), ord('s'):(1,0), ord('a'):(0,-1), ord('d'):(0,1)}
    last = time.time()
    while True:
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in kd:
            nd = kd[k]
            if nd[0]+direction[0] or nd[1]+direction[1]: pending = nd
        if time.time()-last < speed: continue
        last = time.time(); direction = pending
        head = (snake[0][0]+direction[0], snake[0][1]+direction[1])
        if not (0<head[0]<bh-1 and 0<head[1]<bw-1) or head in sset:
            game_over(stdscr, score); return
        snake.appendleft(head); sset.add(head)
        if head == food:
            score += 10; speed = max(0.04, speed-0.002); food = place_food(sset)
        else:
            tail = snake.pop(); sset.discard(tail)
        stdscr.clear()
        put(stdscr, 0, ox, f" SNAKE  Score: {score} ", curses.color_pair(12)|curses.A_BOLD)
        for r in range(bh):
            for c in range(bw):
                ch = ('+'if(r in(0,bh-1))and(c in(0,bw-1))else
                      '─'if r in(0,bh-1) else '│'if c in(0,bw-1) else ' ')
                put(stdscr, oy+r, ox+c, ch, curses.color_pair(7))
        for seg in list(snake)[1:]: put(stdscr, oy+seg[0], ox+seg[1], '▪', curses.color_pair(3))
        put(stdscr, oy+snake[0][0], ox+snake[0][1], '◉', curses.color_pair(3)|curses.A_BOLD)
        put(stdscr, oy+food[0], ox+food[1], '●', curses.color_pair(4)|curses.A_BOLD)
        put(stdscr, oy+bh+1, ox, "  WASD/arrows move   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

# ─────────────────────────────────────────────────
# DINO RUN
# ─────────────────────────────────────────────────

def run_dino(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(True); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()
    GR = h-5; DC = 6
    dy = GR; vy = 0; duck = False
    obs = []; score = 0; speed = 0.07; last = time.time(); frame = 0

    while True:
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (ord(' '),curses.KEY_UP,ord('w')) and dy==GR: vy = -2
        duck = k in (ord('s'),curses.KEY_DOWN)

        if time.time()-last < speed: continue
        last = time.time(); frame += 1; score += 1

        dy += vy; vy = min(vy+1, 2)
        if dy >= GR: dy = GR; vy = 0

        if not obs or obs[-1][0] < w - random.randint(20,40):
            obs.append([w-2, random.choice([1,2])])
        obs = [[c-2,ht] for c,ht in obs if c>2]

        dh = 1 if duck else 2
        dead = False
        for oc, oh in obs:
            if oc in range(DC-1, DC+2):
                for ro in range(oh):
                    for dr in range(dh):
                        if GR-ro == dy-dr: dead = True
        if dead: game_over(stdscr, score); return

        speed = max(0.03, 0.07 - score*0.00003)
        stdscr.clear()
        put(stdscr, 0, 2, f" DINO RUN  Score: {score} ", curses.color_pair(12)|curses.A_BOLD)
        put(stdscr, GR+1, 0, '─'*(w-1), curses.color_pair(3))
        if duck:
            put(stdscr, GR, DC-1, '<▬>', curses.color_pair(6)|curses.A_BOLD)
        else:
            put(stdscr, dy-1, DC, 'Ö', curses.color_pair(6)|curses.A_BOLD)
            put(stdscr, dy,   DC-1, '[█]', curses.color_pair(6))
        for oc, oh in obs:
            for ro in range(oh):
                put(stdscr, GR-ro, oc, '▲' if ro==oh-1 else '█', curses.color_pair(4)|curses.A_BOLD)
        cp = (w-(frame)%w)%w
        put(stdscr, 3, cp%(w-5), '~≈~', curses.color_pair(2))
        put(stdscr, 5, (cp+w//3)%(w-5), '≈~≈', curses.color_pair(2))
        put(stdscr, h-2, 2, "  SPACE/↑ jump   ↓/S duck   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

# ─────────────────────────────────────────────────
# GOLD RUN
# ─────────────────────────────────────────────────

def run_gold(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(True); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()
    lane_rows = [h//4, h//2, 3*h//4]
    PC = 8; target = 1; anim_y = lane_rows[1]
    objects = []; score = 0; dist = 0; speed = 0.07; last = time.time(); frame = 0

    while True:
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (curses.KEY_UP,ord('w')) and target>0: target -= 1
        if k in (curses.KEY_DOWN,ord('s')) and target<2: target += 1
        if time.time()-last < speed: continue
        last = time.time(); frame += 1; dist += 1

        ty = lane_rows[target]
        if anim_y < ty: anim_y = min(anim_y+2, ty)
        elif anim_y > ty: anim_y = max(anim_y-2, ty)
        cur_lane = min(range(3), key=lambda i: abs(lane_rows[i]-anim_y))

        if not objects or objects[-1][0] < w-random.randint(15,30):
            objects.append([w-2, random.randint(0,2), 'coin' if random.random()<0.4 else 'obs'])
        objects = [[c-2,l,t] for c,l,t in objects if c>1]

        for obj in objects:
            if abs(obj[0]-PC)<=1 and obj[1]==cur_lane:
                if obj[2]=='obs': game_over(stdscr, score); return
                elif obj[2]=='coin': score += 10; obj[0] = -99

        speed = max(0.03, 0.07-dist*0.000025)
        stdscr.clear()
        put(stdscr, 0, 2, f" GOLD RUN  Score:{score}  Dist:{dist} ", curses.color_pair(12)|curses.A_BOLD)
        for lr in lane_rows:
            put(stdscr, lr+1, 0, '·'*(w-1), curses.color_pair(2))
        for oc, ol, ot in objects:
            row = lane_rows[ol]
            if ot=='coin': put(stdscr, row, oc, '¢', curses.color_pair(5)|curses.A_BOLD)
            else:
                put(stdscr, row-1, oc, '▄', curses.color_pair(4))
                put(stdscr, row,   oc, '█', curses.color_pair(4)|curses.A_BOLD)
        put(stdscr, anim_y-1, PC-1, '\\O/', curses.color_pair(6)|curses.A_BOLD)
        put(stdscr, anim_y,   PC,   '|',    curses.color_pair(6))
        put(stdscr, anim_y+1, PC-1, '/ \\', curses.color_pair(6))
        put(stdscr, h-2, 2, "  ↑/W ↓/S switch lanes   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

# ─────────────────────────────────────────────────
# TETRIS
# ─────────────────────────────────────────────────

def run_tetris(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(True); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()
    BW, BH = 10, 20
    ox = max(0,(w-BW*2-14)//2); oy = max(0,(h-BH-3)//2)

    PIECES = [[[1,1,1,1]],[[1,1],[1,1]],[[0,1,0],[1,1,1]],
              [[1,0],[1,0],[1,1]],[[0,1],[0,1],[1,1]],
              [[0,1,1],[1,1,0]],[[1,1,0],[0,1,1]]]
    COLORS = [6,5,7,4,8,3,9]

    def rot(p): return [list(r) for r in zip(*p[::-1])]
    def valid(b,p,px,py):
        for r,row in enumerate(p):
            for c,v in enumerate(row):
                if v:
                    nr,nc = py+r, px+c
                    if nr<0 or nr>=BH or nc<0 or nc>=BW or b[nr][nc]: return False
        return True
    def place(b,p,px,py,col):
        for r,row in enumerate(p):
            for c,v in enumerate(row):
                if v: b[py+r][px+c] = col
    def clear_lines(b):
        new = [row for row in b if any(c==0 for c in row)]
        cl = BH-len(new); b[:] = [[0]*BW]*cl + new; return cl
    def new_piece():
        i = random.randrange(7)
        return [r[:] for r in PIECES[i]], COLORS[i]

    board = [[0]*BW for _ in range(BH)]
    piece,color = new_piece(); nxt,nc = new_piece()
    px,py = BW//2-len(piece[0])//2, 0
    score=0; level=1; lines=0; di=0.5; last_drop=time.time()
    st = [0,100,300,500,800]

    def land():
        nonlocal piece,color,nxt,nc,px,py,score,level,lines,di
        place(board,piece,px,py,color)
        cl = clear_lines(board); lines+=cl; score+=st[min(cl,4)]
        level=lines//10+1; di=max(0.1,0.5-(level-1)*0.04)
        piece,color=nxt,nc; nxt,nc=new_piece()
        px,py=BW//2-len(piece[0])//2,0
        if not valid(board,piece,px,py): game_over(stdscr,score); return False
        return True

    while True:
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (curses.KEY_LEFT,ord('a')):
            if valid(board,piece,px-1,py): px-=1
        elif k in (curses.KEY_RIGHT,ord('d')):
            if valid(board,piece,px+1,py): px+=1
        elif k in (curses.KEY_UP,ord('w')):
            r=rot(piece)
            if valid(board,r,px,py): piece=r
        elif k in (curses.KEY_DOWN,ord('s')):
            if valid(board,piece,px,py+1): py+=1
            elif not land(): return
        elif k==ord(' '):
            while valid(board,piece,px,py+1): py+=1
            if not land(): return

        if time.time()-last_drop >= di:
            last_drop=time.time()
            if valid(board,piece,px,py+1): py+=1
            elif not land(): return

        gy=py
        while valid(board,piece,px,gy+1): gy+=1
        stdscr.clear()
        put(stdscr, oy, ox, f" TETRIS  Lv:{level} ", curses.color_pair(12)|curses.A_BOLD)
        put(stdscr, oy, ox, '┌'+'─'*(BW*2)+'┐', curses.color_pair(7))
        put(stdscr, oy+BH+1, ox, '└'+'─'*(BW*2)+'┘', curses.color_pair(7))
        for r in range(BH):
            put(stdscr, oy+1+r, ox, '│', curses.color_pair(7))
            put(stdscr, oy+1+r, ox+BW*2+1, '│', curses.color_pair(7))
            for c in range(BW):
                v=board[r][c]
                put(stdscr, oy+1+r, ox+1+c*2, '██' if v else '  ', curses.color_pair(v) if v else curses.color_pair(2))
        for r,row in enumerate(piece):
            for c,v in enumerate(row):
                if v:
                    put(stdscr, oy+1+gy+r, ox+1+(px+c)*2, '░░', curses.color_pair(color))
                    put(stdscr, oy+1+py+r, ox+1+(px+c)*2, '██', curses.color_pair(color)|curses.A_BOLD)
        sx=ox+BW*2+3
        put(stdscr, oy+1, sx, f"Score", curses.color_pair(5))
        put(stdscr, oy+2, sx, f"{score}", curses.color_pair(5)|curses.A_BOLD)
        put(stdscr, oy+4, sx, f"Lines:{lines}", curses.color_pair(2))
        put(stdscr, oy+5, sx, f"Level:{level}", curses.color_pair(2))
        put(stdscr, oy+7, sx, "Next:", curses.color_pair(2))
        for r,row in enumerate(nxt):
            for c,v in enumerate(row):
                if v: put(stdscr, oy+8+r, sx+c*2, '██', curses.color_pair(nc))
        put(stdscr, oy+BH+2, ox, " ←→ move  ↑ rotate  ↓ soft  SPC hard  Q quit ", curses.color_pair(2))
        stdscr.refresh()

# ─────────────────────────────────────────────────
# FLAPPY BIRD
# ─────────────────────────────────────────────────

def run_flappy(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(True); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()
    GAP=8; PW=3; bc=w//5; by=h//2; vy=0
    pipes=[]; score=0; speed=0.06; last=time.time(); frame=0; started=False
    pipes.append([w-1, random.randint(3,h-GAP-4)])

    while True:
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (ord(' '),curses.KEY_UP,ord('w')): vy=-2; started=True
        if time.time()-last < speed: continue
        last=time.time(); frame+=1
        if started:
            vy=min(vy+1,3); by+=vy
            pipes=[[c-1,t] for c,t in pipes if c>0]
            if not pipes or pipes[-1][0]<w-random.randint(25,40):
                pipes.append([w-1, random.randint(3,h-GAP-4)])
        for p in pipes:
            if p[0]==bc: score+=1
        for pc,pt in pipes:
            if abs(pc-bc)<=1 and (by<=pt or by>=pt+GAP):
                game_over(stdscr,score); return
        if by<=0 or by>=h-2: game_over(stdscr,score); return
        stdscr.clear()
        put(stdscr, 0, 2, f" FLAPPY BIRD  Score: {score} ", curses.color_pair(12)|curses.A_BOLD)
        for pc,pt in pipes:
            for r in range(1,h-1):
                if r<pt or r>=pt+GAP:
                    for dc in range(PW):
                        col=pc+dc-1
                        if 0<=col<w: put(stdscr,r,col,'█',curses.color_pair(3))
            for dc in range(PW):
                col=pc+dc-1
                if 0<=col<w:
                    if 0<pt-1<h:    put(stdscr,pt-1,col,'▄',curses.color_pair(3)|curses.A_BOLD)
                    if 0<pt+GAP<h:  put(stdscr,pt+GAP,col,'▀',curses.color_pair(3)|curses.A_BOLD)
        put(stdscr, by, bc, ['>','≥'][frame%2]+'●', curses.color_pair(5)|curses.A_BOLD)
        put(stdscr, h-2, 0, '▄'*(w-1), curses.color_pair(3))
        if not started: center(stdscr, h//2+3, "SPACE / ↑ to flap!", curses.color_pair(5)|curses.A_BOLD)
        put(stdscr, h-1, 2, "  SPACE/↑ flap   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

# ─────────────────────────────────────────────────
# BREAKOUT
# ─────────────────────────────────────────────────

def run_breakout(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(True); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()

    PAD_W = 7
    BRICK_ROWS = 5
    BRICK_COLS = (w - 4) // 4
    BRICK_COLORS = [4, 7, 5, 3, 6]

    def new_bricks():
        return [[True]*BRICK_COLS for _ in range(BRICK_ROWS)]

    def draw_all():
        stdscr.clear()
        put(stdscr, 0, 2, f" BREAKOUT  Score:{score}  Lives:{lives} ", curses.color_pair(12)|curses.A_BOLD)
        for r in range(BRICK_ROWS):
            for c in range(BRICK_COLS):
                if bricks[r][c]:
                    put(stdscr, 2+r, 2+c*4, '▐██▌', curses.color_pair(BRICK_COLORS[r])|curses.A_BOLD)
        # paddle
        put(stdscr, h-3, pad_x, '▀'*PAD_W, curses.color_pair(6)|curses.A_BOLD)
        # ball
        put(stdscr, int(ball_y), int(ball_x), '●', curses.color_pair(5)|curses.A_BOLD)
        put(stdscr, h-1, 2, "  ←/A  →/D move paddle   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

    bricks = new_bricks()
    pad_x = w//2 - PAD_W//2
    ball_x = float(w//2); ball_y = float(h-5)
    bdx = 1.0; bdy = -1.0
    score = 0; lives = 3; speed = 0.04; last = time.time()

    while True:
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (curses.KEY_LEFT,  ord('a')): pad_x = max(1, pad_x-4)
        if k in (curses.KEY_RIGHT, ord('d')): pad_x = min(w-PAD_W-4, pad_x+4)

        if time.time()-last < speed: continue
        last = time.time()

        ball_x += bdx; ball_y += bdy

        # wall bounce
        if ball_x <= 1:        ball_x = 1;      bdx = abs(bdx)
        if ball_x >= w-2:      ball_x = w-2;    bdx = -abs(bdx)
        if ball_y <= 1:        ball_y = 1;       bdy = abs(bdy)

        # paddle bounce
        if int(ball_y) == h-3 and pad_x <= int(ball_x) <= pad_x+PAD_W:
            bdy = -abs(bdy)
            # angle based on hit position
            offset = int(ball_x) - (pad_x + PAD_W//2)
            bdx = offset * 0.4 if offset != 0 else bdx

        # fell below
        if ball_y >= h-1:
            lives -= 1
            if lives <= 0: game_over(stdscr, score); return
            ball_x = float(pad_x + PAD_W//2); ball_y = float(h-5)
            bdx = 1.0; bdy = -1.0

        # brick collision
        br = int(ball_y) - 2
        bc_idx = (int(ball_x) - 2) // 4
        if 0 <= br < BRICK_ROWS and 0 <= bc_idx < BRICK_COLS and bricks[br][bc_idx]:
            bricks[br][bc_idx] = False; bdy = -bdy
            score += (BRICK_ROWS - br) * 10

        # cleared all bricks
        if not any(bricks[r][c] for r in range(BRICK_ROWS) for c in range(BRICK_COLS)):
            bricks = new_bricks(); speed = max(0.02, speed-0.005); score += 200

        draw_all()

# ─────────────────────────────────────────────────
# MINESWEEPER
# ─────────────────────────────────────────────────

def run_minesweeper(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.nodelay(False); stdscr.keypad(True)
    h, w = stdscr.getmaxyx()

    COLS, ROWS = min(20, (w-4)//3), min(14, h-6)
    MINES = (ROWS*COLS)//6

    def new_game():
        mines = set()
        while len(mines) < MINES:
            mines.add((random.randint(0,ROWS-1), random.randint(0,COLS-1)))
        counts = [[0]*COLS for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                if (r,c) not in mines:
                    counts[r][c] = sum(1 for dr in(-1,0,1) for dc in(-1,0,1)
                                       if (r+dr,c+dc) in mines)
        return mines, counts, [[False]*COLS for _ in range(ROWS)], [[False]*COLS for _ in range(ROWS)]

    def reveal(r,c, revealed, counts, mines):
        if not (0<=r<ROWS and 0<=c<COLS) or revealed[r][c]: return
        revealed[r][c] = True
        if counts[r][c] == 0 and (r,c) not in mines:
            for dr in(-1,0,1):
                for dc in(-1,0,1): reveal(r+dr,c+dc,revealed,counts,mines)

    mines, counts, revealed, flagged = new_game()
    cr, cc = 0, 0; score = 0; won = False

    NUM_COLORS = [0,3,6,4,8,4,6,7,2]

    while True:
        stdscr.clear()
        put(stdscr, 0, 2, f" MINESWEEPER  Mines:{MINES}  Flagged:{sum(flagged[r][c] for r in range(ROWS) for c in range(COLS))} ",
            curses.color_pair(12)|curses.A_BOLD)

        for r in range(ROWS):
            for c in range(COLS):
                x = 2 + c*3; y = 2 + r
                is_cur = (r==cr and c==cc)
                if revealed[r][c]:
                    if (r,c) in mines:
                        put(stdscr, y, x, ' * ', curses.color_pair(4)|curses.A_BOLD)
                    else:
                        n = counts[r][c]
                        ch = f' {n} ' if n else '   '
                        attr = curses.color_pair(NUM_COLORS[n])|curses.A_BOLD if n else curses.color_pair(2)
                        put(stdscr, y, x, ch, attr)
                elif flagged[r][c]:
                    attr = curses.color_pair(5)|curses.A_BOLD
                    if is_cur: attr |= curses.A_REVERSE
                    put(stdscr, y, x, ' F ', attr)
                else:
                    attr = curses.color_pair(1)
                    if is_cur: attr = curses.color_pair(13)|curses.A_BOLD
                    put(stdscr, y, x, '[ ]', attr)

        if won:
            center(stdscr, h-3, "YOU WIN! 🎉", curses.color_pair(3)|curses.A_BOLD)
        put(stdscr, h-2, 2, "  arrows move   ENTER reveal   F flag   R restart   Q quit  ", curses.color_pair(2))
        stdscr.refresh()

        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k in (ord('r'),ord('R')): mines,counts,revealed,flagged=new_game(); cr=cc=0; won=False; continue
        if won: continue
        if k == curses.KEY_UP    and cr>0: cr-=1
        if k == curses.KEY_DOWN  and cr<ROWS-1: cr+=1
        if k == curses.KEY_LEFT  and cc>0: cc-=1
        if k == curses.KEY_RIGHT and cc<COLS-1: cc+=1
        if k in (ord('f'),ord('F')) and not revealed[cr][cc]:
            flagged[cr][cc] = not flagged[cr][cc]
        if k in (curses.KEY_ENTER,10,13) and not flagged[cr][cc] and not revealed[cr][cc]:
            if (cr,cc) in mines:
                # reveal all mines
                for r,c in mines: revealed[r][c]=True
                stdscr.clear()
                put(stdscr, 0, 2, " MINESWEEPER ", curses.color_pair(12)|curses.A_BOLD)
                for r in range(ROWS):
                    for c in range(COLS):
                        x=2+c*3; y=2+r
                        if (r,c) in mines: put(stdscr,y,x,' * ',curses.color_pair(4)|curses.A_BOLD)
                        elif revealed[r][c]:
                            n=counts[r][c]; ch=f' {n} ' if n else '   '
                            put(stdscr,y,x,ch,curses.color_pair(NUM_COLORS[n]) if n else curses.color_pair(2))
                        else: put(stdscr,y,x,'[ ]',curses.color_pair(1))
                game_over(stdscr, score, "BOOM! 💥"); return
            else:
                reveal(cr,cc,revealed,counts,mines)
                score += 10
                safe = ROWS*COLS - MINES
                if sum(revealed[r][c] for r in range(ROWS) for c in range(COLS)) >= safe:
                    won = True

# now we should actually make a way to select games, shouldn't we

GAMES = [
    ("2048",        run_2048),
    ("Snake",       run_snake),
    ("Dino Run",    run_dino),
    ("Gold Run",    run_gold),
    ("Tetris",      run_tetris),
    ("Flappy Bird", run_flappy),
    ("Breakout",    run_breakout),
    ("Minesweeper", run_minesweeper),
]

BANNER = r"""
             _               _      
            | |             | |     
   ___   ___| |_ _   _ _ __ | | ___ 
  / _ \ / __| __| | | | '_ \| |/ _ \
 | (_) | (__| |_| |_| | |_) | |  __/
  \___/ \___|\__|\__,_| .__/|_|\___|
                      | |           
                      |_|           
"""

def run_menu(stdscr):
    curses.curs_set(0); init_colors()
    stdscr.keypad(True); stdscr.nodelay(False)
    sel = 0
    while True:
        stdscr.clear(); h, w = stdscr.getmaxyx()
        lines = [l for l in BANNER.split('\n') if l.strip()]
        sr = max(1, (h - len(lines) - len(GAMES) - 5) // 2)
        for i, line in enumerate(lines):
            center(stdscr, sr+i, line, curses.color_pair(5)|curses.A_BOLD)
        mt = sr + len(lines) + 1
        for i, (name, _) in enumerate(GAMES):
            label = f"  {'▶' if i==sel else ' '}  {name:<18}  "
            center(stdscr, mt+i, label,
                   curses.color_pair(13)|curses.A_BOLD if i==sel else curses.color_pair(2))
        center(stdscr, mt+len(GAMES)+1, "↑ ↓  navigate    ENTER  play    Q  quit", curses.color_pair(7))
        stdscr.refresh()
        k = stdscr.getch()
        if k in (ord('q'),ord('Q')): break
        if k == curses.KEY_UP:   sel = (sel-1) % len(GAMES)
        if k == curses.KEY_DOWN: sel = (sel+1) % len(GAMES)
        if k in (curses.KEY_ENTER,10,13):
            try: GAMES[sel][1](stdscr)
            except Exception as e:
                stdscr.clear()
                center(stdscr, stdscr.getmaxyx()[0]//2, f"Error: {e}", curses.color_pair(4))
                wait_key(stdscr)

# Prep to run script, plus provide help args per p7mj's standard...

def main(args=None):
    if args and ("-h" in args or "--help" in args):
        print("""
OCTUPLE
Usage:
  octuple [flags]

Flags:
  -h: this help section

Notes:
  A collection of 8 minigames to appease your endless boredom.
  Games: 2048, Snake, Dino Run, Gold Run, Tetris, Flappy Bird, Breakout, Minesweeper.
  Navigate the menu with arrow keys, select with ENTER, quit any game with Q.
""")
        return
    curses.wrapper(run_menu)

if __name__ == "__main__":
    main()