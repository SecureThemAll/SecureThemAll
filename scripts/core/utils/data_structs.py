from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List, AnyStr


@dataclass
class SOSRepairSettings:
    template: str
    work_dir: Path
    db_path: Path
    snippets: Tuple[int, int]
    max_susp_lines: int
    test_list: Path
    test_script: Path
    test_script_type: Path
    compile_script: Path
    faulty_code: Path
    method_range: Tuple[int, int]
    sosrepair: bool
    make_out: Path
    bulk_running_path: Path
    gcov_objects: Path
    num_rerun_tests: int = 1

    def attrs_to_dict(self):
        return {"WORKING_DIR": f"\"{self.work_dir}\"", "GENERATE_DB_PATH": f"\"{str(self.db_path)}\"",
                "LARGEST_SNIPPET": self.snippets[1], "SMALLEST_SNIPPET": self.snippets[0],
                "MAX_SUSPICIOUS_LINES": self.max_susp_lines, "TESTS_LIST": f"\"{str(self.test_list)}\"",
                "TEST_SCRIPT": f"\"{str(self.test_script)}\"", "TEST_SCRIPT_TYPE": f"\"{str(self.test_script_type)}\"",
                "COMPILE_SCRIPT": f"\"{str(self.compile_script)}\"", "FAULTY_CODE": f"\"{str(self.faulty_code)}\"",
                "METHOD_RANGE": str(self.method_range), "SOSREPAIR": str(self.sosrepair),
                "NUMBER_OF_TIMES_RERUNNING_TESTS": self.num_rerun_tests,
                "BULK_RUN_PATH": f"\"{str(self.bulk_running_path)}\"", "COMPILE_EXTRA_ARGS": str([]),
                "MAKE_OUTPUT": f"\"{str(self.make_out)}\"", "GCOV_OBJECTS": f"\"{str(self.gcov_objects)}\"",
                "EXCLUDE_SCANF": "False"}

    def write(self, out_path: Path) -> Path:
        settings_file = out_path / 'settings.py'

        with settings_file.open(mode="w+") as sf:
            sf.write(str(self))

        return settings_file

    def __str__(self):
        return f"{self.template}\n" + '\n'.join([f"{key} = {value}" for key, value in self.attrs_to_dict().items()]) + "\n"


@dataclass
class Patch:
    target_file: str
    edits: List[AnyStr]
    fix: str = ""

    def __len__(self):
        return len(self.edits)

    def is_fix(self):
        return self.fix and self.fix != ""

    def add_edit(self, edit: str):
        self.edits.append(edit)

    def to_dict(self):
        return {"target_file": self.target_file, "fix": self.fix, "edits": self.edits}

    def __str__(self):
        return str(self.to_dict())

