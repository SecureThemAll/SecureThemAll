#!/usr/bin/env python3

from typing import List
from pathlib import Path

from core.repair_tool import RepairTool
from core.input_parser import add_repair_tool
from core.runner.repair_task import RepairTask
from distutils.dir_util import copy_tree
from core.utils.data_structs import Patch


def _regex_file(folder: Path, name: str, regex: str):
    re_file = folder / Path(name)

    with re_file.open(mode="w") as rf:
        rf.write(regex)
        return re_file


class MutApr(RepairTool):
    """MUT-APR"""

    def __init__(self, **kwargs):
        super(MutApr, self).__init__(name="MutApr", **kwargs)

    def repair(self, repair_task: RepairTask):
        """"
        :type repair_task: RepairTask
        """
        # checkouts the challenge binary to a temporary path
        # tool works with preprocessed files, makes part of the init
        self.benchmark.compile(self.challenge, preprocess=True, save_temps=True, no_track=True)

        try:
            self.begin()
            repair_dir = self.challenge.working_dir / self.configuration.dirs.repair
            prefix = self.benchmark.prefix(self.challenge)
            vuln_files = self.challenge.manifest(preprocessed=True)
            # instrument manifest files
            inst_files = self._instrument(files=vuln_files, prefix=prefix)

            if inst_files:
                self._coverage(inst_files=inst_files, prefix=prefix)

                for file in vuln_files:
                    repair_cwd = repair_dir / Path(file.parent, file.stem)
                    repair_cmd = self._get_repair_cmd(prefix / file, repair_dir=repair_cwd)

                    if self.ssh_host:
                        repair_cmd = self.write_run_script(repair_cmd, script_cwd=repair_cwd)

                    super().__call__(cmd_str=repair_cmd, cmd_cwd=repair_cwd, ssh=True)

                self.end()

                for file in vuln_files:
                    repair_cwd = repair_dir / Path(file.parent, file.stem)
                    self._get_patches(prefix=prefix, target_file=file, edits_path=repair_cwd)

            return self.output

        finally:
            repair_task.status = self.repair_status()
            # self.dispose(challenge.working_dir)

    def _get_patches(self, prefix: Path, target_file: Path, edits_path: Path):
        target_file_str = str(target_file)
        patch = Patch(target_file=str(target_file), edits=[])
        baseline_path = prefix / Path(target_file_str + "-baseline.c")
        best_path = prefix / Path(target_file_str + "--best.c")

        if baseline_path.exists():
            if best_path.exists():
                patch.fix = self.diff(baseline_path, best_path)

            if edits_path.exists():
                for file in edits_path.iterdir():
                    if not file.is_dir() and file.suffix == ".c" and file.stat().st_size > 0:
                        patch.edits.append(self.diff(baseline_path, file))

        self.results.add_patch(patch)

    def _instrument(self, files: List[Path], prefix: Path) -> List[str]:
        inst_path = self.challenge.working_dir / self.configuration.dirs.instrument
        inst_path.mkdir(parents=True, exist_ok=True)
        inst_files = []

        for file in files:
            out_path = inst_path / file.parent

            if not out_path.exists():
                out_path.mkdir()

            out_file = out_path / file.name
            args_str = ' '.join([f"{opt} {arg}" for opt, arg in self.tool_configs["inst"]["args"].items()])
            program_path = self.path / Path(self.tool_configs["inst"]["program"])
            inst_cmd = f"{program_path} {args_str} {prefix / file}"

            with out_file.open(mode="w") as inst_file:
                # TODO: Fix parsing errorFatal error: exception Frontc.ParseError from coverage program
                #  mainly with source code
                out, err = super().__call__(cmd_str=inst_cmd, ssh=True)
                # print(out, err)
                if err:
                    continue
                # TODO: fix this, for some reason the tool creates wrong path for coverage in the
                #  instrumented source code
                if out and out != '':
                    out = out.replace("fopen(\".//", 'fopen(\"/')
                    inst_file.write(out)
                    inst_files.append(str(out_file))

        return inst_files

    def _coverage(self, inst_files: List[str], prefix: str):
        self.benchmark.compile(self.challenge, inst_files, preprocess=True, cpp_files=True,
                               fault_localization=self.fault_localization)

        # creates folder for coverage files
        cov_dir = self.challenge.working_dir / self.configuration.dirs.coverage
        cov_dir.mkdir(parents=True, exist_ok=True)

        self.benchmark.test(challenge=self.challenge, pos_tests=True, coverage={"cov_out_dir": cov_dir,
                                                                                "rename_suffix": ".goodpath"})
        self.benchmark.test(challenge=self.challenge, neg_tests=True, coverage={"cov_out_dir": cov_dir})

        copy_tree(cov_dir, prefix)

    def write_compile_script(self, regex: str, repair_dir: str, target_file: str) -> Path:
        compile_script_file = self.challenge.working_dir / "mut_compile.sh"
        log_file = self.challenge.working_dir / "clog.txt"

        with compile_script_file.open(mode="w") as csf:
            compile_cmd = self.benchmark.compile(challenge=self.challenge, instrumented_files=[target_file],
                                                 regex=regex, prefix=repair_dir, cpp_files=True, log_file=log_file,
                                                 sanity_check=self.sanity_check)
            if self.ssh_host:
                compile_cmd = compile_cmd[:-1] + " $@" + compile_cmd[-1:]
            else:
                compile_cmd += " $@"
            csf.write(f"#!/bin/bash\n{compile_cmd}")
        compile_script_file.chmod(0o777)
        return compile_script_file

    def write_test_script(self, type: str, regex: str, repair_dir: str) -> Path:
        test_script_file: Path = self.challenge.working_dir / f"mut_test_{type}.sh"
        log_file = self.challenge.working_dir / "tlog.txt"

        with test_script_file.open(mode="w") as tsf:
            if type == "good":
                test_cmd = self.benchmark.test(challenge=self.challenge, regex=regex, pos_tests=True, exit_fail=True,
                                               prefix=repair_dir, log_file=log_file)
            else:
                test_cmd = self.benchmark.test(challenge=self.challenge, regex=regex, neg_tests=True, exit_fail=True,
                                               prefix=repair_dir, log_file=log_file)
            if self.ssh_host:
                test_cmd = test_cmd[:-1] + " $@" + test_cmd[-1:]
            else:
                test_cmd += " $@"
            tsf.write(f"#!/bin/bash\n{test_cmd}")
        test_script_file.chmod(0o777)
        return test_script_file

    def _get_repair_cmd(self, target_file: Path, repair_dir: Path):
        repair_dir.mkdir(parents=True, exist_ok=True)
        args_str = ' '.join([f"{opt} {arg}" for opt, arg in self.tool_configs["args"].items()])

        cre = _regex_file(self.challenge.working_dir, "compile.txt", self.tool_configs["regex"]["compile"])
        gre = _regex_file(self.challenge.working_dir, "good.txt", self.tool_configs["regex"]["good"])
        bre = _regex_file(self.challenge.working_dir, "bad.txt", self.tool_configs["regex"]["bad"])

        test_good = str(self.write_test_script(type="good", regex=str(gre), repair_dir=str(repair_dir)))
        test_bad = str(self.write_test_script(type="bad", regex=str(bre), repair_dir=str(repair_dir)))
        compile_cmd = str(self.write_compile_script(str(cre), repair_dir=str(repair_dir), target_file=str(target_file)))
        modify_cmd = str(self.program)
        modify_cmd = modify_cmd + f" {args_str} {target_file}"
        # fix_cmd += f" --faultpath {fl_out_file}"
        modify_cmd += f" --gcc \"{compile_cmd}\""
        modify_cmd += f" --good \"{test_good}\""
        modify_cmd += f" --bad \"{test_bad}\""

        return modify_cmd


def mut_apr_args(input_parser):
    input_parser.add_argument('--version', action='version', version='MUT-APR')


parser = add_repair_tool("MUT-APR", MutApr, 'Repair challenges with MUT-APR')
mut_apr_args(parser)
