#!/usr/bin/env python3
"""
玫瑰线 (Rose Curve / Rhodonea Curve)
r = cos(kθ) 的极坐标曲线

运行: python3 rose.py
依赖: Python 内置 turtle（无需安装）

花瓣数 = k (当 k 为奇数) 或 2k (当 k 为偶数)
"""

import math
import turtle
import colorsys

# ── 配置 ──
K = 5               # 花瓣参数：奇数=k瓣，偶数=2k瓣，非整数=复杂图案
A = 280             # 振幅（花瓣长度）
STEPS = 2000        # 采样点数
SPEED = 0           # 0=最快, 1=最慢
BG_COLOR = "#0d0d1a"  # 深色背景
LINE_WIDTH = 2

def rose_curve(k, a, steps):
    """生成玫瑰线的 (x, y) 坐标列表"""
    points = []
    # 需要 2π * denominator 个周期来闭合曲线
    # 当 k = p/q 时，需要 q 个完整周期
    # 简化：扫描到足够闭合
    max_theta = 2 * math.pi
    # 对于非整数 k，可能需要更多周期
    if k != int(k):
        # 找到最简分数
        from fractions import Fraction
        frac = Fraction(k).limit_denominator(20)
        max_theta *= frac.denominator

    for i in range(steps):
        theta = (i / steps) * max_theta
        r = a * math.cos(k * theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append((x, y))
    return points


def draw_rose(k, a, steps):
    """用 turtle 绘制玫瑰线"""
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.bgcolor(BG_COLOR)
    screen.title(f"🌹 玫瑰线 · k={k}")
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(SPEED)
    t.pensize(LINE_WIDTH)

    points = rose_curve(k, a, steps)

    for i, (x, y) in enumerate(points):
        # 渐变色：从深红到粉金
        hue = 0.95 + 0.05 * (i / len(points))  # 红-粉范围
        if hue > 1.0:
            hue -= 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.9 + 0.1 * (i % 5) / 5)
        color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        t.pencolor(color)

        if i == 0:
            t.penup()
            t.goto(x, y)
            t.pendown()
        else:
            t.goto(x, y)

        # 每 20 帧刷新一次，产生绘制动画
        if i % 20 == 0:
            screen.update()

    screen.update()

    # 写标题
    t.penup()
    t.goto(0, -320)
    t.pencolor("#c9a96e")
    t.write(f"玫瑰线 r = cos({k}θ)", align="center",
            font=("Georgia", 18, "italic"))

    screen.exitonclick()


if __name__ == "__main__":
    import sys
    k = K
    if len(sys.argv) > 1:
        try:
            k = float(sys.argv[1])
        except ValueError:
            print(f"用法: python3 rose.py [花瓣数]")
            print(f"示例: python3 rose.py 5    # 5瓣玫瑰")
            print(f"       python3 rose.py 2    # 4瓣玫瑰")
            print(f"       python3 rose.py 1.5  # 复杂图案")
            sys.exit(1)
    print(f"🌹 绘制玫瑰线 k={k} ...")
    draw_rose(k, A, STEPS)
