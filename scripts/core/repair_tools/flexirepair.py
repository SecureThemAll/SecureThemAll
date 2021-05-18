import re
from pathlib import Path

from core.input_parser import add_repair_tool
from core.repair_tool import RepairTool
from core.runner.repair_task import RepairTask
from core.utils.data_structs import Patch


class FlexiRepair(RepairTool):
    """FlexiRepair"""

    def __init__(self, name: str = None, **kwargs):
        super().__init__(name=name if name else "FlexiRepair", remove_path=True, **kwargs)

    def repair(self, repair_task: RepairTask):
        """"
        :type repair_task: RepairTask
        """
        #self.benchmark.compile(self.challenge, preprocess=True, save_temps=True, no_track=True)
        self.prefix = self.benchmark.prefix(self.challenge)

        try:
            repair_cmd = self._get_repair_cmd()

            if self.ssh_host:
                repair_cmd = self.write_run_script(repair_cmd)

            self.begin()
            super().__call__(cmd_str=repair_cmd, cmd_cwd=str(self.challenge.working_dir), ssh=True)
            self.end()

            for file_path in self.challenge.manifest(preprocessed=True):
                self._get_patches(file_path)

            return self.output

        finally:
            repair_task.status = self.repair_status()
            # self.dispose(challenge.working_dir)

    def _get_patches(self, target_file: Path):
        manifest_files = self.challenge.manifest(prefix=self.challenge.source)
        repair_file = self.challenge.working_dir / Path("repair", manifest_files[0].name)
        patterns_dir = self.challenge.working_dir / Path("patterns")
        patch = Patch(target_file=str(target_file), edits=[])

        if repair_file.exists():
            patch.fix = self.diff(path=manifest_files[0], path_compare=repair_file)

        if patterns_dir.exists():
            for pattern in patterns_dir.iterdir():
                with pattern.open(mode='r') as p:
                    patch.edits.append(p.read())

        self.results.add_patch(patch)

    def write_manifest(self):
        import json
        tests = [f"n{i+1}" for i in range(self.challenge.neg_tests)] + [f"p{i+1}" for i in range(self.challenge.pos_tests)]
        manifest_files = self.challenge.manifest(prefix=self.challenge.source)
        out_path = self.challenge.working_dir / Path('manifest.json')
        flexi_mainfest = {"working_dir": str(self.challenge.working_dir),
                          "source_file": str(manifest_files[0]),
                          "test_script": str(self.write_test_script()) + " TEST_NAME",
                          "tests": tests,
                          "compile_script": str(self.write_compile_script())}

        with out_path.open(mode="w") as op:
            json.dump(flexi_mainfest, op)

        return out_path

    def write_compile_script(self) -> Path:
        compile_script_file = self.challenge.working_dir / "compile_script.sh"
        log_file = self.challenge.working_dir / "clog.txt"

        with compile_script_file.open(mode="w") as csf:
            compile_cmd = self.benchmark.compile(self.challenge, log_file=log_file, sanity_check=self.sanity_check,
                                                 fault_localization=self.fault_localization)
            csf.write(f"#!/bin/bash\n{compile_cmd}")

        compile_script_file.chmod(0o777)
        return compile_script_file

    def write_test_script(self) -> Path:
        test_script_file: Path = self.challenge.working_dir / "test_script.sh"
        log_file = self.challenge.working_dir / "tlog.txt"

        with test_script_file.open(mode="w") as tsf:
            test_cmd = self.benchmark.test(self.challenge, tests=["$1"], exit_fail=True, log_file=log_file)
            tsf.write(f"#!/bin/bash\n{test_cmd}")
        test_script_file.chmod(0o777)
        return test_script_file

    def _get_repair_cmd(self):
        arguments = self.tool_configs["arguments"]
        arguments["-root"] = str(self.path / arguments["-root"])
        arguments["-prop"] = str(self.path / arguments["-prop"])
        arguments["--manifest_path"] = str(self.write_manifest())
        repair_cmd = "python " + str(self.program)

        for opt, arg in arguments.items():
            if arg != "":
                repair_cmd += f" {opt} {arg}"
            else:
                repair_cmd += f" {opt}"

        return repair_cmd


def flexi_args(input_parser):
    input_parser.add_argument('--version', action='version', version='FlexiRepair 26ccc50')


parser = add_repair_tool("FlexiRepair", FlexiRepair, 'Repair the challenge with FlexiRepair')
flexi_args(parser)
