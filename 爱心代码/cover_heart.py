import pygame
import random
import math
import sys
"""pip install pygame-ce"""
# --- 基础配置 ---
WIDTH, HEIGHT = 1000, 800
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2 - 50
FPS = 60

# 统一颜色池 (确保都是整数)
HEART_COLORS = [
    (255, 182, 193), (255, 192, 203), (255, 105, 180), 
    (255, 20, 147), (219, 112, 147), (255, 240, 245)
]

def get_heart_coord(t, scale):
    """心形数学公式"""
    x = 16 * (math.sin(t) ** 3)
    y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
    return CENTER_X + x * scale, CENTER_Y + y * scale

class StarParticle:
    def __init__(self, tx, ty, color):
        self.tx, self.ty = tx, ty
        self.x, self.y = CENTER_X + random.uniform(-20, 20), CENTER_Y + random.uniform(-20, 20)
        self.color = color
        self.size = random.uniform(1, 2.8)
        self.base_alpha = random.randint(160, 255)

    def draw(self, screen, current_scale):
        # 实时计算带呼吸缩放的目标位置
        target_x = CENTER_X + (self.tx - CENTER_X) * current_scale
        target_y = CENTER_Y + (self.ty - CENTER_Y) * current_scale
        
        # 平滑移动
        self.x += (target_x - self.x) * 0.1
        self.y += (target_y - self.y) * 0.1
        
        # --- 核心修复：确保颜色和透明度为整数 ---
        # 随机闪烁透明度，并用 int() 限制在 0-255
        temp_alpha = int(max(0, min(255, self.base_alpha + random.randint(-30, 30))))
        
        # 创建支持透明度的表面
        s_size = int(self.size * 2) + 2
        s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
        
        # 确保颜色分量也是整数
        r, g, b = [int(c) for c in self.color]
        
        pygame.draw.circle(s, (r, g, b, temp_alpha), (s_size // 2, s_size // 2), int(self.size))
        screen.blit(s, (int(self.x), int(self.y)))

def main():
    pygame.init()
    # 启用双缓冲
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Particle Heart")
    clock = pygame.time.Clock()

    particles = []
    # 增加到 3000 个粒子让爱心更丰满
    for i in range(10000):
        t = random.uniform(0, 2 * math.pi)
        # 扩散填充内部，sqrt 保证均匀度
        r = math.sqrt(random.random()) 
        tx, ty = get_heart_coord(t, 19 * r)
        particles.append(StarParticle(tx, ty, random.choice(HEART_COLORS)))

    frame = 0
    try:
        while True:
            screen.fill((0, 0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.quit()
                    sys.exit()

            # 呼吸缩放因子
            beat_scale = 1.0 + 0.07 * abs(math.sin(frame * 0.05))
            frame += 1

            # 绘制底层扩散光圈（倒影/底座感）
            reflection_y = HEIGHT - 180
            for i in range(0, 360, 8):
                rad = math.radians(i)
                rx = CENTER_X + math.cos(rad) * 230 * (1.0 + 0.02 * math.sin(frame*0.05))
                ry = reflection_y + math.sin(rad) * 40
                # 绘制暗色光点
                pygame.draw.circle(screen, (80, 20, 40), (int(rx), int(ry)), 1)

            # 更新并绘制粒子
            for p in particles:
                p.draw(screen, beat_scale)

            pygame.display.flip()
            clock.tick(FPS)
            
    except (pygame.error, SystemExit):
        pass

if __name__ == "__main__":
    main()