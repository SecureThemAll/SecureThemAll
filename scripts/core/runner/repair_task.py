#!/usr/bin/env python3

# from: https://github.com/program-repair/RepairThemAll/blob/8223384d1c354e6dea10c75d3db90b034ec11ae5/script/core/runner/RepairTask.py
import time
from pathlib import Path

from core.repair_tool import RepairTool
from ..setting import Setting


class RepairTask(Setting):

    def __init__(self,
                 tool: RepairTool,
                 challenge_name: str,
                 **kwargs):
        super(RepairTask, self).__init__(name="RepairTask", **kwargs)
        """"
        :type tool: RepairTool
        :type benchmark: Benchmark
        :type challenge_name: str
        """
        self.tool = tool
        self.challenge = challenge_name
        self._init_log_file(folder=Path(self.tool.name, self.challenge, str(self.tool.seed)),
                            file=Path("repair.log"))
        self.status = None
        self.starting_date = None
        self.end_date = None

    def run(self):
        self.starting_date = time.time()
        self.tool.init_challenge(challenge_name=self.challenge)
        output = self.tool.repair(self)
        self.tool.save()
        return output
