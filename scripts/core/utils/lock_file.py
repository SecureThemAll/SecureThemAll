#!/usr/bin/env python3

import time
import random

from pathlib import Path


class LockFile:
    def __init__(self, root: Path, file_name: str):
        self.root = root
        self.lock_file = root / Path(file_name)

    def __call__(self):
        file = self.lock_file.open(mode="w+")
        file.close()

    def is_lock(self):
        return self.lock_file.exists()

    def wait_lock(self):
        while self.is_lock():
            secs = random.randrange(2, 8)
            time.sleep(secs)

    def unlock(self):
        if self.lock_file.exists():
            self.lock_file.unlink()
