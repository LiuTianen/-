#!/usr/bin/env python3
"""
蝴蝶曲线 (Butterfly Curve) · Temple Fay
参数方程：
  x = sin(t) * (e^cos(t) - 2cos(4t) - sin⁵(t/12))
  y = cos(t) * (e^cos(t) - 2cos(4t) - sin⁵(t/12))

运行: python3 butterfly.py [精度=4]
依赖: Python 内置 turtle（无需安装）
"""

import math
import turtle
import colorsys
import sys

# ── 配置 ──
A = 60              # 振幅（缩放）
STEPS = 4000        # 采样点基数
SPEED = 0           # 0=最快
BG_COLOR = "#0a0a18"
LINE_WIDTH = 2

def butterfly_curve(a, steps):
    """
    生成蝴蝶曲线的 (x, y) 坐标列表
    t 从 0 到 12π
    """
    points = []
    max_t = 12 * math.pi
    for i in range(steps):
        t = (i / steps) * max_t
        r = math.exp(math.cos(t)) - 2 * math.cos(4 * t) - math.sin(t / 12) ** 5
        x = a * math.sin(t) * r
        y = a * math.cos(t) * r
        points.append((x, y))
    return points


def draw_butterfly(a, steps):
    """用 turtle 绘制蝴蝶曲线"""
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.bgcolor(BG_COLOR)
    screen.title("🦋 蝴蝶曲线 · Butterfly Curve")
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(SPEED)
    t.pensize(LINE_WIDTH)

    points = butterfly_curve(a, steps)
    total = len(points)

    for i, (x, y) in enumerate(points):
        # 渐变色：从蓝紫渐变到橙金（蝴蝶翅膀色）
        progress = i / total
        hue = 0.6 + 0.35 * progress  # 蓝紫(0.6) → 橙金(0.12 绕回)
        if hue > 1.0:
            hue -= 1.0
        # 中部更亮，两端更深
        dist = abs(progress - 0.5) * 2  # 0=中部, 1=两端
        saturation = 0.7 + 0.3 * (1 - dist)
        value = 0.6 + 0.4 * (1 - dist)

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        t.pencolor(color)

        if i == 0:
            t.penup()
            t.goto(x, y)
            t.pendown()
        else:
            t.goto(x, y)

        if i % 30 == 0:
            screen.update()

    screen.update()

    # 写标题
    t.penup()
    t.goto(0, -340)
    t.pencolor("#c9a96e")
    t.write("蝴蝶曲线 · Butterfly Curve", align="center",
            font=("Georgia", 16, "italic"))
    t.goto(0, -360)
    t.pencolor("#666")
    t.write("Temple Fay · x = sin t (e^cos t − 2cos 4t − sin⁵ t/12)",
            align="center", font=("Georgia", 10, "italic"))

    screen.exitonclick()


if __name__ == "__main__":
    multiplier = 1
    if len(sys.argv) > 1:
        try:
            multiplier = float(sys.argv[1])
        except ValueError:
            print(f"用法: python3 butterfly.py [精度倍数]")
            print(f"示例: python3 butterfly.py 1")
            print(f"       python3 butterfly.py 2    # 2倍精度")
            print(f"       python3 butterfly.py 4    # 4倍精度（更细腻）")
            sys.exit(1)
    steps = int(STEPS * multiplier)
    print(f"🦋 绘制蝴蝶曲线 (精度 ×{multiplier}, {steps} 点) ...")
    draw_butterfly(A, steps)
