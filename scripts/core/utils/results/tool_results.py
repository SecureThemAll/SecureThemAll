import json

from pathlib import Path
from typing import List
from core.utils.stats import Stats
from core.utils.metrics import Metrics


class ChallengeResults:
    def __init__(self, path: Path, name: str, timeout: int, sanity_check: bool, fault_localization: bool):
        self.path = path
        self.name = name

        if not self.path.exists():
            self.stats = Stats(sanity_check=sanity_check, fault_localization=fault_localization)
        else:
            self.stats = Stats.load(sanity_check=sanity_check, fault_localization=fault_localization,
                                    path=path, time_limit=timeout)

        self.metrics = self.stats()

    def __add__(self, other):
        if not isinstance(other, ChallengeResults):
            return NotImplemented

        return self.metrics + other.metrics

    def __truediv__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        return self.metrics / other


class ToolResults:
    def __init__(self, path: Path, timeout: int, configs: Path, seed: int = 0):
        self.name = path.name

        with configs.open(mode="r") as c:
            self.configs = json.load(c)

        self.sanity_check = False
        self.fault_localization = False

        if "sanity_check" in self.configs and isinstance(self.configs["sanity_check"], bool):
            self.sanity_check = self.configs["sanity_check"]

        if "fault_localization" in self.configs and isinstance(self.configs["fault_localization"], bool):
            self.fault_localization = self.configs["fault_localization"]

        self.path = path
        self.seed = seed
        self.challenge_results = [ChallengeResults(path=Path(challenge, f"result_{self.seed}.json"),
                                                   name=challenge.name, sanity_check=self.sanity_check,
                                                   fault_localization=self.fault_localization,
                                                   timeout=timeout) for challenge in path.iterdir() if challenge.is_dir()]
        self.size = len(self.challenge_results)
        self.metrics: Metrics = None

    def __call__(self, all_fixes: dict) -> Metrics:
        if not self.metrics:
            metrics = Metrics()
            others_fixes = all_fixes.copy()
            del others_fixes[self.name]

            for cr in self.challenge_results:
                others_cr_fixes = [1 if fixes[cr.name] else 0 for tn, fixes in others_fixes.items()]
                sum_others_cr_fixes = sum(others_cr_fixes)
                if cr.metrics.fix_score == 1:
                    if sum_others_cr_fixes == 0:
                        cr.metrics.uniqueness = 1
                    else:
                        inverse = len(others_cr_fixes) - sum_others_cr_fixes
                        cr.metrics.uniqueness = inverse / len(others_cr_fixes)
                cr.metrics.fix_score = cr.metrics.fix_score if cr.metrics.fix_score >= 0.6 else 0
                metrics += cr.metrics

            self.metrics = metrics / self.size

        return self.metrics

    def get_fixes(self):
        return {cr.name: cr.stats.is_fixed() for cr in self.challenge_results}

    def get_duration(self):
        return sum(cr.stats.duration for cr in self.challenge_results)

    def check_dates(self):
        pass

    def challenges_fixed(self):
        return [cr.path.parent.name for cr in self.challenge_results if cr.stats.is_fixed() == 1]

    @staticmethod
    def challenges_fix_score(challenge_results: List[ChallengeResults] = None):
        if not challenge_results:
            return []
        return [cr.stats.fix_score() for cr in challenge_results]

    def challenges_fix_score_dict(self, challenge_results: List[ChallengeResults] = None):
        if not challenge_results:
            challenge_results = self.challenge_results
        return {cr.name: cr.stats.fix_score() for cr in challenge_results}

    def challenges_vuln_fixes(self, challenge_results: List[ChallengeResults] = None):
        vuln_fixes = []

        if not challenge_results:
            challenge_results = self.challenge_results

        for cr in challenge_results:
            vuln_fixes.extend(cr.stats.vuln_fixes())

        return vuln_fixes

    def group_by_cwe_type(self, cwe_types: dict, cwe_type: str):
        return {cr.name: cr for cr in self.challenge_results if cwe_types[cr.name] == cwe_type}

    def fix_score_cwe_type(self, cwe_types: dict, cwe_type: str):
        group = self.group_by_cwe_type(cwe_types, cwe_type)
        cns, crs = group.keys(), group.values()
        res = self.challenges_fix_score(list(crs))

        print('\t' + self.name, len(cns), len(res))
        return cns, res

    def vuln_fixes_cwe_type(self, cwe_types: dict, cwe_type: str):
        group = self.group_by_cwe_type(cwe_types, cwe_type)
        cns, crs = group.keys(), group.values()

        return cns, self.challenges_vuln_fixes(list(crs))
