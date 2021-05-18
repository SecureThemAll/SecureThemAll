import re
from pathlib import Path

from core.input_parser import add_repair_tool
from core.repair_tool import RepairTool
from core.runner.repair_task import RepairTask
from core.utils.data_structs import Patch


class Prophet(RepairTool):
    """Prophet"""

    def __init__(self, name: str = None, **kwargs):
        super(Prophet, self).__init__(name=name if name else "Prophet", remove_patch=True, wrap_dir="program", **kwargs)

    def repair(self, repair_task: RepairTask):
        """"
        :type repair_task: RepairTask
        """

        try:
            repair_cmd = self._get_repair_cmd()

            if self.ssh_host:
                repair_cmd = self.write_run_script(repair_cmd)
                repair_cmd += f"; cp -rip {self.challenge.working_dir.parent / 'prophet/src/stats' } {self.challenge.working_dir}"
            self.begin()
            self.env["CBREPAIR"] = str(self.configuration.bench_paths.program)
            super().__call__(cmd_str=repair_cmd, cmd_cwd=str(self.challenge.working_dir.parent), ssh=True)
            self.end()

            for file_path in self.challenge.manifest():
                self._get_patches(file_path)

            return self.output

        finally:
            repair_task.status = self.repair_status()
            self.challenge.working_dir = self.challenge.working_dir.parent / Path("workdir", "src")
            # self.dispose(challenge.working_dir)

    def _get_patches(self, target_file: Path):
        patch = Patch(target_file=str(target_file), edits=[])
        target_file_path = self.challenge.source / target_file
        fixed_file_path = self.challenge.working_dir.parent / f"__fixed_{self.challenge.name / target_file}".replace("/", "_")
        edits_path = self.challenge.working_dir.parent / Path("workdir", "patches", target_file.parent)

        if target_file_path.exists():
            if fixed_file_path.exists():
                patch.fix = self.diff(target_file_path, fixed_file_path)

            if edits_path.exists():
                for file in edits_path.iterdir():
                    if not file.is_dir() and file.suffix == ".c" and file.stat().st_size > 0:
                        edit_diff = self.diff(target_file_path, file)
                        patch.edits.append(edit_diff.split("; void* memset(void*, int, unsigned long);")[-1])

        self.results.add_patch(patch)

    def write_revlog_file(self):
        rev_file = self.challenge.working_dir.parent / "tests.revlog"

        with rev_file.open(mode="w") as rf:
            diff_cases = f"Diff Cases: Tot {self.challenge.neg_tests}"
            first_neg_test = self.challenge.pos_tests + self.challenge.neg_tests
            neg_tests = ' '.join([str(i) for i in range(self.challenge.pos_tests + 1, first_neg_test + 1)])
            pos_cases = f"Positive Cases: Tot {self.challenge.pos_tests}"
            pos_tests = ' '.join([str(i) for i in range(1, self.challenge.pos_tests + 1)])
            reg_cases = "Regression Cases: Tot 0"
            rf.write(f"-\n-\n{diff_cases}\n{neg_tests}\n{pos_cases}\n{pos_tests}\n{reg_cases}\n")

        return rev_file

    def write_config_file(self, rev_file: Path, build_cmd: Path, test_cmd: Path):
        manifest_files = self.challenge.manifest(prefix=self.challenge.name)
        config_file = self.challenge.working_dir.parent / Path('run.conf')

        with config_file.open(mode="w") as cf:
            rev_str = f"revision_file={rev_file}"
            src_dir = f"src_dir={self.challenge.working_dir}"
            test_dir = f"test_dir={self.challenge.working_dir.parent / 'tests'}"
            loc = "localizer=profile"
            target_file = f"bugged_file={manifest_files[0]}"
            cf.write(f"{rev_str}\n{src_dir}\n{test_dir}\nbuild_cmd={build_cmd}\ntest_cmd={test_cmd}\n{target_file}\n{loc}")

        return config_file

    def _get_repair_cmd(self):
        arguments = self.tool_configs["arguments"]
        build_cmd = self.tool_configs["conf"]["build_cmd"]
        test_cmd = self.tool_configs["conf"]["test_cmd"]
        arguments["-dump-passed-candidate"] = self.challenge.working_dir.parent / "passed.txt"
        # Default is 5000 LOC
        #arguments["-first-n-loc"] = "1000"
        wd_pp = self.challenge.working_dir.parent / "workdir"
        (self.challenge.working_dir.parent / 'tests').mkdir(parents=True, exist_ok=True)
        arguments["-r"] = str(wd_pp)
        rev_file = self.write_revlog_file()
        repair_cmd = f"{self.tool_configs['program']} {self.write_config_file(rev_file, build_cmd, test_cmd)}"

        for opt, arg in arguments.items():
            if arg != "":
                repair_cmd += f" {opt} {arg}"
            else:
                repair_cmd += f" {opt}"

        return repair_cmd


def prophet_args(input_parser):
    input_parser.add_argument('--version', action='version', version='Prophet')


parser = add_repair_tool("Prophet", Prophet, 'Repair the challenge with Prophet')
prophet_args(parser)
