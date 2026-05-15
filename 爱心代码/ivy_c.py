'''
Date: 2026-05-12 00:50:07
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-15 00:20:07
FilePath: \-\爱心代码\ivy.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
import tkinter as tk
import tkinter.font as tkfont
import random
import time
import math

# ========== 配置 ==========
TARGET_TEXT = "❤"           # 中心大字
PARTICLE_TEXT = "❤"         # 每个粒子显示的内容
NUM_ITEMS = 400             # 粒子数量
PARTICLE_SIZE = 10          # 粒子字号
CENTER_FONT_SIZE = 220      # 中心大字字号
SPEED = 2.5                 # 像素/帧
REFRESH_DELAY = 16          # ≈60 FPS
SCATTER_DURATION = 9        # 随机飘散秒数

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

# ========== 计算心形目标点 ==========
def point_in_polygon(x, y, poly):
    """射线法判断点是否在多边形内部"""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def sample_heart_targets(num_points, sw, sh):
    """使用经典心形参数方程生成轮廓，并在内部均匀撒点作为目标坐标"""
    outline = []
    scale = min(sw, sh) / 38
    cx, cy = sw // 2, sh // 2 - 30  # 稍微上移，让心形居中更好看

    # 生成心形轮廓（600个点，足够平滑）
    for i in range(600):
        t = i * 2 * math.pi / 600
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        outline.append((cx + x * scale, cy + y * scale))

    # 计算轮廓边界框
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # 在边界框内随机撒点，保留落在心形内部的点
    pts = []
    attempts = 0
    max_attempts = num_points * 20
    while len(pts) < num_points and attempts < max_attempts:
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        if point_in_polygon(x, y, outline):
            pts.append((x, y))
        attempts += 1

    # 兜底：如果随机撒点不够，从轮廓上补充
    while len(pts) < num_points:
        pts.append(random.choice(outline))

    return pts

targets = sample_heart_targets(NUM_ITEMS, screen_width, screen_height)

# ========== 创建带阴影的粒子 ==========
items = []
pfont = (FONT_FACE, PARTICLE_SIZE, "bold")

for i in range(NUM_ITEMS):
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    color = random_warm_color()

    # 阴影层
    shadow_id = canvas.create_text(
        x + 1, y + 1, text=PARTICLE_TEXT, fill="#330000",
        font=pfont, anchor='nw'
    )
    # 主文字层
    text_id = canvas.create_text(
        x, y, text=PARTICLE_TEXT, fill=color,
        font=pfont, anchor='nw'
    )

    dx = random.choice([-1, 1]) * random.uniform(SPEED * 0.6, SPEED * 1.4)
    dy = random.choice([-1, 1]) * random.uniform(SPEED * 0.6, SPEED * 1.4)

    items.append({
        'shadow': shadow_id,
        'text': text_id,
        'dx': dx,
        'dy': dy,
        'target': targets[i],
        'gather_speed': 0.04 + random.random() * 0.06,
        'breath_phase': random.random() * math.pi * 2,
        'arrived': False
    })

# ========== 中心大字 ==========
center_text_items = []

def create_center_text():
    cx, cy = screen_width // 2, screen_height // 2 - 30
    # 粉色外发光（多层偏移）
    glow_offsets = [(-5,0),(5,0),(0,-5),(0,5),(-4,-4),(4,4),(-4,4),(4,-4)]
    for ox, oy in glow_offsets:
        tid = canvas.create_text(
            cx + ox, cy + oy, text=TARGET_TEXT,
            font=(FONT_FACE, CENTER_FONT_SIZE, "bold"),
            fill="#FF1493", anchor='center'
        )
        center_text_items.append(tid)
    # 白色主体
    main_id = canvas.create_text(
        cx, cy, text=TARGET_TEXT,
        font=(FONT_FACE, CENTER_FONT_SIZE, "bold"),
        fill="white", anchor='center'
    )
    center_text_items.append(main_id)
    # 将大字移到最底层，让粒子在其上方汇聚
    for tid in center_text_items:
        canvas.tag_lower(tid)

# ========== 动画循环 ==========
start_time = time.time()
phase = 'scatter'
gather_start_time = 0
center_text_created = False

def update():
    global phase, gather_start_time, center_text_created
    
    # 阶段切换
    if phase == 'scatter' and time.time() - start_time >= SCATTER_DURATION:
        phase = 'gather'
        gather_start_time = time.time()
    
    if phase == 'scatter':
        for item in items:
            dx, dy = item['dx'], item['dy']
            canvas.move(item['shadow'], dx, dy)
            canvas.move(item['text'], dx, dy)

            bbox = canvas.bbox(item['text'])
            if bbox:
                x1, y1, x2, y2 = bbox
                if x1 < 0 or x2 > screen_width:
                    item['dx'] = -dx
                if y1 < 0 or y2 > screen_height:
                    item['dy'] = -dy
    else:
        # 延迟显示中心大字，让粒子先汇聚一会儿
        if not center_text_created and time.time() - gather_start_time > 0.6:
            create_center_text()
            center_text_created = True
        
        for item in items:
            x, y = canvas.coords(item['text'])
            tx, ty = item['target']
            
            if not item['arrived']:
                dist = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
                if dist > 2:
                    new_x = x + (tx - x) * item['gather_speed']
                    new_y = y + (ty - y) * item['gather_speed']
                    canvas.coords(item['shadow'], new_x + 1, new_y + 1)
                    canvas.coords(item['text'], new_x, new_y)
                else:
                    # 到达目标，吸附并标记
                    item['arrived'] = True
                    canvas.coords(item['shadow'], tx + 1, ty + 1)
                    canvas.coords(item['text'], tx, ty)
            else:
                # 呼吸微动
                bp = item['breath_phase'] + 0.05
                item['breath_phase'] = bp
                bx = tx + math.sin(bp) * 2
                by = ty + math.cos(bp * 0.7) * 2
                canvas.coords(item['shadow'], bx + 1, by + 1)
                canvas.coords(item['text'], bx, by)
    
    root.after(REFRESH_DELAY, update)

# ========== 点击退出 ==========
def on_click(event=None):
    root.destroy()

root.bind("<Button-1>", on_click)

update()
root.mainloop()
