# ☁️ 云朵生成器 · Cloud Generator

用**柏林噪声 (Perlin Noise)** 算法生成独一无二的云朵。
每朵云有唯一 ID，「这片云只属于你」。

## 原理

```
随机种子 → Perlin Noise 2D → 多倍频叠加 (FBM) → 阈值裁切 → 立体着色
```

- **分形布朗运动 (FBM)**：5~7 层噪声叠加，低频决定大形状，高频增加绒毛边缘
- **平滑阶跃 (smoothstep)**：阈值附近渐变过渡，边缘蓬松自然
- **立体光影**：上方偏白（模拟阳光），下方偏灰紫（阴影）

## 文件

| 文件 | 说明 |
|------|------|
| `cloud.py`   | Python turtle 版（纯内置库） |
| `index.html` | Web Canvas 交互版 |

## 使用

### Web 版

浏览器打开 `index.html`：
- 🎲 **生成新云** — 每次都不同，宇宙唯一
- 🌅☀️🌇🌙 **四种天空** — 朝霞 / 晴空 / 黄昏 / 夜空
- 📸 **截图保存** — 带云 ID 水印的 PNG
- 💫 云朵缓缓呼吸 + 飘移动画

### Python 版

```bash
python3 cloud.py                # 随机种子
python3 cloud.py 42             # 指定种子（可复现）
python3 cloud.py 42 dawn        # 种子 + 主题
```

主题：`dawn`（朝霞） `clear`（晴空） `dusk`（黄昏） `night`（夜空）

## 唯一 ID

每朵云基于随机种子生成 6 位唯一 ID（如 `CLOUD-A7F3K2`），截图中永久留存。

## 技术栈

- Python: 纯内置 `turtle` + `random` + `math`，零依赖。Perlin Noise 从零实现。
- Web: Canvas 2D API，Perlin Noise JS 从零实现。
