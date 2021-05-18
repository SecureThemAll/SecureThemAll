#!/usr/bin/env python3

# from: https://github.com/program-repair/RepairThemAll/blob/8223384d1c354e6dea10c75d3db90b034ec11ae5/script/core/renderer/EmptyRenderer.py

from core.runner.runner import Runner


class EmptyRenderer(object):
    def __init__(self, runner):
        """
        :param runner:
        :type runner: Runner
        """
        self.runner = runner
        pass

    def render(self):
        pass

    def render_final_result(self):
        pass
