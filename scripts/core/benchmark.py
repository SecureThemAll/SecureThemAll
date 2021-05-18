#!/usr/bin/env python3

import shutil

from pathlib import Path
from typing import List

from core.challenge import Challenge
from core.setting import Setting
from .utils.lock_file import LockFile


class Benchmark(Setting):
    """Benchmark"""

    def __init__(self, debug: bool = False, ssh_bench: str = None, **kwargs):
        super(Benchmark, self).__init__(name="Benchmark", ssh_host=ssh_bench, **kwargs)
        self.paths = self.configuration.bench_paths
        self.challenges = None
        self.verbose = True
        self.debug = debug

        self._init_log_file(folder=Path("benchmark", str(self.seed)),
                            file=Path("benchmark.log"))
        self.get_challenges()

    def _get_challenge_info(self, name):
        challenge = self.get_challenge(name)

        if challenge is not None:
            return challenge.get_info()

        return None

    def init_challenge(self, tool_name: str, challenge_name: str, remove_patch: bool = False,
                       wrap_dir: str = None) -> Challenge:
        wd = Path(self.configuration.paths.working_dir, tool_name, f"{challenge_name}_{self.seed}")
        if wrap_dir:
            wd = wd / wrap_dir
        lock = LockFile(self.configuration.paths.root, self.configuration.lock_file)
        cmd_str = self.checkout(working_directory=wd, challenge_name=challenge_name, remove_patch=remove_patch)

        if wd.exists():
            shutil.rmtree(wd.parent if wrap_dir else wd)
        try:
            lock.wait_lock()
            lock()
            _, _ = super().__call__(cmd_str=cmd_str, msg=f"Checking out challenge {challenge_name} to {wd}.\n",
                                    exit_err=True)
            pos_tests, neg_tests = self.count_tests(working_directory=wd, challenge_name=challenge_name)
            return Challenge(name=challenge_name, working_dir=wd, pos_tests=pos_tests, neg_tests=neg_tests)
        finally:
            lock.unlock()

    def get_challenges(self):
        if not self.challenges:
            cmd_str = f"{self.paths.program} catalog"
            cmd_str = self.ssh_cmd(cmd_str)
            out, err = super().__call__(cmd_str=cmd_str, msg="Querying benchmarks challenges")

            self.challenges = out.splitlines()

        return self.challenges

    def checkout(self, working_directory: Path, challenge_name: str, remove_patch: bool = False):
        cmd_str = f"{self.paths.program} checkout -wd {working_directory} -cn {challenge_name}"

        if self.debug:
            cmd_str += " -v"

        if remove_patch:
            cmd_str += " -rp"

        return self.ssh_cmd(cmd_str)

    def make(self, challenge: Challenge, gcc: bool = False, replace: bool = False, save_temps: bool = False,
             exit_err: bool = True, script: bool = False, call: bool = False, no_status: bool = False,  log_file: str = None,
             compiler_trail_path: bool = False, build_args_file: str = None, include_args: str = None):
        cmd_str = f"{self.paths.program} make -wd {challenge.working_dir} -cn {challenge.name}"

        if gcc:
            cmd_str += " --gcc"

        if compiler_trail_path:
            cmd_str += " --compiler_trail_path"

        if no_status:
            cmd_str += " --no_status"

        if replace:
            cmd_str += " --replace"

        if save_temps:
            cmd_str += " --save_temps"

        if include_args:
            cmd_str += f" --include_args {include_args}"

        if exit_err:
            cmd_str += " --exit_err"

        if script:
            cmd_str += " --script"

        if log_file:
            cmd_str += f" -l {log_file}"

        if build_args_file:
            cmd_str += f" --build_args_file {build_args_file}"

        if self.debug:
            cmd_str += " -v"

        if call:
            out, err = super().__call__(cmd_str=cmd_str, ssh=True, msg=f"Making {challenge.name}.\n")

            if out:
                return out
            return err

        return self.ssh_cmd(cmd_str)

    def compile(self, challenge: Challenge, instrumented_files: List[str] = None, preprocess=False, regex: str = None,
                prefix: str = None, log_file: str = None, fix_files: List[str] = None, cpp_files: bool = False,
                separate: bool = False, coverage: bool = False, no_status: bool = False, gcc: bool = False,
                script: bool = False, call: bool = False, save_temps: bool = False, sanity_check: bool = False,
                fault_localization: bool = False, no_track: bool = False, write_build_args: Path = None,
                backup: Path = None):
        cmd_str = f"{self.paths.program} compile -wd {challenge.working_dir} -cn {challenge.name}"
        cmd_flags = ""

        if instrumented_files:
            inst_files_str = ' '.join(instrumented_files)
            cmd_flags += f" -ifs {inst_files_str}"

        if fix_files:
            fix_files_str = ' '.join(fix_files)
            cmd_flags += f" -ffs {fix_files_str}"

        if cpp_files:
            cmd_flags += f" -cpp"

        if gcc:
            cmd_flags += f" --gcc"

        if regex:
            cmd_flags += f" -r {regex}"

        if prefix:
            cmd_flags += f" -pf {prefix}"

        if log_file:
            cmd_flags += f" -l {log_file}"

        if coverage:
            cmd_flags += f" --coverage"

        if save_temps:
            cmd_flags += f" --save_temps"

        if no_status:
            cmd_flags += f" --no_status"

        if sanity_check:
            cmd_str += f" -sc"

        if fault_localization:
            cmd_flags += f" -fl"

        if no_track:
            cmd_flags += f" --no_track"

        if script:
            cmd_str += " --script"

        if write_build_args:
            cmd_str += f" --write_build_args {write_build_args}"

        if backup:
            cmd_str += f" --backup {backup}"

        if self.debug:
            cmd_str += " -v"

        if preprocess or call:
            out, err = super().__call__(cmd_str=cmd_str + cmd_flags, ssh=True,
                                        msg=f"Compiling {challenge.name}.\n")

            if out:
                return out
            return err

        if separate:
            return self.ssh_cmd(cmd_str), cmd_flags

        cmd = cmd_str + cmd_flags

        if self.ssh_host:
            cmd = f"\"{cmd}\""

        return self.ssh_cmd(cmd)

    def test(self, challenge: Challenge, tests: List[str] = None, pos_tests: bool = False, neg_tests: bool = False,
             exit_fail: bool = False, write_fail: bool = False, out_file: str = None, coverage: dict = None,
             regex: str = None, prefix: str = None, log_file: str = None, neg_pov: bool = False,
             only_numbers: bool = False, no_status: bool = False, print_ids: bool = False, gcov: bool = False,
             print_class: bool = False):
        cmd_str = f"{self.paths.program} test"

        if coverage or gcov:
            cmd_str += f"-coverage"

        cmd_str = f"{cmd_str} -wd {challenge.working_dir} -cn {challenge.name}"

        if tests:
            tests_str = ' '.join(tests)
            cmd_str += f" -tn {tests_str}"
        elif pos_tests:
            cmd_str += " --pos_tests"
        elif neg_tests:
            cmd_str += " --neg_tests"

        if exit_fail:
            cmd_str += " -ef"

        if write_fail:
            cmd_str += " -wf"

        if neg_pov:
            cmd_str += " -np"

        if only_numbers:
            cmd_str += " --only_numbers"

        if no_status:
            cmd_str += f" --no_status"

        if print_ids:
            cmd_str += f" --print_ids"

        if print_class:
            cmd_str += f" --print_class"

        if gcov:
            cmd_str += f" --gcov"

        if out_file:
            cmd_str += f" -of {out_file}"

        if regex:
            cmd_str += f" -r {regex}"

        if prefix:
            cmd_str += f" -pf {prefix}"

        if log_file:
            cmd_str += f" -l {log_file}"

        if self.debug:
            cmd_str += " -v"

        if coverage:
            cmd_str += " " + ' '.join([f"--{opt} {arg}" for opt, arg in coverage.items()])
            out, err = super().__call__(cmd_str=cmd_str, msg=f"Testing {challenge.name}.\n", ssh=True)

            if out:
                return out
            return err

        if self.ssh_host:
            cmd_str = f"\"{cmd_str}\""

        return self.ssh_cmd(cmd_str)

    def prefix(self, challenge: Challenge):
        cmd_str = f"{self.paths.program} info --kind prefix -wd {challenge.working_dir} -cn {challenge.name}"
        out, err = super().__call__(cmd_str=cmd_str, msg=f"Querying {challenge.name}'s prefix.\n", ssh=True)

        if not err:
            return out.splitlines()[0]

        return ""

    def patch(self, challenge_name: str):
        cmd_str = f"{self.paths.program} patch -cn {challenge_name}"
        out, err = super().__call__(cmd_str=cmd_str, ssh=True)

        if err:
            return ""

        return out

    def count_tests(self, challenge_name: str, working_directory: Path):
        cmd_str = f"{self.paths.program} info --kind count_tests -wd {working_directory} -cn {challenge_name}"

        if not self.ssh_host:
            cmd_str += "-l {self.log_file}"

        out, err = super().__call__(cmd_str=cmd_str, exit_err=True, ssh=True,
                                    msg=f"Querying {challenge_name}'s tests count.\n")
        out_split = out.splitlines()[0].split(" ")
        return int(out_split[0]), int(out_split[1])
