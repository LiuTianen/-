import tkinter as tk
import random
import math

# ==========================================
# 心形数学函数 · 浪漫文字烟花优化版
# ==========================================

# ---------- 配置 ----------
TEXT_POOL = [
    "我爱你 ❤️",
    "想你了 💕",
    "永远爱你 ✨",
    "你是唯一 💖",
    "陪你很久 🌸",
]

BG_COLOR = "black"

PARTICLE_COUNT = 50

REFRESH_DELAY = 13
FIREWORK_INTERVAL = 2400

FONT_MAX = 30
FONT_MIN = 8

LIFETIME = 120

HEART_SCALE = 18

# ---------- 窗口 ----------
root = tk.Tk()

root.title("Heart Firework")

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


# ---------- 工具 ----------
COLORS = [
    "#FF1493",
    "#FF69B4",
    "#FFB6C1",
    "#FFD700",
    "#FF6347",
    "#FFFFFF",
    "#DA70D6",
    "#00BFFF",
]

# 预计算渐隐颜色表：避免每帧进行 hex 解析和字符串拼接
FADE_TABLE = {}
for c in COLORS:
    r = int(c[1:3], 16)
    g = int(c[3:5], 16)
    b = int(c[5:7], 16)
    table = []
    for life in range(LIFETIME, -1, -1):
        ratio = life / LIFETIME
        table.append(f"#{int(r * ratio):02x}{int(g * ratio):02x}{int(b * ratio):02x}")
    FADE_TABLE[c] = table


def random_color():
    return random.choice(COLORS)


# ==========================================
# 心形数学函数
#
# x = 16 sin³(t)
# y = 13 cos(t) - 5 cos(2t) - 2 cos(3t) - cos(4t)
#
# ==========================================
def heart_function(t):
    x = 16 * math.sin(t) ** 3

    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )

    return x, y


# ---------- 创建心形烟花 ----------
def create_heart_firework(cx=None, cy=None):
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
        t = (2 * math.pi / PARTICLE_COUNT) * i

        hx, hy = heart_function(t)

        # 缩放
        hx *= HEART_SCALE
        hy *= HEART_SCALE

        # 随机扰动
        hx += random.uniform(-8, 8)
        hy += random.uniform(-8, 8)

        # 初始速度
        dx = hx * 0.08
        dy = -hy * 0.08

        color = random_color()

        size = random.randint(FONT_MIN, FONT_MAX)

        item = canvas.create_text(
            cx,
            cy,
            text=text,
            fill=color,
            font=("微软雅黑", size, "bold")
        )

        particles.append({
            "id": item,
            "x": cx,
            "y": cy,
            "dx": dx,
            "dy": dy,
            "life": LIFETIME,
            "base_color": color,
        })


# ---------- 更新动画 ----------
def update():
    remove_ids = []
    remove_particles = []

    for p in particles:
        p["life"] -= 1

        if p["life"] <= 0:
            remove_ids.append(p["id"])
            remove_particles.append(p)
            continue

        # 缓慢阻尼
        p["dx"] *= 0.992
        p["dy"] *= 0.992

        # 微重力
        p["dy"] += 0.02

        p["x"] += p["dx"]
        p["y"] += p["dy"]

        # 查表获取渐隐颜色
        color = FADE_TABLE[p["base_color"]][LIFETIME - p["life"]]

        # 只更新坐标和颜色，不再每帧修改 font（极大提升性能）
        canvas.coords(p["id"], p["x"], p["y"])
        canvas.itemconfig(p["id"], fill=color)

    # 批量删除已消亡的粒子
    if remove_ids:
        canvas.delete(*remove_ids)
    for p in remove_particles:
        particles.remove(p)

    root.after(REFRESH_DELAY, update)


# ---------- 连续烟花 ----------
def loop_firework():
    create_heart_firework()

    # 中央超级爱心爆炸
    if random.random() < 0.35:
        create_heart_firework(
            screen_w // 2,
            screen_h // 2
        )

    root.after(
        FIREWORK_INTERVAL,
        loop_firework
    )


# ---------- ESC退出 ----------
def exit_app(event):
    root.destroy()

root.bind("<Escape>", exit_app)

# ---------- 启动 ----------
loop_firework()
update()

root.mainloop()
