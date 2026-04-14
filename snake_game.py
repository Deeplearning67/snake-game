#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snake Game 贪吃蛇 — v1.0
A classic snake game built with Python + Pygame.
Supports bilingual Chinese/English UI, high score tracking, and cross-platform play.

Requirements: Python 3.8+, pygame 2.6+
Install: pip install pygame
Run: python snake_game.py
"""

import pygame
import random
import sys
import os

# ======================== Font Setup ========================
def _get_chinese_font(size):
    """Locate system Chinese font, return pygame.Font in priority order."""
    windir = os.environ.get('WINDIR', 'C:\\Windows')
    font_dir = os.path.join(windir, 'Fonts')
    candidates = [
        ('msyh.ttc',   'Microsoft YaHei'),
        ('simhei.ttf', 'SimHei'),
        ('simkai.ttf', 'KaiTi'),
        ('simsun.ttc', 'SimSun'),
    ]
    for fname, fname_zh in candidates:
        fpath = os.path.join(font_dir, fname)
        if os.path.exists(fpath):
            try:
                f = pygame.font.Font(fpath, size)
                f.render('\u6d4b', True, (0, 0, 0))   # test render
                print(f"[font] {fname_zh} ({fname}) OK")
                return f
            except Exception:
                pass
    return pygame.font.Font(None, size)   # fallback to system default

def _make_font(size):
    return _get_chinese_font(size)

# ======================== Game Constants ========================
BLOCK  = 20
COLS   = 30
ROWS   = 22
WIDTH  = COLS * BLOCK
HEIGHT = ROWS * BLOCK
FPS    = 8

DIRS = {
    'UP':    ( 0, -1),
    'DOWN':  ( 0,  1),
    'LEFT':  (-1,  0),
    'RIGHT': ( 1,  0),
}

COLOR_BG        = ( 10,  10,  25)
COLOR_GRID      = ( 50,  50,  90)
COLOR_SNAKE_H   = ( 60, 210, 100)
COLOR_SNAKE_B   = ( 30, 140,  60)
COLOR_FOOD      = (255,  80,  80)
COLOR_FOOD_GLOW = (255, 160,  80)
COLOR_SCORE     = (100, 220, 160)
COLOR_TITLE     = ( 80, 200, 255)
COLOR_GAMEOVER  = (255,  80,  80)
COLOR_PROMPT    = (160, 160, 200)
COLOR_BORDER    = ( 40,  40,  90)

# ======================== Helpers ========================
def gr(col, row):
    """Grid cell pygame.Rect (with 1px inner margin)."""
    return pygame.Rect(col * BLOCK + 1, row * BLOCK + 1, BLOCK - 2, BLOCK - 2)

def random_food(snake):
    """Generate food position that does not overlap the snake."""
    while True:
        c = random.randint(0, COLS - 1)
        r = random.randint(0, ROWS - 1)
        if (c, r) not in snake:
            return (c, r)

def draw_grid(surface):
    for r in range(ROWS + 1):
        pygame.draw.line(surface, COLOR_GRID, (0, r * BLOCK), (WIDTH, r * BLOCK), 1)
    for c in range(COLS + 1):
        pygame.draw.line(surface, COLOR_GRID, (c * BLOCK, 0), (c * BLOCK, HEIGHT), 1)

def draw_border(surface):
    pygame.draw.rect(surface, COLOR_BORDER, (0, 0, WIDTH, HEIGHT), 3)

def draw_snake(surface, snake, direction='RIGHT'):
    """Draw gradient snake body + animated head with eyes."""
    for i, (c, r) in enumerate(snake):
        shade = max(0.3, 1.0 - i / len(snake) * 0.6)
        col = (
            int(COLOR_SNAKE_B[0] * shade + 10),
            int(COLOR_SNAKE_B[1] * shade + 20),
            int(COLOR_SNAKE_B[2]),
        )
        pygame.draw.rect(surface, col, gr(c, r), border_radius=4)

    if not snake:
        return
    c, r = snake[0]
    pygame.draw.rect(surface, COLOR_SNAKE_H, gr(c, r), border_radius=5)

    # Eyes follow movement direction
    cx, cy = c * BLOCK + BLOCK // 2, r * BLOCK + BLOCK // 2
    eye_dir = DIRS.get(direction, DIRS['RIGHT'])
    ex, ey = eye_dir
    if ey != 0:   # vertical movement → eyes side by side
        pygame.draw.circle(surface, (255, 255, 255), (cx - 4, cy + ey * 3), 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 4, cy + ey * 3), 2)
    else:         # horizontal movement → eyes top and bottom
        pygame.draw.circle(surface, (255, 255, 255), (cx + ex * 3, cy - 4), 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx + ex * 3, cy + 4), 2)

def draw_food(surface, food, tick):
    """Draw pulsing food with glow effect."""
    c, r = food
    pulse = 0.85 + 0.15 * abs((tick % 40) / 20.0 - 1)
    size  = max(6, int((BLOCK - 4) * pulse))
    offset = (BLOCK - size) // 2
    x, y = c * BLOCK + offset, r * BLOCK + offset
    pygame.draw.rect(surface, COLOR_FOOD_GLOW, (x - 2, y - 2, size + 4, size + 4), border_radius=5)
    pygame.draw.rect(surface, COLOR_FOOD,       (x,     y,     size,     size    ), border_radius=4)

def draw_score_bar(surface, score, best, font_sm, font_md):
    bar = pygame.Surface((WIDTH, 34), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 150))
    surface.blit(bar, (0, 0))
    surface.blit(font_md.render(f'\u5f97\u5206: {score}', True, COLOR_SCORE), (10, 5))
    bs = font_sm.render(f'\u6700\u9ad8: {best}', True, COLOR_PROMPT)
    surface.blit(bs, (WIDTH - bs.get_width() - 10, 7))

def draw_start_screen(surface, ft, fm, fs):
    surface.fill(COLOR_BG)
    draw_grid(surface)
    draw_border(surface)
    title = ft.render('\u8d2a \u5403 \u86c7', True, COLOR_TITLE)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    sub = fm.render('SNAKE GAME', True, (60, 100, 160))
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 140))
    tips = [
        '\u2191 \u2193 \u2190 \u2192  \u63a7\u5236\u65b9\u5411',
        '\u7a7a\u683c\u952e   \u5f00\u59cb / \u6682\u505c',
        'R \u952e       \u91cd\u65b0\u5f00\u59cb',
        'ESC        \u9000\u51fa\u6e38\u620f',
    ]
    for i, tip in enumerate(tips):
        t = fs.render(tip, True, COLOR_PROMPT)
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 220 + i * 32))
    v = fs.render('v1.0  2026-04-14', True, (60, 60, 100))
    surface.blit(v, (WIDTH // 2 - v.get_width() // 2, HEIGHT - 30))

def draw_gameover_screen(surface, score, best, ft, fm, fs):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 20, 210))
    surface.blit(overlay, (0, 0))
    go = ft.render('\u6e38\u620f\u7ed3\u675f', True, COLOR_GAMEOVER)
    surface.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 90))
    sc = fm.render(f'\u672c\u5c40\u5f97\u5206: {score}', True, COLOR_SCORE)
    surface.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2 - 30))
    if score > 0 and score >= best:
        nb = fs.render('\u2605 \u65b0\u8bb0\u5f55! \u2605', True, (255, 220, 60))
        surface.blit(nb, (WIDTH // 2 - nb.get_width() // 2, HEIGHT // 2 + 5))
    bs = fs.render(f'\u5386\u53f2\u6700\u9ad8: {best}', True, COLOR_PROMPT)
    surface.blit(bs, (WIDTH // 2 - bs.get_width() // 2, HEIGHT // 2 + 42))
    for i, p in enumerate(['R \u91cd\u65b0\u5f00\u59cb', 'ESC \u9000\u51fa']):
        t = fs.render(p, True, COLOR_PROMPT)
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 + 85 + i * 30))

# ======================== Best Score Storage ========================
def _get_best_path():
    """Return the best-score file path, using a path near the script on failure."""
    for candidate in [
        os.environ.get('HOME', ''),
        os.environ.get('USERPROFILE', ''),
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
    ]:
        if candidate:
            p = os.path.join(candidate, 'snake_best.txt')
            try:
                open(p, 'a').close()
                return p
            except OSError:
                pass
    return os.path.join(os.getcwd(), 'snake_best.txt')

BEST_FILE = _get_best_path()

def load_best():
    try:
        with open(BEST_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_best(score):
    try:
        with open(BEST_FILE, 'w') as f:
            f.write(str(score))
    except Exception:
        pass

# ======================== Main ========================
def main():
    pygame.init()
    pygame.display.set_caption('\u8d2c\u5403\u86c7')   # 贪吃蛇
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()

    font_sm    = _make_font(18)
    font_md    = _make_font(26)
    font_title = _make_font(54)

    best = load_best()

    snake     = []
    direction = 'RIGHT'
    next_dir  = 'RIGHT'
    food      = (0, 0)
    score     = 0
    alive     = True
    paused    = False
    tick_count= 0
    speed     = FPS
    state     = 'START'

    def reset():
        nonlocal snake, direction, next_dir, food, score, alive, paused, tick_count, speed
        snake     = [(COLS//2, ROWS//2), (COLS//2-1, ROWS//2), (COLS//2-2, ROWS//2)]
        direction = 'RIGHT'
        next_dir  = 'RIGHT'
        food      = random_food(snake)
        score     = 0
        alive     = True
        paused    = False
        tick_count= 0
        speed     = FPS

    reset()
    running = True

    while running:
        clock.tick(60)
        tick_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if   state == 'START':    state = 'PLAYING'
                    elif state == 'GAMEOVER': reset(); state = 'PLAYING'
                    elif state == 'PLAYING':  state = 'PAUSED'
                    elif state == 'PAUSED':   state = 'PLAYING'
                continue

            if event.type != pygame.KEYDOWN:
                continue
            key = event.key

            if key == pygame.K_ESCAPE:
                running = False

            if key == pygame.K_r:
                if state in ('GAMEOVER', 'PLAYING', 'PAUSED'):
                    reset(); state = 'PLAYING'

            if key == pygame.K_SPACE:
                if   state == 'START':    state = 'PLAYING'
                elif state == 'PLAYING':   state = 'PAUSED'
                elif state == 'PAUSED':    state = 'PLAYING'

            if state == 'PLAYING' and alive:
                if key in (pygame.K_UP,   pygame.K_w) and direction != 'DOWN':
                    next_dir = 'UP'
                elif key in (pygame.K_DOWN,  pygame.K_s) and direction != 'UP':
                    next_dir = 'DOWN'
                elif key in (pygame.K_LEFT,  pygame.K_a) and direction != 'RIGHT':
                    next_dir = 'LEFT'
                elif key in (pygame.K_RIGHT, pygame.K_d) and direction != 'LEFT':
                    next_dir = 'RIGHT'

        # Logic tick
        if state == 'PLAYING' and alive and tick_count % max(1, 60 // speed) == 0:
            direction = next_dir
            dx, dy = DIRS[direction]
            hx, hy = snake[0][0] + dx, snake[0][1] + dy

            if not (0 <= hx < COLS and 0 <= hy < ROWS) or (hx, hy) in snake:
                alive = False
                state = 'GAMEOVER'
                if score > best:
                    best = score
                    save_best(best)
                continue

            snake.insert(0, (hx, hy))
            if (hx, hy) == food:
                score += 10
                food = random_food(snake)
                if score % 50 == 0 and speed < 18:
                    speed += 1
            else:
                snake.pop()

        # Render
        if state == 'START':
            draw_start_screen(screen, font_title, font_md, font_sm)
        else:
            screen.fill(COLOR_BG)
            draw_grid(screen)
            draw_border(screen)
            draw_food(screen, food, tick_count)
            draw_snake(screen, snake, direction)
            draw_score_bar(screen, score, best, font_sm, font_md)
            if state == 'PAUSED':
                ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                ov.fill((0, 0, 20, 160))
                screen.blit(ov, (0, 0))
                p  = font_title.render('\u5df2\u6682\u505c', True, (120, 200, 255))
                p2 = font_md.render('\u7a7a\u683c\u952e\u7ee7\u7eed', True, COLOR_PROMPT)
                screen.blit(p,  (WIDTH // 2 - p.get_width()  // 2, HEIGHT // 2 - 30))
                screen.blit(p2, (WIDTH // 2 - p2.get_width() // 2, HEIGHT // 2 + 20))
            if state == 'GAMEOVER':
                draw_gameover_screen(screen, score, best, font_title, font_md, font_sm)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
