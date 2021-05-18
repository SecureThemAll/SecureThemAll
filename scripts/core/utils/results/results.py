import json
import dateutil.parser
from datetime import datetime, timedelta

from pathlib import Path
from typing import List, AnyStr
from core.utils.data_structs import Patch


class Results:
    def __init__(self, repair_begin: str = None, repair_end: str = None, patches: List[dict] = None, pos_tests: int = 0,
                 neg_tests: int = 0, compilations: int = 0, failed_compilations: int = 0, passed_neg_tests: int = 0,
                 passed_pos_tests: int = 0, failed_neg_tests: int = 0, failed_pos_tests: int = 0, duration: float = 0,
                 outcomes: dict = None, errors: List[AnyStr] = None, **kwargs):
        self.repair_begin = dateutil.parser.parse(repair_begin) if repair_begin else repair_begin
        self.repair_end = dateutil.parser.parse(repair_end) if repair_end else repair_end
        self.patches = Results.load_patches(patches) if patches else []
        self.compilations = compilations
        self.failed_compilations = failed_compilations
        self.pos_tests = pos_tests
        self.neg_tests = neg_tests
        self.passed_neg_tests = passed_neg_tests
        self.passed_pos_tests = passed_pos_tests
        self.failed_neg_tests = failed_neg_tests
        self.failed_pos_tests = failed_pos_tests
        self.outcomes = outcomes if outcomes else {}
        # in seconds
        self.duration = duration
        self.errors = errors if errors else []

    def __len__(self):
        return len(self.patches)

    def __call__(self, tracker: Path, errors: List[AnyStr]):
        self.calc_duration()
        self.errors = errors

        try:
            with tracker.open(mode="r") as tf:
                tracker = json.load(tf)

                for cid, outcome in tracker['outcomes'].items():
                    self.outcomes[cid] = outcome

                    if 'compiles' in outcome:
                        for compiles in outcome["compiles"]:
                            if compiles == 0:
                                self.compilations += 1
                            else:
                                self.failed_compilations += 1

                    if 'neg_tests' in outcome:
                        for nt, test_result in outcome["neg_tests"].items():
                            for tro in test_result:
                                if tro['outcome'] == 1:
                                    self.passed_neg_tests += 1
                                else:
                                    self.failed_neg_tests += 1

                    if 'pos_tests' in outcome:
                        for pt, test_result in outcome["pos_tests"].items():
                            for tro in test_result:
                                if tro['outcome'] == 1:
                                    self.passed_pos_tests += 1
                                else:
                                    self.failed_pos_tests += 1

        except FileNotFoundError as fnfe:
            self.errors.append(str(fnfe))

    def begin(self):
        self.repair_begin = datetime.now()

    def end(self):
        self.repair_end = datetime.now()

    def add_patch(self, patch: Patch):
        self.patches.append(patch)

    def calc_duration(self):
        if not self.repair_begin:
            self.begin()

        if not self.repair_end:
            self.end()

        delta: timedelta = self.repair_end - self.repair_begin
        self.duration = delta.total_seconds()

    @staticmethod
    def load(path: Path):
        with path.open(mode="r") as p:
            results = json.load(p)

            return Results(**results)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w") as res:
            json.dump(self.to_dict(), res, indent=2)

    @staticmethod
    def load_patches(patches: List[dict]) -> List[Patch]:
        return [Patch(target_file=patch["target_file"], fix=patch["fix"], edits=patch["edits"]) for patch in patches]

    def to_dict(self):
        return {"repair_begin": str(self.repair_begin), "repair_end": str(self.repair_end),
                "patches": [patch.to_dict() for patch in self.patches], "compilations": self.compilations,
                "failed_compilations": self.failed_compilations, "outcomes": self.outcomes,
                "neg_tests": self.neg_tests, "pos_tests": self.pos_tests,
                "passed_neg_tests": self.passed_neg_tests, "passed_pos_tests": self.passed_pos_tests,
                "failed_neg_tests": self.failed_neg_tests, "failed_pos_tests": self.failed_pos_tests,
                "duration": self.duration, "errors": self.errors}

    def __str__(self):
        return str(self.to_dict())
