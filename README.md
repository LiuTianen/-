# - ✨ 浪漫代码合集

> 用代码写诗，用数学画爱。

## 🗂️ 项目目录

### 🌹 玫瑰线 · Rose Curve
极坐标曲线 `r = cos(kθ)` — 花瓣数随参数变化的数学之美。

- [`rose/rose.py`](rose/rose.py) — Python turtle 动画绘制
- [`rose/index.html`](rose/index.html) — Web Canvas 交互版
  - 🎚️ 拖动滑块变换花瓣数 k (1~10)
  - 🎨 渐变色 + 粒子漂浮特效

```bash
python3 rose/rose.py 5   # 5瓣玫瑰
```

### 🦋 蝴蝶曲线 · Butterfly Curve
Temple Fay 的参数方程 — 展翅般的优雅图案。

- [`butterfly/butterfly.py`](butterfly/butterfly.py) — Python turtle 绘制
- [`butterfly/index.html`](butterfly/index.html) — Web Canvas 交互版
  - 🎚️ 调整轨迹周期 & 缩放
  - 🎨 四种颜色主题（经典蓝紫 / 日落橙 / 翡翠绿 / 银白）

```bash
python3 butterfly/butterfly.py 2   # 2倍精度
```

### ❤️ 心形方程画廊 · Heart Equation Gallery
6 条经典心形数学方程 — 交互切换，每条配一句浪漫情话。

- [`heart-gallery/index.html`](heart-gallery/index.html) — Web Canvas 画廊
  - ⬅️➡️ 6 条方程自由切换（笛卡尔心形线 / 隐式心形 / 参数心形 / 倾斜之心 / 繁花心形 / 爱之根式）
  - ⟳ 自动轮播 + 键盘操作
  - 🎨 每条独立配色，粒子光晕

```bash
# 浏览器直接打开即可
open heart-gallery/index.html
```

### ☁️ 云朵生成器 · Cloud Generator
Perlin 噪声算法生成独一无二的云朵 — 每朵云有唯一 ID。

- [`cloud/cloud.py`](cloud/cloud.py) — Python turtle 版（纯内置库）
- [`cloud/index.html`](cloud/index.html) — Web Canvas 交互版
  - 🎲 一键生成新云 · 📸 截图保存
  - 🌅☀️🌇🌙 四种天空主题（朝霞/晴空/黄昏/夜空）
  - 💫 云朵呼吸飘移 + 唯一 ID 水印

```bash
python3 cloud/cloud.py           # 随机云朵
python3 cloud/cloud.py 42 dawn   # 种子 + 主题
```

### 💚 代码雨表白 · Code Rain Confession
输入名字 → Matrix 代码雨 → 弹簧物理汇聚成名字 → 浪漫揭示。

- [`code-rain/code_rain.py`](code-rain/code_rain.py) — Python turtle 版（纯内置库）
- [`code-rain/index.html`](code-rain/index.html) — Web Canvas 全屏交互版
  - ⌨️ 输入 TA 的名字 + Enter
  - 🌧️ Matrix 代码雨（日文片假名 + 数字 + 符号）
  - 🧲 弹簧物理汇聚 → 颜色绿渐变粉
  - ❤️ 名字发光成形 + 揭示文案

```bash
python3 code-rain/code_rain.py 张三     # Python 版
open code-rain/index.html               # Web 版
```

### 💕 Love Rain · cmatrix --love
黑客帝国风格，但下落的是 ❤️🌸💕 — 五种 emoji 主题随心切换。

- [`love-rain/love_rain.py`](love-rain/love_rain.py) — Python turtle 版（纯内置库）
- [`love-rain/index.html`](love-rain/index.html) — Web Canvas 全屏交互版
  - 🖱️ 点击绽放心动（粒子炸裂）
  - ⌨️ 空格切换 5 种主题（全模式/红心/花雨/星尘/粉彩）
  - 🌫️ 拖尾 + 光晕 + 正弦摇摆物理

```bash
python3 love-rain/love_rain.py     # Python 版
open love-rain/index.html          # Web 版
```

### ❤️ 爱心代码
多种方式绘制爱心的 Python 脚本集合。

| 脚本 | 说明 |
|------|------|
| `heart.py` | 标准爱心 |
| `cover_heart.py` | 封面级爱心 |
| `love.py` | 带文字浪漫版 |
| `cake.py` | 爱心蛋糕 |
| `ivy.py` / `ivy_c.py` | Ivy 定制版 |
| `very_love.py` | 高甜度版本 |

```bash
cd 爱心代码 && python3 love.py
```

### 💌 Miss You
Flask Web 应用 — 表达思念的互动页面。

```bash
cd miss_you/miss_you_web && python3 app.py
```

### 🗺️ City Map
城市地图生成器 — 生成定制城市地图。

```bash
cd city_map && python3 city_map_new.py
```

### 🖼️ Pho
图片处理工具。

---

## 🚀 运行依赖

所有 Python 项目均为内置库（`turtle`、`colorsys`、`math`）或标准 Flask，零额外依赖。

Web 版直接浏览器打开即可。

---

*"Mathematics is the language with which God has written the universe." — Galileo*

*代码即情书。*
