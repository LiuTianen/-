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
    ox.settings.log_console = True
    from shapely.ops import unary_union
    OSMN_AVAILABLE = True
except ImportError:
    OSMN_AVAILABLE = False
    print("警告: osmnx 未安装，将使用模拟模式（需手动提供坐标）")
    print("安装命令: pip install osmnx shapely")


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
                 dpi: int = 300):
        self.city_name = city_name
        self.style = style
        self.show_water = show_water
        self.show_boundary = show_boundary
        self.output_path = output_path or f"{self._safe_filename(city_name)}_map.png"
        self.figsize = figsize
        self.dpi = dpi
        self.markers: List[Marker] = []
        
        # 数据存储
        self.roads = []  # 道路线段列表
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
        ox.settings.timeout = 600 # 延长到10分钟
        ox.settings.use_cache = True
        
        # 如果你有本地代理，取消下面两行的注释
        # proxy = "http://127.0.0.1:7890"
        # ox.settings.proxies = {'http': proxy, 'https': proxy}
        try:
            print(f"正在下载 {self.city_name} 的 OSM 数据...")
            
            # 1. 获取道路网络
            G = ox.graph_from_place(self.city_name, network_type="all", simplify=True)
            self._extract_roads_from_graph(G)
            
            # 2. 获取边界
            boundary_gdf = ox.geocode_to_gdf(self.city_name)
            self.boundary = boundary_gdf.geometry.unary_union
            
            # 3. 获取水域
            if self.show_water:
                try:
                    water_gdf = ox.features_from_place(self.city_name, {'natural': 'water'})
                    water_geoms = water_gdf[water_gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])].geometry
                    water_union = unary_union(water_geoms)
                    self._extract_waters(water_union)
                except Exception as e:
                    print(f"  水域数据获取失败: {e}")
            
            # 4. 计算边界框
            self._calculate_bounds()
            
            print("数据下载完成！")
            return True
            
        except Exception as e:
            print(f"OSM 数据获取失败: {e}")
            return False
    
    def _extract_roads_from_graph(self, G):
        """从 osmnx 图中提取道路线段"""
        for u, v, data in G.edges(data=True):
            if 'geometry' in data:
                coords = list(data['geometry'].coords)
            else:
                node_u = G.nodes[u]
                node_v = G.nodes[v]
                coords = [(node_u['x'], node_u['y']), (node_v['x'], node_v['y'])]
            if len(coords) >= 2:
                self.roads.append(coords)
    
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
        for road in self.roads:
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
        self.roads = roads
        self.waters = waters or []
        self._calculate_bounds()
    
    def _draw_heart(self, ax, x: float, y: float, size: float, color: str):
        """绘制爱心标记"""
        t = np.linspace(0, 2*np.pi, 100)
        # 爱心参数方程，缩放适配坐标系
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
        
        # 2. 绘制水域
        if self.show_water:
            for water in self.waters:
                if len(water) >= 3:
                    water_patch = Polygon(water, closed=True,
                                         facecolor=self.style.water,
                                         edgecolor=self.style.water_edge,
                                         linewidth=0.6, alpha=0.7, zorder=2)
                    ax.add_patch(water_patch)
        
        # 3. 绘制道路
        for road in self.roads:
            if len(road) >= 2:
                xs = [p[0] for p in road]
                ys = [p[1] for p in road]
                ax.plot(xs, ys, color=self.style.road, 
                       linewidth=0.35, alpha=0.85, zorder=3)
        
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
        ax.text(0.98, -0.02, "data © OpenStreetMap", transform=ax.transAxes,
               fontsize=10, ha='right', va='top', 
               color=self.style.text_color, style='italic', alpha=0.7)
        
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
    
    # 基本参数
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
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建样式
    style = MapStyle.get_preset(args.style)
    
    # 创建生成器
    gen = CityMapGenerator(
        city_name=args.city,
        style=style,
        show_water=not args.no_water,
        show_boundary=not args.no_boundary,
        output_path=args.output,
        figsize=(args.width, args.height),
        dpi=args.dpi
    )
    
    # 添加标记点
    if args.markers:
        for marker_str in args.markers:
            try:
                marker = Marker.from_string(marker_str)
                gen.add_marker(marker)
            except ValueError as e:
                print(f"警告: {e}")
    
    # 获取数据
    if args.mock:
        # 模拟模式：从文件加载或内置示例
        if args.boundary_file and args.roads_file:
            boundary = load_json_data(args.boundary_file)
            roads = load_json_data(args.roads_file)
            gen.load_mock_data(boundary, roads)
        else:
            print("错误: mock模式需要提供 --boundary-file 和 --roads-file")
            sys.exit(1)
    else:
        # 在线模式：从OSM获取
        success = gen.fetch_osm_data()
        if not success and not OSMN_AVAILABLE:
            print("提示: 安装 osmnx 后重试: pip install osmnx shapely")
            sys.exit(1)
    
    # 生成地图
    gen.generate()


if __name__ == '__main__':
    main()