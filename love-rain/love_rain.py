#!/usr/bin/env python3
"""
🌸 cmatrix --love · Love Rain
黑客帝国风格，但下落的是 ❤️🌸💕，而不是绿色数字

运行: python3 love_rain.py
依赖: Python 内置 turtle（无需安装）
"""

import math
import random
import turtle
import time

# ═══════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════
W, H = 800, 600
BG_COLOR = "#0a0410"
PARTICLE_COUNT = 180

# ═══════════════════════════════════════════
# 模式
# ═══════════════════════════════════════════
MODES = [
    ("💕 全模式",  ["❤️","💕","💗","💖","💝","💘","💓","💞","🩷",
                    "🌸","🌺","🌷","🌹","💐","✨","💫","🦋","🎀","💌","🤍"]),
    ("❤️ 红心",   ["❤️","💕","💗","💖","💝","💘","💓","💞","🩷","♥","❣","💟"]),
    ("🌸 花雨",   ["🌸","🌺","🌷","🌹","🌼","🌻","💐","✿","❀","🏵️","💮"]),
    ("✨ 星尘",   ["✨","⭐","🌟","💫","✧","✦","⭑","♪"]),
    ("🩷 粉彩",   ["🩷","💗","💖","🌸","💝","🎀","💕","💓","💞"]),
]

# ═══════════════════════════════════════════
# 粒子类
# ═══════════════════════════════════════════

class LoveParticle:
    __slots__ = ('x','y','vx','vy','emoji','size',
                 'sway_amp','sway_freq','sway_phase',
                 'rotation','rot_speed','opacity','from_burst','life')

    def __init__(self, x=None, y=None, from_burst=False, emojis=None):
        self.reset(x, y, from_burst, emojis)

    def reset(self, x=None, y=None, from_burst=False, emojis=None):
        if emojis is None:
            emojis = MODES[0][1]
        self.x = x if x is not None else random.uniform(-W//2, W//2)
        self.y = y if y is not None else random.uniform(H//2, H//2 + 200)
        speed = random.uniform(0.3, 1.5)
        self.vy = -speed * (0.3 if from_burst else 1.0)
        self.vx = random.uniform(-0.4, 0.4)
        self.emoji = random.choice(emojis)
        self.size = random.randint(14, 36)
        self.sway_amp = random.uniform(0.5, 3.0)
        self.sway_freq = random.uniform(0.02, 0.06)
        self.sway_phase = random.random() * math.pi * 2
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2.0, 2.0)
        self.opacity = 1.0
        self.from_burst = from_burst
        self.life = 1.0

    def update(self):
        self.sway_phase += self.sway_freq
        self.x += self.vx + math.sin(self.sway_phase) * self.sway_amp * 0.3
        self.y += self.vy
        self.rotation += self.rot_speed

        if self.from_burst:
            self.life -= 0.015
            self.vy -= 0.005  # 微重力向下
            self.opacity *= 0.99

        margin = 50
        return not (self.y < -H//2 - margin or self.y > H//2 + margin or
                    self.x < -W//2 - margin or self.x > W//2 + margin or
                    self.life <= 0)


# ═══════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════

def love_rain():
    screen = turtle.Screen()
    screen.setup(W + 20, H + 20)
    screen.bgcolor(BG_COLOR)
    screen.title("💕 cmatrix --love · Love Rain")
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.penup()

    mode_idx = 0
    particles = []
    bursts = []

    def get_emojis():
        return MODES[mode_idx][1]

    # 初始化
    for _ in range(PARTICLE_COUNT):
        p = LoveParticle(
            x=random.uniform(-W//2, W//2),
            y=random.uniform(-H//2, H//2),
            emojis=get_emojis()
        )
        particles.append(p)

    # 底部提示
    hint = turtle.Turtle()
    hint.hideturtle()
    hint.speed(0)
    hint.penup()
    hint.color("#555")
    hint.goto(0, -H//2 + 25)
    hint.write("🖱️ 点击绽放心动 · 空格切换模式 · Q 退出",
               align="center", font=("PingFang SC", 11, "normal"))

    # 模式显示
    mode_display = turtle.Turtle()
    mode_display.hideturtle()
    mode_display.speed(0)
    mode_display.penup()

    def update_mode_display():
        mode_display.clear()
        mode_display.goto(0, H//2 - 35)
        mode_display.color("#885566")
        mode_display.write(MODES[mode_idx][0], align="center",
                           font=("PingFang SC", 16, "bold"))

    update_mode_display()

    # 计数
    burst_count = [0]
    count_display = turtle.Turtle()
    count_display.hideturtle()
    count_display.speed(0)
    count_display.penup()

    running = True

    # ── 绘制一帧 ──
    def draw_frame():
        t.clear()

        # 更新粒子
        for p in particles:
            if not p.update():
                p.reset(
                    x=random.uniform(-W//2, W//2),
                    y=H//2 + 50,
                    emojis=get_emojis()
                )
                burst_count[0] += 1

        # 更新爆裂粒子
        for b in bursts[:]:
            if not b.update():
                bursts.remove(b)

        # 绘制主粒子
        for p in particles:
            t.goto(p.x, p.y)
            # 颜色根据 emoji 类型微调
            if any(c in p.emoji for c in '❤💕💗💖💝💘💓💞🩷♥'):
                t.pencolor("#ff8899")
            elif any(c in p.emoji for c in '🌸🌺🌷🌹🌼🌻💐✿❀'):
                t.pencolor("#ffaacc")
            elif any(c in p.emoji for c in '✨⭐🌟💫✧✦♪'):
                t.pencolor("#ffddaa")
            else:
                t.pencolor("#ffccdd")
            t.write(p.emoji, align="center",
                    font=("Apple Color Emoji", p.size, "normal"))

        # 绘制爆裂粒子
        for b in bursts:
            t.goto(b.x, b.y)
            t.pencolor("#ff8899")
            t.write(b.emoji, align="center",
                    font=("Apple Color Emoji", b.size, "normal"))

        # 更新计数
        if burst_count[0] > 0:
            count_display.clear()
            count_display.goto(W//2 - 80, H//2 - 20)
            count_display.color("#664444")
            count_display.write(f"🌸 ×{burst_count[0]}", align="right",
                                font=("Courier New", 12, "normal"))

        screen.update()

    # ── 点击绽放心动 ──
    def on_click(x, y):
        emojis = get_emojis()
        count = random.randint(10, 20)
        for i in range(count):
            angle = (2 * math.pi * i) / count + random.uniform(0, 0.3)
            speed = random.uniform(2, 6)
            b = LoveParticle(x, y, from_burst=True, emojis=emojis)
            b.vx = math.cos(angle) * speed
            b.vy = math.sin(angle) * speed
            b.size = random.randint(10, 22)
            b.life = 2.0
            b.opacity = 0.9
            bursts.append(b)
        burst_count[0] += 1

    screen.onclick(on_click)

    # ── 键盘 ──
    def on_space():
        nonlocal mode_idx
        mode_idx = (mode_idx + 1) % len(MODES)
        update_mode_display()
        # 切换模式时刷新所有粒子 emoji
        emojis = get_emojis()
        for p in particles:
            p.emoji = random.choice(emojis)

    def on_q():
        nonlocal running
        running = False
        screen.bye()

    screen.onkey(on_space, "space")
    screen.onkey(on_q, "q")
    screen.onkey(on_q, "Q")
    screen.listen()

    # ── 主循环 ──
    while running:
        draw_frame()
        # 小延迟让 turtle 事件循环能处理键盘
        time.sleep(0.016)  # ~60fps


# ═══════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════

if __name__ == '__main__':
    print("💕 cmatrix --love · Love Rain")
    print("   🖱️ 点击绽放心动 · 空格切换模式 · Q 退出")
    print("   ❤️🌸💕 五种主题：全模式 / 红心 / 花雨 / 星尘 / 粉彩")
    love_rain()
