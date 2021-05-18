#!/usr/bin/env python3

from dataclasses import dataclass
from os.path import dirname, abspath
from pathlib import Path
from core.utils.paths import ConfigPaths, BenchPaths, ConfigDirs

ROOT_DIR = dirname(dirname(__file__))
SOURCE_DIR = dirname(abspath(__file__))


@dataclass
class Configuration:
    paths: ConfigPaths
    bench_paths: BenchPaths
    dirs: ConfigDirs
    lock_file: str
    tools_timeout: int  # In seconds
    command_timeout: int  # In seconds
    local_threads: int

    def validate(self):
        return self.paths.validate() and self.bench_paths.validate() \
               and self.tools_timeout > 0 and self.local_threads > 0

    def set_bench_root(self, rel_bench_path: str):
        rbp = Path(rel_bench_path)
        self.bench_paths = BenchPaths(root=rbp, program=rbp / Path("src", "cb_repair.py"))

    def set_working_dir(self, wd: str):
        self.paths.working_dir = Path(wd)


config_paths = ConfigPaths(root=Path(ROOT_DIR),
                           src=Path(SOURCE_DIR),
                           working_dir=Path("/tmp"),
                           out_dir=Path(ROOT_DIR, "results"),
                           log_dir=Path(ROOT_DIR, "logs"),
                           data_dir=Path(ROOT_DIR, "data"),
                           plots_dir=Path(ROOT_DIR, "plots"),
                           repair_tools=Path(ROOT_DIR, "repair_tools")
                           )

bench_root = Path(ROOT_DIR, "benchmark", "cb-repair")
bench_paths = BenchPaths(
    root=bench_root,
    program=bench_root / Path("src", "cb_repair.py")
)

config_dirs = ConfigDirs(
    coverage=Path("coverage"),
    instrument=Path("instrument"),
    repair=Path("repair")
)

configuration = Configuration(
    paths=config_paths,
    bench_paths=bench_paths,
    dirs=config_dirs,
    lock_file="LOCK_CHALS_INIT",
    tools_timeout=3600,
    command_timeout=30,
    local_threads=1
)
