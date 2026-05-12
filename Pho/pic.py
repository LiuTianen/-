'''
Date: 2026-05-13 00:08:44
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-13 00:27:28
FilePath: \-\Pho\pic.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# -----------------------------
# 配置参数
# -----------------------------
img_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")  # 批量照片文件夹
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mosaic_result.png") # 输出路径
target_text = "星"                # 目标文字/形状
font_path = "arial.ttf"           # 字体文件路径（系统字体或自定义）
canvas_size = (800, 800)          # 最终拼图大小
cell_size = (40, 40)              # 每张图片占用的单元格大小

# -----------------------------
# 读取和缩放图片
# -----------------------------
def load_and_resize_images(folder, size):
    images = []
    for fname in os.listdir(folder):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(os.path.join(folder, fname)).convert('RGB')
            img = img.resize(size)
            images.append(img)
    return images

images = load_and_resize_images(img_folder, cell_size)
if not images:
    raise ValueError("没有找到图片，请检查路径")

# -----------------------------
# 创建目标文字/形状灰度图
# -----------------------------
def create_pattern(text, font_path, canvas_size):
    img = Image.new('L', canvas_size, color=255)  # 白色背景
    draw = ImageDraw.Draw(img)
    # 自动适配文字大小
    font_size = 10
    while True:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w > canvas_size[0]*0.9 or h > canvas_size[1]*0.9:
            break
        font_size += 5
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (canvas_size[0] - w) / 2 - bbox[0]
    y = (canvas_size[1] - h) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=0)  # 黑色文字
    return np.array(img)

pattern_array = create_pattern(target_text, font_path, canvas_size)

# -----------------------------
# 将图片映射到目标图案
# -----------------------------
def match_images_to_pattern(images, pattern_array, cell_size):
    img_gray = [np.array(img.convert('L')).mean() for img in images]  # 图片平均灰度
    rows = pattern_array.shape[0] // cell_size[1]
    cols = pattern_array.shape[1] // cell_size[0]

    result = Image.new('RGB', (cols*cell_size[0], rows*cell_size[1]), color=(255,255,255))
    usage_count = [0] * len(images)  # 记录每张图的使用次数

    for i in range(rows):
        for j in range(cols):
            # 对应目标灰度
            y, x = i*cell_size[1], j*cell_size[0]
            target_gray = pattern_array[y:y+cell_size[1], x:x+cell_size[0]].mean()
            diffs = np.array([abs(g - target_gray) for g in img_gray])

            # 先找出最匹配的前 N 个候选
            top_n = min(5, len(images))
            candidates = np.argsort(diffs)[:top_n]

            # 在候选中挑选使用次数最少的；如果使用次数相同，则选灰度差更小的
            idx = min(candidates, key=lambda idx: (usage_count[idx], diffs[idx]))
            usage_count[idx] += 1
            result.paste(images[idx], (j*cell_size[0], i*cell_size[1]))
    return result

mosaic_img = match_images_to_pattern(images, pattern_array, cell_size)
mosaic_img.save(output_path)
print(f"生成完成，保存路径: {output_path}")