import json
import re
from pathlib import Path

from core.input_parser import add_repair_tool
from core.repair_tool import RepairTool
from core.runner.repair_task import RepairTask
from core.utils.data_structs import Patch


class CquenceR(RepairTool):
    """CquenceR"""

    def __init__(self, **kwargs):
        super(CquenceR, self).__init__(name="CquenceR", remove_patch=True, **kwargs)

    def repair(self, repair_task: RepairTask):
        """"
        :type repair_task: RepairTask
        """
        # checkouts the challenge binary to a temporary path
        # self.benchmark.compile(self.challenge, preprocess=True)

        try:
            repair_cmd = self._get_repair_cmd()

            if self.ssh_host:
                repair_cmd = self.write_run_script(repair_cmd)

            self.begin()
            super().__call__(cmd_str=repair_cmd, cmd_cwd=str(self.challenge.working_dir), ssh=True)
            self.end()

            for file_path in self.challenge.manifest():
                self._get_patches(file_path)

            return self.output

        finally:
            repair_task.status = self.repair_status()
            # self.dispose(challenge.working_dir)

    def _get_patches(self, target_file: Path):
        patch = Patch(target_file=str(target_file), edits=[])

        repaired_file = self.challenge.working_dir / Path("repair") / target_file
        baseline_file = self.challenge.source / target_file
        edits_path = self.challenge.working_dir / Path('patches')

        if repaired_file.exists():
            diff = self.diff(path=baseline_file, path_compare=repaired_file)
            patch.fix = diff

        if edits_path.exists():
            for f in edits_path.iterdir():
                if f.is_dir() and re.match(r"^\d{6}$", str(f.name)):
                    edit_file = f / target_file
                    if not edit_file.is_dir() and edit_file.stat().st_size > 0:
                        diff = self.diff(path=baseline_file, path_compare=edit_file)
                        patch.edits.append(diff)

        self.results.add_patch(patch)

    def write_manifest(self):
        manifest_file = self.challenge.working_dir / Path('hunk_manifest')

        with self.challenge.vuln.open(mode="r") as vf, manifest_file.open(mode="w") as mf:
            for file, hunk in json.load(vf).items():
                hunks = ""
                for start, lines in hunk.items():
                    size = len(lines)
                    hunks += f"{start},{int(start) + (size if size > 1 else 0)};"
                mf.write(f"{file}: {hunks}\n")

        return manifest_file

    def write_compile_script(self, compile_cmd: str) -> Path:
        compile_script_file = self.challenge.working_dir / "ceq_compile.sh"

        with compile_script_file.open(mode="w") as csf:
            csf.write(f"#!/bin/bash\n{compile_cmd} $@")
        compile_script_file.chmod(0o777)

        return compile_script_file

    def write_test_script(self) -> Path:
        test_script_file: Path = self.challenge.working_dir / "ceq_test.sh"
        log_file = self.challenge.working_dir / "tlog.txt"

        with test_script_file.open(mode="w") as tsf:
            test_cmd = self.benchmark.test(self.challenge, tests=["$1"], exit_fail=True, log_file=log_file)
            tsf.write(f"#!/bin/bash\n{test_cmd}")
        test_script_file.chmod(0o777)
        return test_script_file

    def _get_repair_cmd(self):
        arguments = self.tool_configs["arguments"]
        instrumented_files = [str(file) for file in self.challenge.manifest(prefix=self.challenge.source)]
        cmp_cmd, cmp_args = self.benchmark.compile(self.challenge, fix_files=["__SOURCE_NAME__"], separate=True,
                                                   instrumented_files=instrumented_files, sanity_check=self.sanity_check)
        arguments["--compile_script"] = f"\"{str(self.write_compile_script(cmp_cmd))}\""
        arguments["--compile_args"] = f"\"{cmp_args}\""
        arguments["--test_script"] = f"\"{str(self.write_test_script())} __TEST_NAME__\""
        arguments["--working_dir"] = str(self.challenge.working_dir)
        arguments["--prefix"] = str(self.challenge.source)
        arguments["--seed"] = str(self.seed)
        arguments["--verbose"] = ''
        arguments["--manifest_path"] = str(self.write_manifest())
        arguments["--pos_tests"] = str(self.challenge.pos_tests)
        arguments["--neg_tests"] = str(self.challenge.neg_tests)
        arguments["-v"] = ""

        repair_cmd = str(self.program)

        for opt, arg in arguments.items():
            if arg != "":
                repair_cmd += f" {opt} {arg}"
            else:
                repair_cmd += f" {opt}"

        return repair_cmd


def cquencer_args(input_parser):
    input_parser.add_argument('--version', action='version', version='1')


parser = add_repair_tool("CquenceR", CquenceR, 'Repair the challenge with CquenceR')
cquencer_args(parser)
