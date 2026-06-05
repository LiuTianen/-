# 🌹 玫瑰线 (Rose Curve)

极坐标方程 r = cos(kθ) 的可视化实现。

## 运行

### Web 版（推荐）
直接在浏览器打开 `index.html`，拖动滑块实时变换花瓣数量。
- 奇数 k → k 片花瓣
- 偶数 k → 2k 片花瓣
- 非整数 → 缠绕图案

### Python 版
```bash
python3 rose.py         # 默认 5 瓣
python3 rose.py 3       # 3 瓣玫瑰
python3 rose.py 2.5     # 复杂缠绕图案
```
需要图形界面（Tkinter），使用 turtle 内置库绘制。

## 数学

```
r = cos(kθ)

x = r·cos(θ)
y = r·sin(θ)
```

当 k 为有理数 p/q 时，曲线在 q 个完整周期后闭合。
