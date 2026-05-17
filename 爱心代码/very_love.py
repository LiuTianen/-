import tkinter as tk
import random
import math

# =========================================================
# 🌸 樱花爱心轨迹 · 贝塞尔花瓣烟花终极版
#
# 特性：
# - 爱心数学函数
# - 花瓣曲线运动
# - 贝塞尔轨迹
# - 樱花漂浮感
# - 渐隐 + 缩小
# - 连续浪漫烟花
# =========================================================

# ---------------- 配置 ----------------

TEXT_POOL = [
    "我爱你 ❤️",
    "想你了 🌸",
    "永远爱你 💖",
    "你是唯一 ✨",
    "陪你很久 💕",
]

BG_COLOR = "black"

PARTICLE_COUNT = 60

REFRESH_DELAY = 13
FIREWORK_INTERVAL = 2600

FONT_MAX = 30
FONT_MIN = 8

LIFETIME = 150

HEART_SCALE = 15

PETAL_SWING = 18

# ---------------- 窗口 ----------------

root = tk.Tk()

root.title("Sakura Heart Firework")

root.attributes("-fullscreen", True)
root.configure(bg=BG_COLOR)

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

canvas = tk.Canvas(
    root,
    width=screen_w,
    height=screen_h,
    bg=BG_COLOR,
    highlightthickness=0
)

canvas.pack()

particles = []

# =========================================================
# 工具函数
# =========================================================

def random_color():

    colors = [
        "#FFB7C5",
        "#FFC0CB",
        "#FF69B4",
        "#FF1493",
        "#FFD1DC",
        "#FFE4E1",
        "#FFFFFF",
        "#FFF0F5",
    ]

    return random.choice(colors)


def fade_color(color, ratio):

    ratio = max(0, min(1, ratio))

    r = int(int(color[1:3], 16) * ratio)
    g = int(int(color[3:5], 16) * ratio)
    b = int(int(color[5:7], 16) * ratio)

    return f"#{r:02x}{g:02x}{b:02x}"


# =========================================================
# ❤️ 心形数学函数
# =========================================================

def heart_function(t):

    x = 16 * math.sin(t) ** 3

    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )

    return x, y


# =========================================================
# 🌸 二次贝塞尔曲线
# =========================================================

def bezier_curve(p0, p1, p2, t):

    x = (
        (1 - t) ** 2 * p0[0]
        + 2 * (1 - t) * t * p1[0]
        + t ** 2 * p2[0]
    )

    y = (
        (1 - t) ** 2 * p0[1]
        + 2 * (1 - t) * t * p1[1]
        + t ** 2 * p2[1]
    )

    return x, y


# =========================================================
# 🌸 创建樱花爱心烟花
# =========================================================

def create_sakura_heart(cx=None, cy=None):

    if cx is None:
        cx = random.randint(
            screen_w // 3,
            screen_w * 2 // 3
        )

    if cy is None:
        cy = random.randint(
            screen_h // 3,
            screen_h * 2 // 3
        )

    text = random.choice(TEXT_POOL)

    for i in range(PARTICLE_COUNT):

        # 心形轨迹参数
        t = (2 * math.pi / PARTICLE_COUNT) * i

        hx, hy = heart_function(t)

        hx *= HEART_SCALE
        hy *= HEART_SCALE

        # ----------------
        # 贝塞尔起点
        # ----------------
        start = (cx, cy)

        # ----------------
        # 贝塞尔终点（爱心）
        # ----------------
        end = (
            cx + hx * 8,
            cy - hy * 8
        )

        # ----------------
        # 贝塞尔控制点
        # 加入花瓣摆动
        # ----------------
        control = (
            cx + random.uniform(-120, 120),
            cy + random.uniform(-120, 120)
        )

        color = random_color()

        size = random.randint(
            FONT_MAX - 5,
            FONT_MAX
        )

        item = canvas.create_text(
            cx,
            cy,
            text=text,
            fill=color,
            font=("微软雅黑", size, "bold")
        )

        particles.append({

            "id": item,

            "life": LIFETIME,
            "max_life": LIFETIME,

            "start": start,
            "control": control,
            "end": end,

            "base_color": color,
            "size": size,

            "swing_phase": random.uniform(0, math.pi * 2),
            "swing_speed": random.uniform(0.05, 0.12),

            "text": text
        })


# =========================================================
# 🌸 更新动画
# =========================================================

def update():

    remove_list = []

    for p in particles:

        p["life"] -= 1

        if p["life"] <= 0:
            remove_list.append(p)
            continue

        ratio = p["life"] / p["max_life"]

        # 当前贝塞尔进度
        t = 1 - ratio

        # 贝塞尔轨迹
        x, y = bezier_curve(
            p["start"],
            p["control"],
            p["end"],
            t
        )

        # --------------------------------
        # 🌸 花瓣摆动
        # --------------------------------
        swing = math.sin(
            t * 10 +
            p["swing_phase"]
        ) * PETAL_SWING * ratio

        x += swing

        # --------------------------------
        # 渐隐
        # --------------------------------
        color = fade_color(
            p["base_color"],
            ratio
        )

        # --------------------------------
        # 缩小
        # --------------------------------
        size = int(
            FONT_MIN +
            (p["size"] - FONT_MIN) * ratio
        )

        size = max(FONT_MIN, size)

        canvas.coords(
            p["id"],
            x,
            y
        )

        canvas.itemconfig(
            p["id"],
            fill=color,
            font=("微软雅黑", size, "bold")
        )

    # 删除死亡粒子
    for p in remove_list:
        canvas.delete(p["id"])
        particles.remove(p)

    root.after(
        REFRESH_DELAY,
        update
    )


# =========================================================
# 🌸 连续烟花
# =========================================================

def loop_firework():

    create_sakura_heart()

    # 中央超级爱心
    if random.random() < 0.35:

        create_sakura_heart(
            screen_w // 2,
            screen_h // 2
        )

    root.after(
        FIREWORK_INTERVAL,
        loop_firework
    )


# =========================================================
# ESC退出
# =========================================================

def exit_app(event):
    root.destroy()

root.bind("<Escape>", exit_app)

# =========================================================
# 启动
# =========================================================

loop_firework()
update()

root.mainloop()