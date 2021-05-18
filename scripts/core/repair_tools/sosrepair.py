from pathlib import Path

from core.input_parser import add_repair_tool
from core.repair_tool import RepairTool
from core.runner.repair_task import RepairTask
from core.utils.data_structs import SOSRepairSettings
from core.utils.data_structs import Patch
from core.utils.templates import sosrepair_settings_template


class SOSRepair(RepairTool):
    """SOSRepair"""

    def __init__(self, name: str = None, **kwargs):
        super(SOSRepair, self).__init__(name=name if name else "SOSRepair", remove_patch=True, **kwargs)

    def repair(self, repair_task: RepairTask):
        """"
        :type repair_task: RepairTask
        """
        # checkouts the challenge binary to a temporary path
        self.patches_dir = self.challenge.working_dir / "patches"
        self.target = self.challenge.manifest()[0]
        self.prefix = Path(self.benchmark.prefix(self.challenge))
        self.tmp_dir: Path = self.challenge.working_dir / "outputs"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.write_settings()

        try:
            repair_cmd = self.program

            if self.ssh_host:
                repair_cmd = f"\"cd {self.path}; ./run.sh\" 2>&1"

            self.begin()
            super().__call__(cmd_str=repair_cmd, ssh=True, cmd_cwd=str(self.challenge.working_dir))
            self.end()
            self._get_patches()

            return self.output

        finally:
            repair_task.status = self.repair_status()
            # self.dispose(challenge.working_dir)

    def _get_patches(self):
        target_file = self.challenge.manifest()[0]
        target_file_prefix = self.patches_dir / target_file.parent / (target_file.stem + '_sanity_check' + target_file.suffix)
        repair_dir: Path = self.challenge.working_dir / "repair"
        patch = Patch(target_file=str(target_file), edits=[])

        if target_file_prefix.exists():
            if repair_dir.exists():
                for patch_file in repair_dir.iterdir():
                    patch.fix = self.diff(path=target_file_prefix, path_compare=patch_file)
                    break

            if self.patches_dir.exists():
                for file in (self.patches_dir / target_file.parent).iterdir():
                    if 'fault_localization' in str(file) or 'sanity_check' in str(file):
                        continue
                    if file.suffix == ".c" and file.stat().st_size > 0:
                        edit_diff = self.diff(target_file_prefix, file)
                        patch.edits.append(edit_diff)

        self.results.add_patch(patch)

    def write_settings(self):
        vuln = self.challenge.read_vuln()
        vuln_ranges = [[(int(start), int(start) + len(lines)) for start, lines in vc.items()] for vf, vc in
                       vuln.items()]
        vuln_sizes = [vr[1] - vr[0] for vr in vuln_ranges[0]]
        make_out = self.tmp_dir / "make_out.txt"

        target_file = self.tmp_dir / self.target.name

        with (self.challenge.source / self.target).open(mode='r') as sf:
            lines_count = len(sf.read())

        self.benchmark.compile(self.challenge, gcc=True, no_status=True, coverage=True, preprocess=True,
                               write_build_args=make_out)
        target_source = self.challenge.source / self.target.parent
        start_range = vuln_ranges[0][0][0] - 10
        start_range = start_range if start_range >= 0 else 0
        end_range = vuln_ranges[0][-1][1] + 10
        end_range = end_range if end_range <= lines_count else lines_count
        settings = self.tool_configs["settings"]
        settings['log_path'] = str(self.challenge.working_dir)
        sosrepair_settings = SOSRepairSettings(template=sosrepair_settings_template(**settings),
                                               work_dir=self.challenge.working_dir,
                                               db_path=target_source, snippets=(min(vuln_sizes), max(vuln_sizes)+1),
                                               max_susp_lines=sum(vuln_sizes) + 10,
                                               test_list=self.write_tests_list(),
                                               test_script=self.write_test_script(), test_script_type="/bin/bash",
                                               compile_script=self.write_compile_script(),
                                               faulty_code=target_file,
                                               method_range=(start_range, end_range),
                                               sosrepair=self.tool_configs["settings"]["sosrepair"],
                                               gcov_objects=self.prefix / self.target.parent, make_out=make_out,
                                               bulk_running_path=target_source)

        settings_file = sosrepair_settings.write(out_path=self.challenge.working_dir)

        super().__call__(
            cmd_str=f"cp {self.challenge.source / self.target} {target_file}",
            cmd_cwd=str(self.challenge.working_dir))
        # copy settings file from the working_dir to the tool's source
        super().__call__(cmd_str=f"cp {settings_file} {self.path}",
                         ssh=True, cmd_cwd=str(self.challenge.working_dir))

    def write_tests_list(self) -> Path:
        test_list_path = self.challenge.working_dir / "tests-list.txt"

        with test_list_path.open(mode="w") as tl:
            for t in list(range(1, self.challenge.neg_tests + 1)):
                tl.write(f"n{t}\n")
            for t in list(range(1, self.challenge.pos_tests + 1)):
                tl.write(f"p{t}\n")

        return test_list_path

    def write_test_script(self) -> Path:
        test_script_file: Path = self.challenge.working_dir / "sos_test.sh"
        log_file = self.challenge.working_dir / "tlog.txt"

        with test_script_file.open(mode="w") as tsf:
            test_cmd = self.benchmark.test(self.challenge, tests=["$1"], print_class=True, exit_fail=True,
                                           log_file=log_file, gcov=True)
            tsf.write(f"#!/bin/bash\n{test_cmd}")
        test_script_file.chmod(0o777)
        return test_script_file

    def write_compile_script(self) -> Path:
        compile_script_file = self.challenge.working_dir / "sos_compile.sh"
        log_file = self.challenge.working_dir / "clog.txt"

        with compile_script_file.open(mode="w") as tsf:
            compile_cmd = self.benchmark.compile(self.challenge, coverage=True, log_file=log_file, gcc=True,
                                                 backup=self.patches_dir, fault_localization=True, sanity_check=True)
            tsf.write(
                f"#!/bin/bash\ncp {self.tmp_dir / self.target.name} {self.challenge.source / self.target}\n{compile_cmd}")
        compile_script_file.chmod(0o777)
        return compile_script_file


def sosrepair_args(input_parser):
    input_parser.add_argument('--version', action='version', version='SOSRepair 966bb1e')


parser = add_repair_tool("SOSRepair", SOSRepair, 'Repair the challenge with SOSRepair')
sosrepair_args(parser)
