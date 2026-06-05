# 🦋 蝴蝶曲线 · Butterfly Curve

**Temple Fay 的经典参数曲线** — 形如蝴蝶展翅的优美数学图案。

## 数学公式

```
x = sin(t) · (e^cos(t) − 2cos(4t) − sin⁵(t/12))
y = cos(t) · (e^cos(t) − 2cos(4t) − sin⁵(t/12))
```

t ∈ [0, 2π·L]  其中 L 为轨迹周期数

## 文件

| 文件 | 说明 |
|------|------|
| `butterfly.py` | Python turtle 绘制（需图形界面） |
| `index.html`  | Web Canvas 交互版（浏览器直接打开） |

## 使用

### Web 版

直接用浏览器打开 `index.html`：
- 🎚️ **轨迹周期**：调整 t 的范围 (1~8 圈)，更多周期 = 更多翅膀细节
- 🔍 **缩放**：调整蝴蝶尺寸
- 🎨 **颜色主题**：经典蓝紫 / 日落橙 / 翡翠绿 / 银白
- ▶️ **动画绘制**：可见绘制过程，支持暂停
- ✨ 粒子漂浮 + 光晕特效

### Python 版

```bash
python3 butterfly.py          # 默认精度
python3 butterfly.py 2        # 2倍精度，更细腻
python3 butterfly.py 4        # 4倍精度
```

## 技术栈

- Python: 纯内置 `turtle` + `colorsys`，零依赖
- Web: Canvas 2D API，无外部库
