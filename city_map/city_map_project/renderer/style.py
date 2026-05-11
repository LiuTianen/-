'''
Date: 2026-05-12 01:00:58
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-12 01:10:19
FilePath: \-\city_map\city_map_project\renderer\style.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from config import ROAD_WIDTH


def get_road_width(highway_type):

    if isinstance(highway_type, list):
        highway_type = highway_type[0]

    return ROAD_WIDTH.get(highway_type, 0.2)