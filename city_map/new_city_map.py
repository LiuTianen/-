#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用城市脉络图生成器
支持任意城市/地区，基于 OpenStreetMap 数据生成道路网络+水域+边界图

用法:
    python city_map.py --city "Jiujiang, Jiangxi, China"
    python city_map.py --city "Shanghai, China" --style dark
    python city_map.py --city "Beijing" --no-water --markers "116.4,39.9,天安门"
"""

import argparse
import sys
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import json

# ==================== 中文字体配置（必须在导入pyplot之前）====================
import matplotlib
matplotlib.rcParams['font.sans-serif'] = [
    'SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei',
    'Noto Sans CJK SC', 'Source Han Sans CN', 'DejaVu Sans'
]
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon, Circle
from matplotlib.path import Path
import numpy as np

# 尝试导入 osmnx，如果失败则使用模拟模式
try:
    import osmnx as ox
    ox.settings.use_cache = True
    ox.settings.log_console = False   # 关掉啰嗦的限速日志
    ox.settings.request_timeout = 120  # 请求超时
    # 使用国内 Overpass 镜像，加速数据下载
    # Overpass 镜像选一个可用的：
    # 1. overpass.kumi.systems — 欧洲镜像，稳定
    # 2. overpass-api.118899.xyz — 国内镜像，但大城市容易超时
    # 3. overpass.openstreetmap.fr — 法国镜像
    # 如果某个镜像不稳定，换个试试
    ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"
    ox.settings.request_timeout = 300  # 大城市查询需要更长时间
    OSMN_AVAILABLE = True
except ImportError:
    OSMN_AVAILABLE = False
    print("警告: osmnx 未安装，将使用模拟模式（需手动提供坐标）")
    print("安装命令: pip install osmnx shapely")


# ==================== 道路等级权重配置 ====================
# 值越大 → 线越粗
HIGHWAY_WIDTH = {
    'motorway':       1.2,
    'motorway_link':  0.8,
    'trunk':          1.0,
    'trunk_link':     0.7,
    'primary':        0.9,
    'primary_link':   0.6,
    'secondary':      0.7,
    'secondary_link': 0.5,
    'tertiary':       0.5,
    'tertiary_link':  0.4,
    'residential':    0.35,
    'living_street':  0.3,
    'service':        0.25,
    'unclassified':   0.3,
    'footway':        0.15,
    'cycleway':       0.18,
    'path':           0.12,
    'track':          0.2,
    'steps':          0.1,
    'pedestrian':     0.3,
    'default':        0.35,   # 未识别类型的兜底
}


# ==================== 数据类配置 ====================
@dataclass
class MapStyle:
    """地图配色方案"""
    name: str
    background: str
    water: str
    water_edge: str
    road: str
    city_edge: str
    city_fill: str
    marker_color: str
    text_color: str

    @classmethod
    def get_preset(cls, name: str) -> "MapStyle":
        presets = {
            'light': cls(
                name='light',
                background='#F5F0E6', water='#D4E5F7', water_edge='#7BAFD4',
                road='#1a1a1a', city_edge='#8B7355', city_fill='#E8E0D0',
                marker_color='#E74C3C', text_color='#333333'
            ),
            'dark': cls(
                name='dark',
                background='#1a1a2e', water='#16213e', water_edge='#0f3460',
                road='#e94560', city_edge='#533483', city_fill='#16213e',
                marker_color='#e94560', text_color='#eaeaea'
            ),
            'sepia': cls(
                name='sepia',
                background='#f4ecd8', water='#c9b99a', water_edge='#a89080',
                road='#4a3728', city_edge='#8b7355', city_fill='#e6d5b8',
                marker_color='#c0392b', text_color='#3e2723'
            ),
            'minimal': cls(
                name='minimal',
                background='#ffffff', water='#f0f0f0', water_edge='#cccccc',
                road='#000000', city_edge='#999999', city_fill='#fafafa',
                marker_color='#ff0000', text_color='#000000'
            ),
        }
        return presets.get(name, presets['light'])


@dataclass
class Marker:
    """地图标记点"""
    name: str
    lon: float
    lat: float
    style: str = 'star'  # star, heart, circle, diamond
    size: float = 12.0
    color: Optional[str] = None  # None 使用样式默认色

    @classmethod
    def from_string(cls, s: str) -> "Marker":
        """从字符串解析: "116.4,39.9,天安门" 或 "116.4,39.9,天安门,heart" """
        parts = s.split(',')
        if len(parts) < 3:
            raise ValueError(f"标记格式错误: {s}，应为: 经度,纬度,名称[,样式[,大小]]")
        lon, lat, name = float(parts[0]), float(parts[1]), parts[2]
        style = parts[3] if len(parts) > 3 else 'star'
        size = float(parts[4]) if len(parts) > 4 else 12.0
        return cls(name=name, lon=lon, lat=lat, style=style, size=size)


# ==================== 核心绘图类 ====================
class CityMapGenerator:
    """城市脉络图生成器"""

    MARKER_SHAPES = {
        'star': '*',
        'circle': 'o',
        'square': 's',
        'diamond': 'D',
        'triangle': '^',
        'cross': '+',
        'x': 'x',
    }

    def __init__(self, city_name: str, style: MapStyle,
                 show_water: bool = True, show_boundary: bool = True,
                 output_path: Optional[str] = None,
                 figsize: Tuple[float, float] = (16, 10),
                 dpi: int = 300,
                 fast_mode: bool = False):   # ← 【改进2】新增 fast_mode 参数
        self.city_name = city_name
        self.style = style
        self.show_water = show_water
        self.show_boundary = show_boundary
        self.output_path = output_path or f"{self._safe_filename(city_name)}_map.png"
        self.figsize = figsize
        self.dpi = dpi
        self.fast_mode = fast_mode       # ← 【改进2】
        self.markers: List[Marker] = []

        # 数据存储
        self.roads = []  # 现在每个元素是 (coords, width) — ← 【改进1】加粗度信息
        self.waters = []  # 水域多边形列表
        self.boundary = None  # 城市边界
        self.bounds = None  # (min_lon, min_lat, max_lon, max_lat)

    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        return name.replace(', ', '_').replace(' ', '_').replace('/', '_')

    def add_marker(self, marker: Marker):
        """添加标记点"""
        self.markers.append(marker)

    def fetch_osm_data(self) -> bool:
        """从 OpenStreetMap 获取真实数据"""
        if not OSMN_AVAILABLE:
            print("osmnx 不可用，跳过数据获取")
            return False

        # ============ 【改进2】大城市保护 ============
        # 先判断是不是大都市（粗略检测关键词）
        MEGA_CITIES = ['shanghai', 'beijing', 'guangzhou', 'shenzhen',
                       'tokyo', 'london', 'new york', 'mumbai', 'delhi',
                       'mexico city', 'cairo', 'dhaka', 'são paulo']
        city_lower = self.city_name.lower()
        is_mega = any(kw in city_lower for kw in MEGA_CITIES)

        if is_mega and not self.fast_mode:
            print(f"⚠ 检测到'{self.city_name}'是大城市，数据量可能很大")
            print(f"   当前耗时预计 2~10 分钟，内存消耗 1~4GB")
            print(f"   如需快速模式请加 --fast-mode")
            # 自动启用 fast_mode
            self.fast_mode = True
        # ===========================================

        ox.settings.use_cache = True

        # 如果你有本地代理，取消下面两行的注释
        # proxy = "http://127.0.0.1:7890"
        # ox.settings.proxies = {'http': proxy, 'https': proxy}

        # 重试用的镜像列表
        mirrors = [
            ox.settings.overpass_endpoint,  # 当前设置的镜像
            "https://overpass-api.118899.xyz/api/interpreter",
            "https://overpass.openstreetmap.fr/api/interpreter",
        ]

        for attempt, endpoint in enumerate(mirrors):
            if attempt > 0:
                print(f"  重试 {attempt}/{len(mirrors)-1}，切换镜像: {endpoint}")
                ox.settings.overpass_endpoint = endpoint
            else:
                print(f"正在下载 {self.city_name} 的 OSM 数据...")

            try:
                return self._do_fetch_osm_data()
            except Exception as e:
                err_msg = str(e)
                print(f"  镜像失败 ({endpoint}): {err_msg[:80]}...")
                if attempt < len(mirrors) - 1:
                    print(f"  切换镜像重试...")
                    continue
                else:
                    print(f"所有镜像均失败，放弃")
                    return False

        return False

    def _do_fetch_osm_data(self) -> bool:
        """单次 OSM 数据下载（被 fetch_osm_data 调用，支持重试）"""
        try:
            print(f"  正在查询路网数据...")

            # ----- 1. 获取道路网络 -----
            # 【改进1】在 fetch 时就保留 highway 类型
            network_type = "drive" if self.fast_mode else "all"
            # 【改进2】快速模式只下载行车道，大幅减少数据量
            G = ox.graph_from_place(self.city_name, network_type=network_type, simplify=True)
            self._extract_roads_from_graph(G)

            # ----- 2. 获取边界 -----
            boundary_gdf = ox.geocode_to_gdf(self.city_name)
            self.boundary = boundary_gdf.geometry.union_all()

            # ----- 3. 获取水域 + 河流 -----
            if self.show_water:
                # 【改进3】同时获取 natural=water（湖泊/海洋）和 waterway=river（河流）
                water_tags = {'natural': 'water'}
                river_tags = {'waterway': 'river'}

                try:
                    water_gdf = ox.features_from_place(self.city_name, water_tags)
                    water_geoms = water_gdf[water_gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])].geometry
                    if not water_geoms.empty:
                        water_union = water_geoms.union_all()
                        self._extract_waters(water_union)
                except Exception as e:
                    print(f"  水域数据获取失败: {e}")

                try:
                    river_gdf = ox.features_from_place(self.city_name, river_tags)
                    # 河流是 LineString，我们需要把它们画成细水域
                    river_lines = river_gdf[river_gdf.geometry.type == 'LineString']
                    for _, row in river_lines.iterrows():
                        geom = row.geometry
                        # 把线变成窄多边形（buffer 10米左右）
                        if geom.length > 50:  # 过滤太短的河段
                            buffered = geom.buffer(0.001)  # ~100m 宽度，可调
                            if buffered.geom_type == 'Polygon':
                                self.waters.append(list(buffered.exterior.coords))
                except Exception as e:
                    print(f"  河流数据获取失败: {e}")

            # ----- 4. 计算边界框 -----
            self._calculate_bounds()

            print("数据下载完成！")
            return True

        except Exception as e:
            print(f"OSM 数据获取失败: {e}")
            return False

    def _extract_roads_from_graph(self, G):
        """从 osmnx 图中提取道路线段，保留等级宽度信息"""
        # 【改进1】核心改动：根据 highway 类型分配线宽
        for u, v, data in G.edges(data=True):
            # 获取 highway 类型
            highway_type = data.get('highway', 'default')
            if isinstance(highway_type, list):
                highway_type = highway_type[0]  # 取第一个类型

            width = HIGHWAY_WIDTH.get(highway_type, HIGHWAY_WIDTH['default'])

            if 'geometry' in data:
                coords = list(data['geometry'].coords)
            else:
                node_u = G.nodes[u]
                node_v = G.nodes[v]
                coords = [(node_u['x'], node_u['y']), (node_v['x'], node_v['y'])]

            if len(coords) >= 2:
                # 【改进1】存储 (coords, width) 元组
                self.roads.append((coords, width))

    def _extract_waters(self, water_union):
        """提取水域多边形"""
        if water_union is None:
            return
        if water_union.geom_type == 'MultiPolygon':
            for geom in water_union.geoms:
                self.waters.append(list(geom.exterior.coords))
        else:
            self.waters.append(list(water_union.exterior.coords))

    def _calculate_bounds(self):
        """计算地图边界范围"""
        all_points = []
        for road, _ in self.roads:  # 【改进1】拆包 (coords, width)
            all_points.extend(road)
        for water in self.waters:
            all_points.extend(water)

        if all_points:
            lons = [p[0] for p in all_points]
            lats = [p[1] for p in all_points]
            padding = 0.05
            self.bounds = (
                min(lons) - padding, min(lats) - padding,
                max(lons) + padding, max(lats) + padding
            )

    def load_mock_data(self, boundary_coords: List[Tuple[float, float]],
                       roads: List[List[Tuple[float, float]]],
                       waters: List[List[Tuple[float, float]]] = None):
        """加载模拟数据（离线模式）"""
        self.boundary = boundary_coords
        # 【改进1】mock 模式下所有道路用默认宽度
        self.roads = [(road, HIGHWAY_WIDTH['default']) for road in roads]
        self.waters = waters or []
        self._calculate_bounds()

    def _draw_heart(self, ax, x: float, y: float, size: float, color: str):
        """绘制爱心标记"""
        t = np.linspace(0, 2*np.pi, 100)
        scale = size * 0.001
        hx = x + scale * 16 * np.sin(t)**3
        hy = y + scale * (13 * np.cos(t) - 5 * np.cos(2*t)
                         - 2 * np.cos(3*t) - np.cos(4*t))

        heart = mpatches.Polygon(list(zip(hx, hy)),
                                facecolor=color, edgecolor='white',
                                linewidth=1.5, zorder=10)
        ax.add_patch(heart)

    def _draw_marker(self, ax, marker: Marker):
        """绘制单个标记"""
        color = marker.color or self.style.marker_color

        if marker.style == 'heart':
            self._draw_heart(ax, marker.lon, marker.lat, marker.size, color)
        else:
            shape = self.MARKER_SHAPES.get(marker.style, '*')
            ax.plot(marker.lon, marker.lat, marker=shape,
                   markersize=marker.size, color=color,
                   markeredgecolor='white', markeredgewidth=1.5,
                   zorder=10)

        # 文字标签（带背景避免遮挡）
        ax.annotate(marker.name,
                   xy=(marker.lon, marker.lat),
                   xytext=(marker.lon + 0.02, marker.lat + 0.02),
                   fontsize=9, color=self.style.text_color,
                   fontweight='bold', zorder=11,
                   bbox=dict(boxstyle='round,pad=0.3',
                            facecolor=self.style.background,
                            edgecolor='none', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='#999999', lw=0.5)
                   if marker.style != 'heart' else None)

    def generate(self) -> str:
        """生成地图并保存，返回文件路径"""
        fig, ax = plt.subplots(figsize=self.figsize)
        fig.patch.set_facecolor(self.style.background)
        ax.set_facecolor(self.style.background)

        # 1. 绘制城市边界
        if self.show_boundary and self.boundary:
            if hasattr(self.boundary, 'geom_type'):  # shapely geometry
                if self.boundary.geom_type == 'MultiPolygon':
                    for geom in self.boundary.geoms:
                        x, y = geom.exterior.xy
                        ax.plot(x, y, color=self.style.city_edge,
                               linewidth=1.2, linestyle='--', alpha=0.6, zorder=1)
                else:
                    x, y = self.boundary.exterior.xy
                    ax.plot(x, y, color=self.style.city_edge,
                           linewidth=1.2, linestyle='--', alpha=0.6, zorder=1)
            else:  # 模拟数据（坐标列表）
                bx = [p[0] for p in self.boundary] + [self.boundary[0][0]]
                by = [p[1] for p in self.boundary] + [self.boundary[0][1]]
                ax.plot(bx, by, color=self.style.city_edge,
                       linewidth=1.2, linestyle='--', alpha=0.6, zorder=1)

        # 2. 绘制水域 + 河流
        if self.show_water:
            for water in self.waters:
                if len(water) >= 3:
                    water_patch = Polygon(water, closed=True,
                                         facecolor=self.style.water,
                                         edgecolor=self.style.water_edge,
                                         linewidth=0.6, alpha=0.7, zorder=2)
                    ax.add_patch(water_patch)

        # 3. 绘制道路（【改进1】按等级分线宽）
        for road, width in self.roads:
            if len(road) >= 2:
                xs = [p[0] for p in road]
                ys = [p[1] for p in road]
                ax.plot(xs, ys, color=self.style.road,
                       linewidth=width, alpha=0.85, zorder=3)

        # 4. 绘制标记点
        for marker in self.markers:
            self._draw_marker(ax, marker)

        # 5. 设置范围
        if self.bounds:
            ax.set_xlim(self.bounds[0], self.bounds[2])
            ax.set_ylim(self.bounds[1], self.bounds[3])

        # 6. 添加标题和版权
        city_display = self.city_name.split(',')[0] if ',' in self.city_name else self.city_name
        ax.text(0.98, 0.02, city_display, transform=ax.transAxes,
               fontsize=28, ha='right', va='bottom',
               color=self.style.text_color, fontweight='light')
        ax.text(0.98, -0.02, "data \u00a9 OpenStreetMap", transform=ax.transAxes,
               fontsize=10, ha='right', va='top',
               color=self.style.text_color, style='italic', alpha=0.7,
               fontfamily='DejaVu Sans')  # \u00a9=©, DejaVu Sans 有这个符号

        ax.set_axis_off()

        # 保存
        plt.tight_layout(pad=0)
        plt.savefig(self.output_path, dpi=self.dpi, bbox_inches="tight",
                   pad_inches=0.2, facecolor=self.style.background,
                   edgecolor="none")
        plt.close()

        print(f"地图已保存: {self.output_path}")
        return self.output_path


# ==================== 命令行接口 ====================
def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='生成城市脉络图（道路+水域+边界）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --city "Jiujiang, Jiangxi, China"
  %(prog)s --city "Shanghai" --style dark --dpi 600
  %(prog)s --city "Beijing" --no-water --markers "116.4,39.9,天安门,star,15"
  %(prog)s --mock --boundary-file boundary.json --roads-file roads.json
        """
    )

    parser.add_argument('--city', '-c', type=str, required=True,
                       help='城市名称（如: "Jiujiang, Jiangxi, China" 或 "Shanghai"）')

    # 样式参数
    parser.add_argument('--style', '-s', type=str, default='light',
                       choices=['light', 'dark', 'sepia', 'minimal'],
                       help='配色方案 (默认: light)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='输出图片DPI (默认: 300)')
    parser.add_argument('--width', type=float, default=16,
                       help='图片宽度 (默认: 16)')
    parser.add_argument('--height', type=float, default=10,
                       help='图片高度 (默认: 10)')

    # 显示控制
    parser.add_argument('--no-water', action='store_true',
                       help='不显示水域')
    parser.add_argument('--no-boundary', action='store_true',
                       help='不显示城市边界')

    # 【改进2】快速模式
    parser.add_argument('--fast-mode', action='store_true',
                       help='快速模式（仅下载行车道路网，适合大城市）')

    # 标记点
    parser.add_argument('--markers', '-m', type=str, nargs='+',
                       help='标记点列表，格式: "经度,纬度,名称[,样式[,大小]]"')

    # 输出
    parser.add_argument('--output', '-o', type=str,
                       help='输出文件路径（默认: 城市名_map.png）')

    # 离线模式（模拟数据）
    parser.add_argument('--mock', action='store_true',
                       help='使用模拟数据（不连接OSM）')
    parser.add_argument('--boundary-file', type=str,
                       help='边界坐标JSON文件（mock模式）')
    parser.add_argument('--roads-file', type=str,
                       help='道路坐标JSON文件（mock模式）')

    return parser


def load_json_data(filepath: str) -> list:
    """加载JSON坐标数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def main():
    """主入口"""

    # ============ 【改进4】全局异常兜底 ============
    try:
        parser = create_parser()
        args = parser.parse_args()

        # 创建样式
        style = MapStyle.get_preset(args.style)

        # 创建生成器（注入 fast_mode）
        gen = CityMapGenerator(
            city_name=args.city,
            style=style,
            show_water=not args.no_water,
            show_boundary=not args.no_boundary,
            output_path=args.output,
            figsize=(args.width, args.height),
            dpi=args.dpi,
            fast_mode=args.fast_mode,     # ← 【改进2】
        )

        # 解析标记点
        if args.markers:
            for m_str in args.markers:
                marker = Marker.from_string(m_str)
                gen.add_marker(marker)

        # 获取数据并生成
        if args.mock:
            # 离线模式
            if not args.boundary_file or not args.roads_file:
                print("错误: mock 模式需要 --boundary-file 和 --roads-file")
                sys.exit(1)
            boundary = load_json_data(args.boundary_file)
            roads = load_json_data(args.roads_file)
            gen.load_mock_data(boundary, roads)
        else:
            if not OSMN_AVAILABLE:
                print("错误: osmnx 未安装，无法在线获取数据")
                print("请运行: pip install osmnx shapely")
                print("或使用 --mock 离线模式")
                sys.exit(1)
            success = gen.fetch_osm_data()
            if not success:
                print("数据获取失败，终止生成")
                sys.exit(1)

        # 生成地图
        output = gen.generate()
        print(f"\n✅ 地图生成成功: {output}")

    except KeyboardInterrupt:
        print("\n\n用户中断，已退出")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生未预料错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    # ================================================


if __name__ == "__main__":
    main()
