# -*- coding: utf-8 -*-
"""
💖 Ultimate Romantic Birthday Particle Animation
终极浪漫生日粒子动画

功能：
✨ 银河粒子背景
🎂 粒子生日蛋糕
🕯️ 动态火焰
💖 爱心喷发
🎆 烟花爆炸
🌸 花瓣飘落
✨ 发光文字
🌌 流光拖尾
🎇 鼠标点击烟花
💞 粒子环绕

依赖：
pip install pygame numpy

运行：
python ultimate_romantic_birthday.py
"""

import pygame
import random
import math
import numpy as np

# =========================
# 初始化
# =========================
pygame.init()

WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Romantic Birthday")

clock = pygame.time.Clock()

# =========================
# 颜色
# =========================
BLACK = (5, 5, 15)

PINK = (255, 120, 180)
HOT_PINK = (255, 60, 150)
GOLD = (255, 220, 120)
BLUE = (120, 200, 255)
PURPLE = (200, 120, 255)
WHITE = (255, 255, 255)

CAKE1 = (255, 182, 193)
CAKE2 = (255, 160, 122)
CAKE3 = (255, 228, 181)

CREAM = (255, 250, 240)

# =========================
# 粒子类
# =========================
class Particle:

    def __init__(
        self,
        x,
        y,
        color,
        vx,
        vy,
        life,
        size,
        glow=True
    ):
        self.x = x
        self.y = y

        self.color = color

        self.vx = vx
        self.vy = vy

        self.life = life
        self.max_life = life

        self.size = size
        self.glow = glow

    def update(self):

        self.x += self.vx
        self.y += self.vy

        self.vy += 0.01

        self.life -= 1

    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = max(0, int(255 * self.life / self.max_life))

        if self.glow:

            glow_surface = pygame.Surface(
                (self.size * 8, self.size * 8),
                pygame.SRCALPHA
            )

            for i in range(3, 0, -1):

                radius = self.size * i

                pygame.draw.circle(
                    glow_surface,
                    (*self.color, alpha // (i * 2)),
                    (self.size * 4, self.size * 4),
                    radius
                )

            surface.blit(
                glow_surface,
                (self.x - self.size * 4,
                 self.y - self.size * 4)
            )

        else:

            pygame.draw.circle(
                surface,
                (*self.color, alpha),
                (int(self.x), int(self.y)),
                self.size
            )

# =========================
# 爱心粒子
# =========================
heart_particles = []

def spawn_heart(x, y):

    colors = [PINK, HOT_PINK, GOLD]

    for t in np.linspace(0, math.pi * 2, 120):

        hx = 16 * math.sin(t) ** 3

        hy = -(13 * math.cos(t)
               - 5 * math.cos(2 * t)
               - 2 * math.cos(3 * t)
               - math.cos(4 * t))

        scale = random.uniform(0.8, 1.5)

        vx = hx * 0.08 * scale
        vy = hy * 0.08 * scale

        heart_particles.append(
            Particle(
                x,
                y,
                random.choice(colors),
                vx,
                vy,
                random.randint(80, 140),
                random.randint(2, 5)
            )
        )

# =========================
# 烟花
# =========================
fireworks = []

def create_firework(x=None, y=None):

    if x is None:
        x = random.randint(200, WIDTH - 200)

    if y is None:
        y = random.randint(100, HEIGHT // 2)

    colors = [
        PINK,
        GOLD,
        BLUE,
        PURPLE,
        WHITE
    ]

    color = random.choice(colors)

    for _ in range(180):

        angle = random.uniform(0, math.pi * 2)

        speed = random.uniform(1, 8)

        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        fireworks.append(
            Particle(
                x,
                y,
                color,
                vx,
                vy,
                random.randint(60, 120),
                random.randint(2, 5)
            )
        )

# =========================
# 花瓣
# =========================
petals = []

def create_petal():

    x = random.randint(0, WIDTH)

    petals.append(
        Particle(
            x,
            -20,
            (255, 182, 193),
            random.uniform(-1, 1),
            random.uniform(1, 3),
            random.randint(250, 400),
            random.randint(3, 6),
            glow=False
        )
    )

# =========================
# 银河背景星星
# =========================
stars = []

for _ in range(250):

    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3),
        random.randint(100, 255)
    ])

# =========================
# 文字
# =========================
font_big = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 110)

font_small = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 48)

def glow_text(surface, text, font, x, y, color):

    # =========
    # Glow层
    # =========
    for radius in range(4, 0, -1):

        glow_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        glow_text_render = font.render(text, True, color)

        glow_text_render.set_alpha(18)

        # 多方向轻微偏移
        offsets = [
            (-radius, 0),
            (radius, 0),
            (0, -radius),
            (0, radius),

            (-radius // 2, -radius // 2),
            (radius // 2, radius // 2),
        ]

        for ox, oy in offsets:

            glow_surface.blit(
                glow_text_render,
                (x + ox, y + oy)
            )

        surface.blit(glow_surface, (0, 0))

    # =========
    # 清晰主体层
    # =========
    main_text = font.render(text, True, WHITE)

    surface.blit(main_text, (x, y))

# =========================
# 蛋糕
# =========================
def draw_cake(surface, t):

    cx = WIDTH // 2
    cy = HEIGHT // 2 + 140

    layers = [
        (380, 90, CAKE1),
        (290, 80, CAKE2),
        (210, 70, CAKE3)
    ]

    for i, (w, h, color) in enumerate(layers):

        ly = cy - i * 90

        for _ in range(450):

            px = random.randint(cx - w // 2, cx + w // 2)
            py = random.randint(ly - h // 2, ly + h // 2)

            offset = math.sin((px + t) * 0.04) * 2

            pygame.draw.circle(
                surface,
                color,
                (px, int(py + offset)),
                random.randint(1, 3)
            )

        # 奶油波浪
        for x in range(cx - w // 2, cx + w // 2, 10):

            yy = ly - h // 2 + math.sin((x + t) * 0.08) * 5

            pygame.draw.circle(
                surface,
                CREAM,
                (x, int(yy)),
                6
            )

    # 蜡烛
    candles = [-80, 0, 80]

    for dx in candles:

        x = cx + dx
        y = cy - 250

        pygame.draw.rect(surface, BLUE, (x - 5, y, 10, 60))

        flame_size = 12 + math.sin(t * 0.2 + dx) * 3

        pygame.draw.circle(
            surface,
            (255, 120, 0),
            (x, y - 10),
            int(flame_size)
        )

        pygame.draw.circle(
            surface,
            (255, 255, 180),
            (x, y - 14),
            int(flame_size * 0.6)
        )

# =========================
# 主循环
# =========================
running = True
timer = 0

while running:

    clock.tick(60)

    timer += 1

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # 鼠标点击烟花
        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = pygame.mouse.get_pos()

            create_firework(mx, my)
            spawn_heart(mx, my)

    # =====================
    # 背景拖尾
    # =====================
    fade = pygame.Surface((WIDTH, HEIGHT))

    fade.set_alpha(35)

    fade.fill(BLACK)

    screen.blit(fade, (0, 0))

    # =====================
    # 银河星空
    # =====================
    for s in stars:

        alpha = random.randint(100, 255)

        star_surface = pygame.Surface((8, 8), pygame.SRCALPHA)

        pygame.draw.circle(
            star_surface,
            (255, 255, 255, alpha),
            (4, 4),
            s[2]
        )

        screen.blit(star_surface, (s[0], s[1]))

    # =====================
    # 自动烟花
    # =====================
    if timer % 70 == 0:

        create_firework()

    # =====================
    # 自动爱心喷发
    # =====================
    if timer % 90 == 0:

        spawn_heart(WIDTH // 2, HEIGHT // 2 + 50)

    # =====================
    # 花瓣
    # =====================
    if random.random() < 0.35:

        create_petal()

    # =====================
    # 更新粒子
    # =====================
    particle_groups = [
        fireworks,
        heart_particles,
        petals
    ]

    for group in particle_groups:

        for p in group[:]:

            p.update()
            p.draw(screen)

            if p.life <= 0:
                group.remove(p)

    # =====================
    # 蛋糕
    # =====================
    draw_cake(screen, timer)

    # =====================
    # 发光标题
    # =====================
    title_y = 60 + math.sin(timer * 0.04) * 10

    glow_text(
        screen,
        "HAPPY BIRTHDAY",
        font_big,
        WIDTH // 2 - 410,
        int(title_y),
        GOLD
    )

    # =====================
    # 副标题
    # =====================
    sub_y = 180 + math.sin(timer * 0.03) * 6

    glow_text(
        screen,
        "愿所有美好如期而至",
        font_small,
        WIDTH // 2 - 280,
        int(sub_y),
        PINK
    )

    # =====================
    # 环绕粒子
    # =====================
    cx = WIDTH // 2
    cy = HEIGHT // 2 + 50

    for i in range(40):

        angle = timer * 0.01 + i * (math.pi * 2 / 40)

        rx = math.cos(angle) * 260
        ry = math.sin(angle) * 90

        pygame.draw.circle(
            screen,
            GOLD,
            (int(cx + rx), int(cy + ry)),
            2
        )

    pygame.display.flip()

pygame.quit()