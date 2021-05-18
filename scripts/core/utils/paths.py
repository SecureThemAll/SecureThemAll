#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConfigDirs:
    coverage: Path
    instrument: Path
    repair: Path


@dataclass
class BenchPaths:
    root: Path
    program: Path

    def validate(self):
        return self.root.exists() and self.program.exists()


@dataclass
class ConfigPaths:
    root: Path
    src: Path
    working_dir: Path
    out_dir: Path
    log_dir: Path
    data_dir: Path
    plots_dir: Path
    repair_tools: Path

    def validate(self):
        return self.src.exists() and self.root.exists() \
               and self.working_dir.exists() and self.out_dir.exists() and self.plots_dir.exists() \
               and self.repair_tools.exists() and self.log_dir.exists() and self.data_dir.exists()
