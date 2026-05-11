'''
Date: 2026-05-12 01:01:16
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-12 01:02:25
FilePath: \-\city_map\city_map_project\renderer\export.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from config import OUTPUT_NAME, DPI


def export(fig):

    fig.savefig(
        f"output/{OUTPUT_NAME}",
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0.1
    )