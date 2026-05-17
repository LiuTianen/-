import tkinter as tk
import random
import math
import time

# =========================
# 终极浪漫文字烟花版 ❤️
# 飞散 + 渐隐 + 缩小 + 连续烟花
# =========================

# -------- 配置 --------
TEXT_POOL = [
    "我爱你 ❤️",
    "喜欢你 ✨",
    "想你了 💕",
    "永远爱你 💖",
    "你是我的光 🌙",
    "一直陪着你 🌸",
]

WINDOW_BG = "black"

PARTICLE_COUNT = 50          # 每波烟花文字数量
FIREWORK_INTERVAL = 2200      # 每波间隔(ms)

FONT_MAX_SIZE = 28
FONT_MIN_SIZE = 8

SPEED_MIN = 2
SPEED_MAX = 8

LIFETIME = 100                # 粒子寿命(帧)

REFRESH_DELAY = 16            # ≈60FPS

GRAVITY = 0.03                # 微重力
DRAG = 0.992                  # 阻力


# -------- 创建窗口 --------
root = tk.Tk()
root.title("Romantic Fireworks")

root.attributes("-fullscreen", True)
root.configure(bg=WINDOW_BG)

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

canvas = tk.Canvas(
    root,
    width=screen_w,
    height=screen_h,
    bg=WINDOW_BG,
    highlightthickness=0
)
canvas.pack()

particles = []


# -------- 工具函数 --------
def random_color():
    colors = [
        "#FF69B4",
        "#FF1493",
        "#FFB6C1",
        "#FFD700",
        "#00BFFF",
        "#7CFC00",
        "#FF4500",
        "#DA70D6",
        "#00FA9A",
        "#FFFFFF",
    ]
    return random.choice(colors)


def fade_color(hex_color, ratio):
    """
    根据 ratio 渐隐颜色
    ratio: 0~1
    """
    ratio = max(0, min(1, ratio))

    r = int(int(hex_color[1:3], 16) * ratio)
    g = int(int(hex_color[3:5], 16) * ratio)
    b = int(int(hex_color[5:7], 16) * ratio)

    return f"#{r:02x}{g:02x}{b:02x}"


# -------- 创建烟花 --------
def create_firework(x=None, y=None):

    if x is None:
        x = random.randint(
            screen_w // 4,
            screen_w * 3 // 4
        )

    if y is None:
        y = random.randint(
            screen_h // 4,
            screen_h * 3 // 4
        )

    text = random.choice(TEXT_POOL)

    for _ in range(PARTICLE_COUNT):

        angle = random.uniform(0, math.pi * 2)

        speed = random.uniform(
            SPEED_MIN,
            SPEED_MAX
        )

        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed

        color = random_color()

        size = random.randint(
            FONT_MAX_SIZE - 6,
            FONT_MAX_SIZE
        )

        item = canvas.create_text(
            x,
            y,
            text=text,
            fill=color,
            font=("微软雅黑", size, "bold")
        )

        particles.append({
            "id": item,
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
            "life": LIFETIME,
            "max_life": LIFETIME,
            "size": size,
            "base_color": color,
            "text": text
        })


# -------- 更新动画 --------
def update():

    remove_list = []

    for p in particles:

        # 生命周期
        p["life"] -= 1

        if p["life"] <= 0:
            remove_list.append(p)
            continue

        # 生命比例
        ratio = p["life"] / p["max_life"]

        # 物理运动
        p["dx"] *= DRAG
        p["dy"] *= DRAG

        p["dy"] += GRAVITY

        p["x"] += p["dx"]
        p["y"] += p["dy"]

        # 渐隐
        color = fade_color(
            p["base_color"],
            ratio
        )

        # 渐小
        size = int(
            FONT_MIN_SIZE +
            (p["size"] - FONT_MIN_SIZE) * ratio
        )

        size = max(FONT_MIN_SIZE, size)

        # 更新位置
        canvas.coords(
            p["id"],
            p["x"],
            p["y"]
        )

        # 更新样式
        canvas.itemconfig(
            p["id"],
            fill=color,
            font=("微软雅黑", size, "bold")
        )

    # 删除死亡粒子
    for p in remove_list:
        canvas.delete(p["id"])
        particles.remove(p)

    root.after(REFRESH_DELAY, update)


# -------- 连续烟花 --------
def loop_firework():

    # 随机位置连续爆炸
    create_firework()

    # 偶尔中心大爆炸
    if random.random() < 0.3:
        create_firework(
            screen_w // 2,
            screen_h // 2
        )

    root.after(
        FIREWORK_INTERVAL,
        loop_firework
    )


# -------- ESC退出 --------
def exit_app(event):
    root.destroy()

root.bind("<Escape>", exit_app)

# -------- 启动 --------
loop_firework()
update()

root.mainloop()