'''
Date: 2026-05-12 01:00:33
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-12 01:01:59
FilePath: \-\city_map\city_map_project\config.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
CITY = "Jiujiang, Jiangxi, China"

OUTPUT_NAME = "jiujiang_city_art.png"

FIG_SIZE = (18, 10)

BACKGROUND_COLOR = "#ede9df"

ROAD_COLOR = "#222222"

BOUNDARY_COLOR = "#b8aa95"

TEXT_COLOR = "#222222"

FONT_SIZE = 30

DPI = 600

# 不同道路等级粗细
ROAD_WIDTH = {
    "motorway": 2.2,
    "trunk": 1.8,
    "primary": 1.3,
    "secondary": 0.9,
    "tertiary": 0.6,
    "residential": 0.25,
    "unclassified": 0.2,
    "service": 0.15
}