#!/usr/bin/env python3
"""
代码雨表白 (Code Rain Confession)
Matrix 风格代码雨 → 汇聚成对方名字 → 浪漫揭示

运行: python3 code_rain.py [名字]
依赖: Python 内置 turtle（无需安装）
"""

import math
import random
import turtle
import sys
import time

# ═══════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════
W, H = 800, 600
BG_COLOR = "#000000"
RAIN_COLOR = "#00ff41"       # Matrix 绿
TARGET_COLOR = (255, 120, 150)  # 浪漫粉 (目标 RGB)
RAIN_DURATION = 6.0          # 代码雨持续秒数
PARTICLE_COUNT = 400         # 粒子数

# 字符集
CHARS = (
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "アイウエオカキクケコサシスセソタチツテト"
    "+-*/=<>[]{}|;:!@#$%^&"
)


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return tuple(int(_lerp(c1[i], c2[i], t)) for i in range(3))


def rand_char():
    return random.choice(CHARS)


# ═══════════════════════════════════════════
# 目标位置计算（网格拼字）
# ═══════════════════════════════════════════

def compute_targets(name, count):
    """
    将屏幕中心区域划分为 len(name) 个字符块，
    每个块内生成网格点作为目标位置。
    返回 [(x, y), ...] 共 count 个。
    """
    n = len(name)
    block_w = min(70, 320 // n)   # 每个字符块宽度
    spacing_x = block_w + 10      # 块间距
    total_w = n * spacing_x - 10
    start_x = -total_w / 2 + spacing_x / 2

    targets = []
    rows = max(8, count // (n * 12))
    cols = max(8, 12)

    for i in range(n):
        cx = start_x + i * spacing_x
        for row in range(rows):
            for col in range(cols):
                # 添加随机抖动让目标不是完美网格
                jx = random.uniform(-4, 4)
                jy = random.uniform(-4, 4)
                x = cx + (col - cols / 2) * 8 + jx
                y = (row - rows / 2) * 9 + jy
                targets.append((x, y))

    # 截断或补齐到 count
    if len(targets) > count:
        random.shuffle(targets)
        targets = targets[:count]
    elif len(targets) < count:
        # 在名字周围补充额外点
        extra_needed = count - len(targets)
        for _ in range(extra_needed):
            cx = random.choice([start_x + i * spacing_x for i in range(n)])
            targets.append((
                cx + random.uniform(-block_w / 2, block_w / 2),
                random.uniform(-rows * 4.5, rows * 4.5)
            ))

    return targets


# ═══════════════════════════════════════════
# 粒子类
# ═══════════════════════════════════════════

class Particle:
    __slots__ = ('x', 'y', 'tx', 'ty', 'vx', 'vy',
                 'fall_speed', 'char', 'char_timer',
                 'char_interval', 'brightness', 'font_size')

    def __init__(self):
        self.x = random.uniform(-W // 2, W // 2)
        self.y = random.uniform(-H // 2, H // 2 + 100)
        self.tx = 0.0
        self.ty = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.fall_speed = random.uniform(2.0, 6.0)
        self.char = rand_char()
        self.char_timer = random.random() * 20
        self.char_interval = random.uniform(8, 25)
        self.brightness = random.uniform(0.3, 1.0)
        self.font_size = random.randint(11, 17)


# ═══════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════

def code_rain(name, rain_sec=RAIN_DURATION):
    screen = turtle.Screen()
    screen.setup(W + 20, H + 20)
    screen.bgcolor(BG_COLOR)
    screen.title(f"💚 代码雨表白 · {name}")
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.penup()

    # 生成目标和粒子
    targets = compute_targets(name, PARTICLE_COUNT)
    particles = [Particle() for _ in range(PARTICLE_COUNT)]

    # 赋目标
    for p, (tx, ty) in zip(particles, targets):
        p.tx = tx
        p.ty = ty

    # 提示文字
    info_turtle = turtle.Turtle()
    info_turtle.hideturtle()
    info_turtle.speed(0)
    info_turtle.penup()
    info_turtle.color("#555555")
    info_turtle.goto(0, -H // 2 + 30)
    info_turtle.write("按 Enter 提前汇聚 · 按 R 重来 · 按 Q 退出",
                      align="center", font=("PingFang SC", 11, "normal"))

    # ── 阶段 ──
    STATE_RAIN = 0
    STATE_CONVERGE = 1
    STATE_FORMED = 2
    state = STATE_RAIN
    rain_start = time.time()
    converge_start = 0.0
    SPRING = 0.015
    DAMPING = 0.87
    running = True

    # ── 计时器 turtle（显示倒计时） ──
    timer_turtle = turtle.Turtle()
    timer_turtle.hideturtle()
    timer_turtle.speed(0)
    timer_turtle.penup()

    def draw_frame():
        nonlocal state, converge_start

        t.clear()
        timer_turtle.clear()

        now = time.time()

        # ── 雨阶段更新 ──
        if state == STATE_RAIN:
            elapsed = now - rain_start
            # 更新粒子
            for p in particles:
                p.y -= p.fall_speed
                if p.y < -H // 2 - 50:
                    p.y = H // 2 + random.randint(20, 100)
                    p.x = random.uniform(-W // 2, W // 2)
                p.x += random.uniform(-0.5, 0.5)
                if p.x < -W // 2:
                    p.x = W // 2
                if p.x > W // 2:
                    p.x = -W // 2
                p.char_timer += 0.8
                if p.char_timer > p.char_interval:
                    p.char_timer = 0
                    p.char = rand_char()

            # 倒计时
            remaining = max(0, rain_sec - elapsed)
            timer_turtle.goto(0, H // 2 - 30)
            timer_turtle.color("#004400")
            timer_turtle.write(f"代码雨 · {remaining:.1f}s",
                               align="center",
                               font=("Courier New", 13, "bold"))

            # 自动进入汇聚
            if elapsed >= rain_sec:
                state = STATE_CONVERGE
                converge_start = now

        # ── 汇聚阶段更新 ──
        elif state == STATE_CONVERGE:
            elapsed = now - converge_start
            for p in particles:
                dx = p.tx - p.x
                dy = p.ty - p.y
                p.vx += dx * SPRING
                p.vy += dy * SPRING
                p.vx *= DAMPING
                p.vy *= DAMPING
                p.x += p.vx
                p.y += p.vy
                # 字符逐步变成名字的字符
                if random.random() < 0.06:
                    p.char = random.choice(name)

            timer_turtle.goto(0, H // 2 - 30)
            timer_turtle.color("#884455")
            timer_turtle.write("汇聚中...", align="center",
                               font=("PingFang SC", 13, "bold"))

            # 判断是否稳定
            if elapsed > 2.0:
                stable = True
                for p in particles:
                    if abs(p.tx - p.x) > 2 or abs(p.ty - p.y) > 2:
                        stable = False
                        break
                if stable:
                    state = STATE_FORMED

        # ── 成形阶段 ──
        elif state == STATE_FORMED:
            # 轻微呼吸
            for p in particles:
                p.char = random.choice(name)
            timer_turtle.goto(0, H // 2 - 30)
            timer_turtle.color("#996666")
            timer_turtle.write(f"✨ {name} ✨", align="center",
                               font=("PingFang SC", 16, "bold"))

        # ── 绘制所有粒子 ──
        if state <= STATE_CONVERGE:
            color_mix = 0.0 if state == STATE_RAIN else min(1.0, (now - converge_start) / 2.5)
        else:
            color_mix = 1.0

        green = (0, 255, 65)
        pink = TARGET_COLOR

        for p in particles:
            if p.y < -H // 2 - 30 or p.y > H // 2 + 30:
                continue

            cr, cg, cb = _lerp_color(green, pink, color_mix)
            alpha = p.brightness
            r = int(cr * alpha)
            g = int(cg * alpha)
            b = int(cb * alpha)

            color_hex = f"#{min(255,r):02x}{min(255,g):02x}{min(255,b):02x}"
            t.goto(p.x, p.y)
            t.pencolor(color_hex)

            if phase := 2 if state == STATE_FORMED else (1 if state == STATE_CONVERGE else 0):
                if phase >= 1:
                    t.write(p.char, align="center",
                            font=("Courier New", p.font_size, "bold"))
                else:
                    t.write(p.char, align="center",
                            font=("Courier New", p.font_size, "normal"))
            else:
                t.write(p.char, align="center",
                        font=("Courier New", p.font_size, "normal"))

        # ── 成形后写名字光晕 ──
        if state == STATE_FORMED:
            # 光晕层
            glow_offsets = [(2, 0), (-2, 0), (0, 2), (0, -2),
                            (3, 1), (-3, 1), (3, -1), (-3, -1)]
            for ox, oy in glow_offsets:
                t.goto(ox, oy - 40)
                t.pencolor("#ff446688")
                t.write(name, align="center",
                        font=("PingFang SC", 48, "bold"))
            # 主体
            t.goto(0, -40)
            t.pencolor("#ffffff")
            t.write(name, align="center",
                    font=("PingFang SC", 48, "bold"))

            # 副标题
            t.goto(0, -95)
            t.pencolor("#cc8899")
            t.write("你的名字，是我见过最美的代码",
                    align="center",
                    font=("PingFang SC", 14, "normal"))

            # 心
            t.goto(0, -125)
            t.pencolor("#ff6688")
            t.write("❤️", align="center",
                    font=("PingFang SC", 22, "normal"))

        screen.update()

    # ── 键盘事件 ──
    def on_enter():
        nonlocal state, converge_start
        if state == STATE_RAIN:
            state = STATE_CONVERGE
            converge_start = time.time()

    def on_r():
        nonlocal state, rain_start
        # 重置
        state = STATE_RAIN
        rain_start = time.time()
        for p in particles:
            p.x = random.uniform(-W // 2, W // 2)
            p.y = random.uniform(-H // 2, H // 2 + 100)
            p.vx = p.vy = 0
            p.char = rand_char()

    def on_q():
        nonlocal running
        running = False
        screen.bye()

    screen.onkey(on_enter, "Return")
    screen.onkey(on_r, "r")
    screen.onkey(on_r, "R")
    screen.onkey(on_q, "q")
    screen.onkey(on_q, "Q")
    screen.listen()

    # ── 主循环 ──
    frame = 0
    while running:
        draw_frame()
        frame += 1

    # turtle 自己的 mainloop
    # screen.mainloop()  # 如果不用 bye()


# ═══════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════

USAGE = """💚 代码雨表白 · Code Rain Confession

用法:
  python3 code_rain.py             交互式输入名字
  python3 code_rain.py 张三         直接指定名字
  python3 code_rain.py 张三 8       名字 + 雨持续秒数
"""

if __name__ == '__main__':
    import sys

    name = None
    rain_sec = RAIN_DURATION

    if len(sys.argv) > 1:
        name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            rain_sec = float(sys.argv[2])
        except ValueError:
            print(USAGE)
            sys.exit(1)

    if name is None:
        name = input("💚 输入 TA 的名字: ").strip()
        if not name:
            print("名字不能为空哦～")
            sys.exit(1)

    print(f"💚 代码雨表白 · {name}")
    print(f"   代码雨持续 {rain_sec:.0f} 秒后自动汇聚")
    print(f"   按 Enter 提前汇聚 | R 重来 | Q 退出")
    code_rain(name, rain_sec)
