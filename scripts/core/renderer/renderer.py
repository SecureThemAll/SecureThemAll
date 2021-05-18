#!/usr/bin/env python3

# from: https://github.com/program-repair/RepairThemAll/blob/8223384d1c354e6dea10c75d3db90b034ec11ae5/script/core/renderer/renderer.py

import os

from .bash_renderer import BashRenderer
from .empty_renderer import EmptyRenderer

def get_renderer(runner, output_path):
    """
    :param runner:
    :return: EmptyRenderer
    """
    return BashRenderer(runner, output_path)
