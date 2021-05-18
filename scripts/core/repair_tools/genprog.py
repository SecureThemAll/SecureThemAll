import re
from pathlib import Path

from core.input_parser import add_repair_tool
from core.repair_tool import RepairTool
from core.runner.repair_task import RepairTask
from core.utils.data_structs import Patch


class GenProg(RepairTool):
    """GenProg"""

    def __init__(self, name: str = None, **kwargs):
        super().__init__(name=name if name else "GenProg", **kwargs)

    def repair(self, repair_task: RepairTask):
        """"
        :type repair_task: RepairTask
        """
        self.benchmark.compile(self.challenge, preprocess=True, save_temps=True, no_track=True)
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
        repaired_file = self.challenge.working_dir / Path("repair") / target_file
        sanity_file = self.challenge.working_dir / Path("sanity") / target_file
        patch = Patch(target_file=str(target_file), edits=[])

        if sanity_file.exists():
            if repaired_file.exists():
                diff = self.diff(path=sanity_file, path_compare=repaired_file)
                patch.fix = diff

            for f in self.challenge.working_dir.iterdir():
                if f.is_dir() and re.match(r"^\d{6}$", str(f.name)):
                    edit_file = f / target_file
                    if not edit_file.is_dir() and edit_file.stat().st_size > 0:
                        diff = self.diff(path=sanity_file, path_compare=edit_file)
                        patch.edits.append(diff)

        self.results.add_patch(patch)

    def write_manifest(self):
        manifest_files = self.challenge.manifest(preprocessed=True)
        out_path = self.challenge.working_dir / Path('gen_prog_manifest.txt')

        with out_path.open(mode="w") as op:
            for file in manifest_files:
                op.write(f"{file}\n")

        return out_path

    def write_compile_script(self) -> Path:
        compile_script_file = self.challenge.working_dir / "gp_compile.sh"
        log_file = self.challenge.working_dir / "clog.txt"
        instrumented_files = [str(file) for file in self.challenge.manifest(prefix=self.prefix, preprocessed=True)]

        with compile_script_file.open(mode="w") as csf:
            compile_cmd = self.benchmark.compile(self.challenge, fix_files=["$1"], cpp_files=True, log_file=log_file,
                                                 instrumented_files=instrumented_files, sanity_check=self.sanity_check,
                                                 fault_localization=self.fault_localization)
            csf.write(f"#!/bin/bash\n{compile_cmd}")
        compile_script_file.chmod(0o777)
        return compile_script_file

    def write_test_script(self) -> Path:
        test_script_file: Path = self.challenge.working_dir / "gp_test.sh"
        log_file = self.challenge.working_dir / "tlog.txt"

        with test_script_file.open(mode="w") as tsf:
            test_cmd = self.benchmark.test(self.challenge, tests=["$1"], exit_fail=True, log_file=log_file)
            tsf.write(f"#!/bin/bash\n{test_cmd}")
        test_script_file.chmod(0o777)
        return test_script_file

    def _get_repair_cmd(self):
        arguments = self.tool_configs["arguments"]
        arguments["--compiler-command"] = f"\"{str(self.write_compile_script())} __SOURCE_NAME__\""
        arguments["--test-command"] = f"\"{str(self.write_test_script())} __TEST_NAME__\""
        arguments["--prefix"] = self.prefix
        arguments["--pos-tests"] = str(self.challenge.pos_tests)
        arguments["--neg-tests"] = str(self.challenge.neg_tests)
        arguments["--rep"] = "cilpatch" if self.challenge.manifest.multi_file else "c"
        arguments["--program"] = str(self.write_manifest())
        repair_cmd = str(self.program)

        for opt, arg in arguments.items():
            if arg != "":
                repair_cmd += f" {opt} {arg}"
            else:
                repair_cmd += f" {opt}"

        return repair_cmd


def genprog_args(input_parser):
    input_parser.add_argument('--version', action='version', version='GenProg e720256')


parser = add_repair_tool("GenProg", GenProg, 'Repair the challenge with GenProg')
genprog_args(parser)
