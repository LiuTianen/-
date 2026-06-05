#!/usr/bin/env python3
"""
云朵生成器 (Cloud Generator)
用柏林噪声 (Perlin Noise) 生成独一无二的云朵

  x = sin(t) · (e^cos(t) − 2cos(4t) − sin⁵(t/12))
  y = cos(t) · (e^cos(t) − 2cos(4t) − sin⁵(t/12))

运行: python3 cloud.py [种子]
依赖: Python 内置 turtle + random（无需安装）

每次运行生成一朵独一无二的云。
"""

import math
import random
import turtle
import sys

# ═══════════════════════════════════════════
# Perlin Noise 2D (纯 Python 实现，零依赖)
# ═══════════════════════════════════════════

def _fade(t):
    """平滑曲线 6t⁵ − 15t⁴ + 10t³"""
    return t * t * t * (t * (t * 6 - 15) + 10)

def _lerp(a, b, t):
    return a + t * (b - a)

def _make_perm(seed):
    """生成随机排列表"""
    p = list(range(256))
    r = random.Random(seed)
    r.shuffle(p)
    return p * 2  # 双倍长度避免边界检查


# 预计算梯度向量
_GRAD3 = [(1, 1), (-1, 1), (1, -1), (-1, -1),
          (1, 0), (-1, 0), (0, 1), (0, -1)]


def _noise2d(x, y, perm):
    """单层 Perlin 噪声"""
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    u = _fade(xf)
    v = _fade(yf)

    aa = perm[perm[X] + Y]
    ab = perm[perm[X] + Y + 1]
    ba = perm[perm[X + 1] + Y]
    bb = perm[perm[X + 1] + Y + 1]

    def _dot(g, dx, dy):
        return g[0] * dx + g[1] * dy

    x1 = _lerp(_dot(_GRAD3[aa & 7], xf, yf),
               _dot(_GRAD3[ba & 7], xf - 1, yf), u)
    x2 = _lerp(_dot(_GRAD3[ab & 7], xf, yf - 1),
               _dot(_GRAD3[bb & 7], xf - 1, yf - 1), u)
    return _lerp(x1, x2, v)


def fbm(x, y, perm, octaves=6, lacunarity=2.0, gain=0.5):
    """分形布朗运动 — 多倍频叠加"""
    val = 0.0
    amp = 1.0
    freq = 1.0
    max_val = 0.0
    for _ in range(octaves):
        val += _noise2d(x * freq, y * freq, perm) * amp
        max_val += amp
        amp *= gain
        freq *= lacunarity
    return val / max_val  # 归一化到 [-1, 1]


def smoothstep(edge0, edge1, x):
    """平滑阶跃"""
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


# ═══════════════════════════════════════════
# 云朵生成
# ═══════════════════════════════════════════

def generate_cloud(seed, width=600, height=420, grid_res=5):
    """
    生成云朵点阵
    返回: [(x, y, brightness, alpha), ...]
    """
    perm = _make_perm(seed)
    rng = random.Random(seed)

    cx = width / 2
    cy = height / 2

    # 云参数（基于种子随机化）
    threshold = -0.08 + rng.random() * 0.25   # -0.08 ~ 0.17
    edge_soft = 0.20 + rng.random() * 0.15     # 0.20 ~ 0.35
    freq_scale = 0.003 + rng.random() * 0.002   # 噪声频率
    stretch_x = 1.2 + rng.random() * 0.6        # 水平拉伸
    stretch_y = 0.7 + rng.random() * 0.3        # 垂直压缩
    offset_y = -20 + rng.random() * 40          # 垂直偏移
    octaves = 5 + rng.randint(0, 2)             # 5~7 层

    points = []

    for py in range(0, height, grid_res):
        for px in range(0, width, grid_res):
            # 归一化坐标
            nx = (px - cx) / (width * 0.42) * stretch_x
            ny = (py - cy - offset_y) / (height * 0.42) * stretch_y

            # FBM 噪声
            n = fbm(nx * freq_scale * width, ny * freq_scale * height,
                    perm, octaves)

            # 椭圆遮罩
            dist = math.sqrt(nx * nx + ny * ny)
            mask = 1 - smoothstep(0.5, 0.85, dist)

            # 云阈值
            cloudiness = smoothstep(threshold - edge_soft,
                                    threshold + edge_soft, n) * mask

            if cloudiness < 0.05:
                continue

            # 立体光影：上方更亮
            height_factor = 1.0 - (py / height) * 0.4
            brightness = 0.65 + 0.35 * cloudiness * height_factor

            points.append((px - width / 2, height / 2 - py,  # turtle 坐标（中心为原点）
                          brightness, cloudiness))

    return points


# ═══════════════════════════════════════════
# Turtle 绘制
# ═══════════════════════════════════════════

def draw_cloud(seed, theme='clear'):
    """用 turtle 绘制云朵"""
    # 主题配色
    themes = {
        'dawn':  {'bg': '#1a2240', 'cloud_top': (255, 235, 220), 'cloud_bot': (220, 180, 190)},
        'clear': {'bg': '#3a6fb5', 'cloud_top': (255, 255, 255), 'cloud_bot': (220, 230, 240)},
        'dusk':  {'bg': '#1a1030', 'cloud_top': (255, 210, 180), 'cloud_bot': (200, 140, 160)},
        'night': {'bg': '#050510', 'cloud_top': (180, 190, 220), 'cloud_bot': (120, 130, 170)},
    }
    th = themes.get(theme, themes['clear'])

    screen = turtle.Screen()
    screen.setup(750, 550)
    screen.bgcolor(th['bg'])
    cloud_id = _gen_id(seed)
    screen.title(f"☁️ 云朵生成器 · {cloud_id}")
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.penup()

    # 生成云彩点
    points = generate_cloud(seed, width=600, height=420, grid_res=7)

    top_r, top_g, top_b = th['cloud_top']
    bot_r, bot_g, bot_b = th['cloud_bot']

    for (x, y, brightness, alpha) in points:
        # 根据 y 位置混合顶部和底部颜色
        y_ratio = (y + 210) / 420  # 0 = 顶部, 1 = 底部
        r = int(_lerp(top_r, bot_r, y_ratio) * brightness)
        g = int(_lerp(top_g, bot_g, y_ratio) * brightness)
        b = int(_lerp(top_b, bot_b, y_ratio) * brightness)
        color = f"#{min(255,r):02x}{min(255,g):02x}{min(255,b):02x}"

        t.goto(x, y)
        t.pencolor(color)
        t.fillcolor(color)
        # 点的大小基于透明度
        dot_size = int(3 + alpha * 5)
        t.dot(int(dot_size))

    # 写 ID
    t.goto(0, -220)
    t.pencolor('#ffffff88')
    t.write(f"☁️ {cloud_id}", align="center",
            font=("Courier New", 14, "bold"))
    t.goto(0, -245)
    t.pencolor('#ffffff44')
    t.write("这片云只属于你", align="center",
            font=("PingFang SC", 11, "normal"))

    screen.update()

    # 夜空星星
    if theme == 'night':
        rng = random.Random(seed + 999)
        for _ in range(40):
            sx = rng.randint(-350, 350)
            sy = rng.randint(0, 250)
            sz = 1 + rng.random() * 2
            br = 0.3 + rng.random() * 0.5
            t.goto(sx, sy)
            c = int(200 * br)
            t.pencolor(f"#{c:02x}{c+20:02x}{c+55:02x}")
            t.dot(sz)

    screen.update()
    screen.exitonclick()


def _gen_id(seed):
    """生成唯一云 ID"""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    vid = seed & 0xFFFFFFFF
    rid = ''
    for _ in range(6):
        rid = chars[vid % len(chars)] + rid
        vid = vid // len(chars) + (vid * 13 + 7)
        vid &= 0xFFFFFFFF
    return f"CLOUD-{rid}"


# ═══════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════

USAGE = """☁️ 云朵生成器 · Cloud Generator

用法:
  python3 cloud.py               随机种子
  python3 cloud.py 42            指定种子
  python3 cloud.py 42 dawn       种子 + 主题

主题: dawn(朝霞) clear(晴空) dusk(黄昏) night(夜空)
"""

if __name__ == '__main__':
    seed = random.randint(0, 2**31 - 1)
    theme = 'clear'

    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except ValueError:
            print(USAGE)
            sys.exit(1)
    if len(sys.argv) > 2:
        theme = sys.argv[2]
        if theme not in ('dawn', 'clear', 'dusk', 'night'):
            print(f"未知主题: {theme}")
            print(USAGE)
            sys.exit(1)

    cloud_id = _gen_id(seed)
    print(f"☁️ 生成云朵 {cloud_id} (种子={seed}, 主题={theme})")
    print(f"   下次用 python3 cloud.py {seed} {theme} 重现这朵云")
    draw_cloud(seed, theme)
