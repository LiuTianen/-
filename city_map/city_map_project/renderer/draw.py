'''
Date: 2026-05-12 01:01:10
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-12 01:06:33
FilePath: \-\city_map\city_map_project\renderer\draw.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
import matplotlib.pyplot as plt
import osmnx as ox

from config import *
from renderer.style import get_road_width


def draw_map(G, boundary):
    PADDING_RATIO = 0.08

    minx, miny, maxx, maxy = boundary.total_bounds

    width = maxx - minx
    height = maxy - miny

    pad_x = width * PADDING_RATIO
    pad_y = height * PADDING_RATIO

    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)

    ax.set_aspect("equal")
    fig, ax = plt.subplots(
        figsize=FIG_SIZE,
        facecolor=BACKGROUND_COLOR
    )

    # 行政边界
    boundary.boundary.plot(
        ax=ax,
        edgecolor=BOUNDARY_COLOR,
        linewidth=1,
        linestyle="--"
    )

    # 道路绘制
    edges = ox.graph_to_gdfs(G, nodes=False)

    for _, row in edges.iterrows():

        geom = row.geometry
        highway = row.get("highway", "residential")

        width = get_road_width(highway)

        if geom.geom_type == "LineString":

            x, y = geom.xy

            ax.plot(
                x,
                y,
                color=ROAD_COLOR,
                linewidth=width,
                solid_capstyle="round",
                alpha=0.95
            )

        elif geom.geom_type == "MultiLineString":

            for line in geom.geoms:

                x, y = line.xy

                ax.plot(
                    x,
                    y,
                    color=ROAD_COLOR,
                    linewidth=width,
                    solid_capstyle="round",
                    alpha=0.95
                )

    # 去坐标轴
    ax.set_axis_off()

    # 城市名称
    ax.text(
        0.98,
        0.05,
        CITY.split(",")[0],
        transform=ax.transAxes,
        ha="right",
        fontsize=FONT_SIZE,
        color=TEXT_COLOR
    )
    
    return fig, ax