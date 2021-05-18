#!/usr/bin/env python3

# based on: https://github.com/program-repair/RepairThemAll/blob/8223384d1c354e6dea10c75d3db90b034ec11ae5/script/core/RepairTool.py

import json
from pathlib import Path

from core.benchmark import Benchmark
from core.setting import Setting
from core.utils.results.results import Results


class RepairTool(Setting):
    def __init__(self, benchmark: Benchmark, ssh_tool: str = None, remove_patch: bool = False, wrap_dir: str = None,
                 **kwargs):
        super(RepairTool, self).__init__(ssh_host=ssh_tool, **kwargs)
        self.benchmark = benchmark
        self.results = Results()
        self.tool_config_path = self.configuration.paths.data_dir / Path(f"{self.name.lower()}.json")
        self.challenge = None
        self.remove_patch = remove_patch
        self.wrap_dir = wrap_dir
        self.sanity_check = False
        self.fault_localization = False
        self._set_tool_configs(ssh_tool)

        print(f"Discarded arguments {kwargs}")

    def _set_tool_configs(self, ssh_tool: str):
        if not self.tool_config_path.exists():
            raise ValueError(f"No such file {self.tool_config_path}.")

        with self.tool_config_path.open(mode="r") as tc:
            self.tool_configs = json.load(tc)
            self.path = Path(self.tool_configs['ssh_path']) if ssh_tool else self.get_repair_tools_path() / \
                                                                             self.tool_configs["path"]

            if "program" in self.tool_configs:
                self.program = self.path / Path(self.tool_configs["program"])
            else:
                raise ValueError(f"Tool binding failed. No program key in tool's configurations.")

            if "sanity_check" in self.tool_configs and isinstance(self.tool_configs["sanity_check"], bool):
                self.sanity_check = self.tool_configs["sanity_check"]

            if "fault_localization" in self.tool_configs and isinstance(self.tool_configs["fault_localization"], bool):
                self.fault_localization = self.tool_configs["fault_localization"]

        # checkouts the challenge binary to a temporary path

    def init_challenge(self, challenge_name: str):
        self.challenge = self.benchmark.init_challenge(self.name, challenge_name, remove_patch=self.remove_patch,
                                                       wrap_dir=self.wrap_dir)
        self._init_log_file(folder=Path(self.name, challenge_name), file=Path(f"tool_{self.seed}.log"))
        self.results.pos_tests = self.challenge.pos_tests
        self.results.neg_tests = self.challenge.neg_tests

    def diff(self, path: Path, path_compare: Path, cwd_path: Path = None):
        diff_cmd = f"diff {path} {path_compare}"
        out, err = super().__call__(cmd_str=diff_cmd, cmd_cwd=str(cwd_path) if cwd_path else cwd_path)

        if out:
            return out
        return ""

    def begin(self):
        self.results.begin()

    def end(self):
        self.results.end()

    def repair(self, repair_task):
        self.results.begin()
        self.results.end()
        repair_task.status = self.repair_status()
        self.save()
        pass

    def save(self):
        try:
            self.results(tracker=self.challenge.working_dir / '.tracker',
                         errors=self.error.splitlines() if self.error else [])
        except Exception as e:
            self._log(str(e))
        results_path = self.configuration.paths.out_dir / Path(self.name, self.challenge.name,
                                                               f"result_{self.seed}.json")
        self.results.save(path=results_path)

    def repair_status(self):
        if len(self.results) > 0:
            return "PATCHED"
        return "FINISHED"

    def __str__(self):
        return self.name

    def dispose(self, working_dir: Path):
        rm_cmd = f"rm -rf {working_dir}"
        super().__call__(cmd_str=rm_cmd)

    def write_run_script(self, repair_cmd: str, script_cwd: Path = None) -> str:
        run_script_file: Path = (
                                    self.challenge.working_dir.parent if self.wrap_dir else self.challenge.working_dir) / "run.sh"

        with run_script_file.open(mode="w") as rsf:
            rsf.write(f"#!/bin/bash\n{repair_cmd}")
        run_script_file.chmod(0o777)

        return f"\"cd {self.challenge.working_dir if not script_cwd else script_cwd}; {run_script_file}\""
