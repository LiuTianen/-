'''
Date: 2026-05-12 01:00:07
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-12 01:08:00
FilePath: \-\city_map\city_map_project\main.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from config import CITY

from renderer.map_loader import (
    load_graph,
    load_boundary
)

from renderer.draw import draw_map
from renderer.export import export


def main():

    print(f"Loading city: {CITY}")

    G = load_graph(CITY)

    boundary = load_boundary(CITY)

    print("Rendering...")

    fig, ax = draw_map(G, boundary)

    export(fig)

    print("Done.")


if __name__ == "__main__":
    main()