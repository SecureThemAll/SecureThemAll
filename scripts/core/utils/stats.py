from pathlib import Path

from core.utils.metrics import Metrics
from core.utils.results.results import Results

# Low bound constant
c = 10
genprog_def_err = "cat: /etc/redhat-release: No such file or directory\n"


def inv_eq(x: int, upper: int):
    return c ** (-x / upper)


class Stats(Results):
    def __init__(self, sanity_check: bool, fault_localization: bool, time_limit: int = 0, **kwargs):
        """"
        :fixes: original patches that fix the challenge
        :time_limit: tool's time_limit for solving the challenge
        """
        super(Stats, self).__init__(**kwargs)

        self.sc = sanity_check
        self.fl = fault_localization

        if not self.duration:
            self.calc_duration()

        # self.fixes = fixes if fixes else {}
        self._set_edits()
        self.time_limit = time_limit

    def __call__(self):
        # TODO: Fix this, similarity might be left out
        return Metrics(compile_success_rate=self.compilation_success_rate(),
                       pos_tests_success_rate=self.pos_tests_success_rate(),
                       neg_tests_success_rate=self.neg_tests_success_rate(),
                       edits_score=self.edits_score(),
                       fix_score=self.fix_score(),
                       time_score=self.time_score(),
                       repairability=self.repairability(),
                       maintainability=self.maintainability())

    @staticmethod
    def load(path: Path, time_limit: int, sanity_check: bool, fault_localization: bool):
        results = Results.load(path=path)
        res_dict = results.to_dict()
        return Stats(**res_dict, sanity_check=sanity_check, fault_localization=fault_localization,
                     time_limit=time_limit)

    def process_patch(self, file_name: str):
        for patch in self.patches:
            if not patch.is_fix():
                continue
            if patch.target_file == file_name:
                # TODO: fix this, not quite like this for multiple chunks
                return '\n'.join(patch.fix.split('---\n>')[-1].split('\n')[:-1])
        return []

    def _set_edits(self):
        # counts the total edits across patches
        self.edits = sum(
            [len(patch.edits) - 1 if patch.is_fix() else len(patch.edits) for patch in self.patches if len(patch) != 0])

    def regression(self):
        reg_score = []
        compiles = 0

        for cid, outcome in self.outcomes.items():
            if cid == 'sanity_check' or cid == 'fault_localization':
                continue

            if self.outcome_compiles(cid):
                compiles += 1
                passing_pos_tests = self.tests_pass(cid, 'pos_tests', count=True)

                if passing_pos_tests > 0:
                    reg_score.append(passing_pos_tests / self.pos_tests)
                else:
                    reg_score.append(0)

        if reg_score:
            sum_reg_score = sum(reg_score)

            if sum_reg_score > 0:
                return sum_reg_score / compiles

        return 0

    def repairability(self):
        repairability = []
        count = 0

        for cid, outcome in self.outcomes.items():
            if cid == 'sanity_check' or cid == 'fault_localization':
                continue

            if self.outcome_compiles(cid):
                if self.tests_pass(cid, 'pos_tests'):
                    count += 1
                    passing_neg_tests = self.tests_pass(cid, 'neg_tests', count=True)

                    if passing_neg_tests > 0:
                        repairability.append(passing_neg_tests / self.neg_tests)
                    else:
                        repairability.append(0)

        if repairability:
            sum_rep_score = sum(repairability)

            if sum_rep_score > 0:
                return sum_rep_score / count

        return 0

    def maintainability(self):
        maintainability = []
        count = 0

        for cid, outcome in self.outcomes.items():
            if cid == 'sanity_check' or cid == 'fault_localization':
                continue

            if self.outcome_compiles(cid):
                if self.tests_pass(cid, 'neg_tests'):
                    count += 1
                    passing_pos_tests = self.tests_pass(cid, 'pos_tests', count=True)

                    if passing_pos_tests > 0:
                        maintainability.append(passing_pos_tests / self.pos_tests)
                    else:
                        maintainability.append(0)

        if maintainability:
            sum_man_score = sum(maintainability)

            if sum_man_score > 0:
                return sum_man_score / count

        return 0


    def outcome_compiles(self, outcome: str):
        return 'compiles' in self.outcomes[outcome] and self.outcomes[outcome]['compiles'][-1] == 0

    def compilation_success_rate(self):
        if self.compilations == 0:
            return 0.0
        return self.compilations / (self.compilations + self.failed_compilations)

    def pos_tests_success_rate(self):
        if self.passed_pos_tests == 0:
            return 0.0
        return self.passed_pos_tests / (self.passed_pos_tests + self.failed_pos_tests)

    def neg_tests_success_rate(self):
        if self.passed_neg_tests == 0:
            return 0.0
        return self.passed_neg_tests / (self.passed_neg_tests + self.failed_neg_tests)

    def zero_tests(self):
        return self.no_passing_tests() and self.no_failing_tests()

    def no_passing_tests(self):
        return self.passed_pos_tests == 0 and self.passed_neg_tests == 0

    def no_failing_tests(self):
        return self.failed_neg_tests == 0 and self.failed_pos_tests == 0

    def fails(self):
        if not self.outcomes and not self.has_patches():
            return True
        return False

    def check(self, outcome: str, should_neg_fail: bool = False, should_pos_fail: bool = False):
        check_outcome = outcome in self.outcomes and self.all_tests_in_outcome(outcome=outcome)

        if should_neg_fail:
            return check_outcome and self.tests_pass(outcome=outcome, tests='pos_tests') and \
               not self.tests_pass(outcome=outcome, tests='neg_tests')

        if should_pos_fail:
            return check_outcome and not self.tests_pass(outcome=outcome, tests='pos_tests') and \
                   self.tests_pass(outcome=outcome, tests='neg_tests')

        return check_outcome and self.all_tests_pass(outcome=outcome)

    def sanity_check(self):
        return self.failed_neg_tests > 0 and self.passed_pos_tests > 0 and \
               self.check(outcome='sanity_check', should_neg_fail=True)

    def fault_localization(self):
        return self.failed_neg_tests > 0 and self.passed_pos_tests > 0 and \
               self.check(outcome='fault_localization', should_neg_fail=True)

    def undefined_positives(self):
        return self.failed_neg_tests == 0 and self.passed_pos_tests > 0

    def undefined_negatives(self):
        return self.failed_neg_tests > 0 and self.passed_pos_tests == 0

    def has_fix(self):
        return len([patch.fix for patch in self.patches if patch.is_fix()]) > 0

    def has_patches(self):
        return len([patch for patch in self.patches if len(patch.edits) > 0]) > 0

    def fix_score(self):
        edits = self.has_patches()
        has_fix = self.has_fix()
        has_passing_outcome = self.find_outcome_passes()
        has_complete_outcome = self.find_complete_outcome()

        if has_fix and has_passing_outcome:
            return 1

        elif has_fix and not has_passing_outcome:
            return 0.80

        elif edits and not has_fix and has_complete_outcome:
            return 0.80

        elif self.fails():
            return 0

        elif self.sc and not self.sanity_check():
            return 0.20

        elif self.fl and not self.fault_localization():
            return 0.40

        elif not edits and has_complete_outcome:
            return 0.60

        else:
            return 0

    def test_passes(self, outcome: str, tests: str, test_name: str):
        test = self.outcomes[outcome][tests][test_name]
        if not test:
            return False
        return 'outcome' in test[-1] and test[-1]['outcome'] == 1 and test[-1]['code'] == 0

    def tests_in_outcome(self, outcome: str, tests: str):
        if tests not in self.outcomes[outcome]:
            return False

        tests_count = self.pos_tests if tests == 'pos_tests' else self.neg_tests

        if len(self.outcomes[outcome][tests]) != tests_count:
            return False

        return True

    def all_tests_in_outcome(self, outcome: str):
        if outcome not in self.outcomes:
            return False
        return self.tests_in_outcome(outcome, 'pos_tests') and self.tests_in_outcome(outcome, 'neg_tests')

    def tests_pass(self, outcome: str, tests: str = None, count: bool = False):
        if not self.outcomes[outcome]:
            return False
        if tests:
            if not self.tests_in_outcome(outcome, tests):
                return False

            tests_pass = []

            for test in self.outcomes[outcome][tests].keys():
                if self.test_passes(outcome, tests, test):
                    tests_pass.append(1)

            tests_count = self.pos_tests if tests == 'pos_tests' else self.neg_tests

            if count:
                return sum(tests_pass)

            return sum(tests_pass) == tests_count

    def all_tests_pass(self, outcome: str):
        return self.tests_pass(outcome, 'neg_tests') and \
               self.tests_pass(outcome, 'pos_tests')

    def find_complete_outcome(self):
        for cid in self.outcomes:
            if self.check(outcome=cid, should_neg_fail=True):
                return True
            elif self.check(outcome=cid, should_pos_fail=True):
                return True
        return False

    def find_outcome_passes(self):
        #cid = list(self.outcomes.keys())
        #if cid:
        #    cid = cid[-1]
        #else:
        #    return False
        for cid in self.outcomes:
            if cid == 'sanity_check' or cid == 'fault_localization':
                continue
            if not self.all_tests_pass(cid):
                continue
            return True

    def vuln_fixes(self):
        pos_tests_vuln_fixes = []

        for cid in self.outcomes:
            if self.tests_pass(outcome=cid, tests='neg_tests'):
                test_passing = self.tests_pass(outcome=cid, tests='pos_tests', count=True)

                if 0 < test_passing < self.pos_tests:
                    pos_tests_vuln_fixes.append(test_passing / self.pos_tests)

        return pos_tests_vuln_fixes

    def edits_score(self):
        if not self.edits:
            return 0
        if not self.is_fixed():
            return 0
        return inv_eq(self.edits, 50)

    def is_fixed(self):
        return self.fix_score() == 1

    def time_score(self):
        # inversely proportional to the time limit
        # e^(-x/time_limit)
        if not self.duration:
            return 0.0
        if self.fix_score() < 0.6:
            return 0.0

        return inv_eq(self.duration, self.time_limit)

    def __str__(self):
        pass

