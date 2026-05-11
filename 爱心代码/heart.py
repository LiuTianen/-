import tkinter as tk
import math
import random
import time

# --- 基础配置 ---
WIDTH, HEIGHT = 1000, 800
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
PARTICLE_COUNT = 180 
HEART_WORDS = ["✨", "Love", "浪漫", "惊喜", "Happy", "Forever", "Sweet", "❤️", "Luck", "Dream"]
COLOR_POOL = ["#FF1493", "#FF69B4", "#FF4500", "#00BFFF", "#FFD700", "#9400D3", "#7FFF00", "#00FFFF"]

def get_heart_coord(t, scale=18):
    x = 16 * (math.sin(t) ** 3)
    y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
    return CENTER_X + x * scale, CENTER_Y + y * scale

def get_circle_coord(t, radius=250):
    x = math.cos(t) * radius
    y = math.sin(t) * radius
    return CENTER_X + x, CENTER_Y + y

class Particle:
    def __init__(self, canvas, index, mode="instant"):
        self.canvas = canvas
        self.t = (index / PARTICLE_COUNT) * 2 * math.pi
        
        # 目标位置
        self.target_x, self.target_y = get_heart_coord(self.t)
        
        # 初始状态
        self.x, self.y = self.target_x, self.target_y
        self.color = random.choice(COLOR_POOL)
        self.text = random.choice(HEART_WORDS)
        
        # 视觉多样化
        self.font_size = random.randint(9, 14)
        self.border_w = random.randint(0, 2)
        
        # 创建组件
        self.id = canvas.create_text(self.x, self.y, text=self.text, fill="white", 
                                     font=("Microsoft YaHei", self.font_size, "bold"))
        bbox = canvas.bbox(self.id)
        self.bg_id = canvas.create_rectangle(bbox[0]-5, bbox[1]-2, bbox[2]+5, bbox[3]+2, 
                                             fill=self.color, outline="white", width=self.border_w)
        canvas.tag_lower(self.bg_id, self.id)

        self.vx, self.vy = 0, 0
        self.friction = 0.96

    def update_render(self):
        try:
            self.canvas.coords(self.id, self.x, self.y)
            bbox = self.canvas.bbox(self.id)
            self.canvas.coords(self.bg_id, bbox[0]-5, bbox[1]-2, bbox[2]+5, bbox[3]+2)
            return True
        except:
            return False

    def explode(self):
        angle = random.uniform(0, 2 * math.pi)
        power = random.uniform(10, 35) 
        self.vx = math.cos(angle) * power
        self.vy = math.sin(angle) * power

    def drift(self):
        self.vx += random.uniform(-0.3, 0.3)
        self.vy += random.uniform(-0.3, 0.3)
        self.vx *= 0.98
        self.vy *= 0.98
        self.x += self.vx
        self.y += self.vy
        self.update_render()

def ease_out_quint(t):
    return 1 - pow(1 - t, 5)

def move_particles(root, particles, frames, duration_ms=10):
    start_pos = [(p.x, p.y) for p in particles]
    for f in range(frames + 1):
        progress = ease_out_quint(f / frames)
        for i, p in enumerate(particles):
            p.x = start_pos[i][0] + (p.target_x - start_pos[i][0]) * progress
            p.y = start_pos[i][1] + (p.target_y - start_pos[i][1]) * progress
            if not p.update_render(): return False
        root.update()
        time.sleep(duration_ms / 1000)
    return True

def main():
    root = tk.Tk()
    TRANS_COLOR = '#000001'
    root.overrideredirect(True)
    root.attributes("-topmost", True, "-transparentcolor", TRANS_COLOR)
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{WIDTH}x{HEIGHT}+{(sw-WIDTH)//2}+{(sh-HEIGHT)//2}")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=TRANS_COLOR, highlightthickness=0)
    canvas.pack()
    root.bind("<Button-1>", lambda e: root.destroy())

    try:
        # --- 阶段 1: 真正的“画出”爱心 ---
        particles = []
        # 我们按照参数 t 的顺序生成，这样标签会顺着爱心的轮廓一个接一个出现
        for i in range(PARTICLE_COUNT):
            p = Particle(canvas, i)
            particles.append(p)
            
            # 每生成一个就刷新一次，造成“生长”效果
            # 调节 0.03 这个数值，数值越大，爱心画得越慢越细腻
            root.update()
            time.sleep(0.03) 
        
        time.sleep(1.5)

        while True:
            # --- 阶段 2: 随机大爆炸 ---
            for p in particles: p.explode()
            for _ in range(60):
                for p in particles: 
                    p.vx *= 0.94
                    p.vy *= 0.94
                    p.x += p.vx
                    p.y += p.vy
                    p.update_render()
                root.update()
                time.sleep(0.02)

            # --- 阶段 3: 随机漫游 (5-10秒) ---
            start_drift = time.time()
            drift_duration = random.uniform(5, 10)
            while time.time() - start_drift < drift_duration:
                for p in particles: p.drift()
                root.update()
                time.sleep(0.02)

            # --- 阶段 4: 汇聚成圆形 ---
            for p in particles:
                tx, ty = get_circle_coord(p.t)
                p.target_x, p.target_y = tx, ty
            if not move_particles(root, particles, 100): break
            time.sleep(2)

            # --- 阶段 5: 回归爱心 ---
            for p in particles:
                tx, ty = get_heart_coord(p.t)
                p.target_x, p.target_y = tx, ty
            if not move_particles(root, particles, 120): break
            time.sleep(2)

    except tk.TclError:
        pass

if __name__ == "__main__":
    main()