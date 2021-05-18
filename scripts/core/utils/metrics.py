

class Metrics:
    def __init__(self, compile_success_rate: float = 0, pos_tests_success_rate: float = 0, regression: float = 0,
                 neg_tests_success_rate: float = 0, edits_score: float = 0, fix_score: float = 0, time_score: float = 0,
                 repairability: float = 0, maintainability: float = 0, uniqueness: float = 0):
        self.compile_success_rate = compile_success_rate
        self.pos_tests_success_rate = pos_tests_success_rate
        self.neg_tests_success_rate = neg_tests_success_rate
        self.edits_score = edits_score
        self.fix_score = fix_score
        self.time_score = time_score
        self.score = self.compile_success_rate + self.edits_score + self.time_score
        self.regression = regression
        self.repairability = repairability
        self.maintainability = maintainability
        self.uniqueness = uniqueness

    def __call__(self, *args, **kwargs) -> dict:
        return {
            "compile success rate": self.compile_success_rate,
            "positive tests\nsuccess rate": self.pos_tests_success_rate,
            "negative tests\nsuccess rate": self.neg_tests_success_rate,
            "edits score": self.edits_score,
            "duration score": self.time_score,
            "repairability": self.repairability,
            "maintainability": self.maintainability,
            "uniqueness": self.uniqueness
        }

    def performance(self):
        return {"efficiency": self.efficiency(), "effectiveness": self.effectiveness()}

    def efficiency(self) -> float:
        return self.edits_score + self.time_score

    def effectiveness(self):
        return self.compile_success_rate + self.uniqueness + self.maintainability + self.repairability + self.fix_score

    def __add__(self, other):
        if not isinstance(other, Metrics):
            return NotImplemented

        return Metrics(self.compile_success_rate + other.compile_success_rate,
                       self.pos_tests_success_rate + other.pos_tests_success_rate,
                       self.regression + other.regression,
                       self.neg_tests_success_rate + other.neg_tests_success_rate,
                       self.edits_score + other.edits_score,
                       self.fix_score + other.fix_score,
                       self.time_score + other.time_score,
                       self.repairability + other.repairability,
                       self.maintainability + other.maintainability,
                       self.uniqueness + other.uniqueness)

    def __truediv__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        compile_success_rate = self.compile_success_rate / other if self.compile_success_rate != 0 else 0
        pos_tests_success_rate = self.pos_tests_success_rate / other if self.pos_tests_success_rate != 0 else 0
        neg_tests_success_rate = self.neg_tests_success_rate / other if self.neg_tests_success_rate != 0 else 0
        edits_score = self.edits_score / other if self.edits_score != 0 else 0
        fix_score = self.fix_score / other if self.fix_score != 0 else 0
        time_score = self.time_score / other if self.time_score != 0 else 0
        regression = self.regression / other if self.regression != 0 else 0
        repairability = self.repairability / other if self.repairability != 0 else 0
        maintainability = self.maintainability / other if self.maintainability != 0 else 0
        uniqueness = self.uniqueness / other if self.uniqueness != 0 else 0

        return Metrics(compile_success_rate, pos_tests_success_rate, regression, neg_tests_success_rate, edits_score,
                       fix_score, time_score, repairability, maintainability, uniqueness)
