#!/usr/bin/env python3
import json
from pathlib import Path
from typing import List

from .utils.parse import c_to_cpp


class Challenge:
    def __init__(self, name: str, working_dir: Path, pos_tests: int, neg_tests: int):
        self.name = name
        self.working_dir = working_dir
        self.source = working_dir / name
        self.manifest = Manifest(path=self.source / Path("manifest"))
        self.vuln = self.source / Path("vuln")
        self.pos_tests = pos_tests
        self.neg_tests = neg_tests

    def __str__(self):
        return f"{self.name}: {self.manifest}"

    def read_vuln(self):
        with self.vuln.open(mode="r") as vf:
            return json.load(vf)


class Manifest:
    def __init__(self, path: Path):
        self.path = path
        self.files = []
        self.preprocessed = []

        if self.path.exists():
            with self.path.open(mode="r") as m:
                files = m.read().splitlines()

                for file in files:
                    file_path = file.split(':')[0]
                    self.files.append(file_path)
                    cpp_file_name = c_to_cpp(file_path)
                    self.preprocessed.append(cpp_file_name)

        self.multi_file = len(self.files) > 1

    def __call__(self, preprocessed: bool = False, prefix: Path = None) -> List[Path]:
        if preprocessed:
            if prefix:
                return [prefix / Path(cpp_file) for cpp_file in self.preprocessed]
            return [Path(file) for file in self.preprocessed]

        if prefix:
            return [prefix / Path(file) for file in self.files]
        return [Path(file) for file in self.files]

    def __str__(self, preprocessed=False, prefix: Path = None):
        return ' '.join([str(file) for file in self(preprocessed=preprocessed, prefix=prefix)])
