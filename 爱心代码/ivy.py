import tkinter as tk
import tkinter.font as tkfont
import random

# ========== 配置 ==========
TEXT = "我爱你❤"
NUM_ITEMS = 100
FONT_SIZE = 22
SPEED = 2.5              # 像素/帧
REFRESH_DELAY = 16       # ≈60 FPS

# ========== 窗口初始化 ==========
root = tk.Tk()
root.title("表白满屏")
root.attributes('-fullscreen', True)
root.configure(bg='black')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

canvas = tk.Canvas(root, bg='black', highlightthickness=0, cursor='heart')
canvas.pack(fill=tk.BOTH, expand=True)

# ========== 字体 & 配色 ==========
# 优先使用系统里的中文字体，否则回退 Arial
available = set(tkfont.families())
CANDIDATE_FONTS = ["华文行楷", "华文彩云", "Microsoft YaHei", "PingFang SC", "SimHei", "Arial"]
FONT_FACE = next((f for f in CANDIDATE_FONTS if f in available), "Arial")

def random_warm_color():
    """生成柔和浪漫的暖色系"""
    palette = [
        "#FF6B6B", "#FF8E8E", "#FFB6C1", "#FF69B4",
        "#FF1493", "#DB7093", "#FF7F50", "#FFA07A",
        "#FFD700", "#FFAA33", "#EE82EE", "#DA70D6",
        "#F08080", "#FA8072", "#E9967A", "#FFE4E1",
        "#FF4500", "#FF6347", "#DDA0DD", "#F0E68C"
    ]
    return random.choice(palette)

# ========== 创建带阴影的文字 ==========
items = []
font = (FONT_FACE, FONT_SIZE, "bold")

for _ in range(NUM_ITEMS):
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    color = random_warm_color()

    # 阴影层（偏移 2px，深色）
    shadow_id = canvas.create_text(
        x + 2, y + 2, text=TEXT, fill="#330000",
        font=font, anchor='nw'
    )
    # 主文字层
    text_id = canvas.create_text(
        x, y, text=TEXT, fill=color,
        font=font, anchor='nw'
    )

    dx = random.choice([-1, 1]) * random.uniform(SPEED * 0.6, SPEED * 1.4)
    dy = random.choice([-1, 1]) * random.uniform(SPEED * 0.6, SPEED * 1.4)

    items.append({
        'shadow': shadow_id,
        'text': text_id,
        'dx': dx,
        'dy': dy
    })

# ========== 动画循环 ==========
def update():
    for item in items:
        dx, dy = item['dx'], item['dy']
        # 阴影和主文字同步移动
        canvas.move(item['shadow'], dx, dy)
        canvas.move(item['text'], dx, dy)

        # 边界反弹（用 text 层做判断即可）
        bbox = canvas.bbox(item['text'])
        if bbox:
            x1, y1, x2, y2 = bbox
            if x1 < 0 or x2 > screen_width:
                item['dx'] = -dx
            if y1 < 0 or y2 > screen_height:
                item['dy'] = -dy
    root.after(REFRESH_DELAY, update)

# ========== 点击退出 ==========
def on_click(event=None):
    root.destroy()

root.bind("<Button-1>", on_click)      # 鼠标左键点击退出

update()
root.mainloop()
