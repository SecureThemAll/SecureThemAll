#!/usr/bin/env python3
import subprocess
import sys
import psutil

from typing import IO, Union, AnyStr, Tuple, Dict, List
from pathlib import Path
from threading import Timer

# 50 MB
LIST_SIZE_LIMIT = 50000000
COMMAND_OUTPUT_DUMP_FILE = 'command_dump.txt'


def print_error(*args, **kwargs):
    print(args, file=sys.stderr, **kwargs)


def list_gt_size_limit(lst: List):
    """
        Checks the memory usage of a list (takes into account only primitive object)
    """
    return sys.getsizeof(lst) > LIST_SIZE_LIMIT


def dump_list_to_file(lst: List):
    """
        Checks the memory usage of a list (takes into account only primitive object)
    """
    with open(COMMAND_OUTPUT_DUMP_FILE, 'a') as f:
        f.write('\n'.join(lst))
    print_error(f"Dropped command output with size {sys.getsizeof(lst)} bytes to {COMMAND_OUTPUT_DUMP_FILE}")


# https://stackoverflow.com/a/54775443
def _timer_out(p: subprocess.Popen):
    print("Command timed out")
    process = psutil.Process(p.pid)
    
    for proc in process.children(recursive=True):
        proc.kill()
    
    process.kill()


class Command:
    def __init__(self, command, cwd: str = None):
        self.out = None
        self.err = None

        if isinstance(command, str):
            self.shell = True
        elif isinstance(command, list):
            self.shell = False
        else:
            raise ValueError("Command must be a string or a list.")

        self.command = command
        self.cwd = cwd

    def _exec(self, proc: subprocess.Popen):
        self.out = []

        for line in proc.stdout:
            self.out += line

            if self.verbose:
                print(line, end="")

            if self.file:
                self._write(line)

            if list_gt_size_limit(self.out):
                # dump_list_to_file(self.out)
                self.out = []

        proc.wait()

        if proc.returncode and proc.returncode != 0:
            proc.kill()
            self.err = proc.stderr.read()

            if not self.err:
                self.err = "Unexpected crash"

            # if self.verbose:
            #    print(self.err)

            if self.file and self.err:
                self._write(self.err)

    def _write(self, msg: AnyStr):
        if isinstance(self.file, Path):
            with self.file.open(mode="a") as f:
                f.write(msg)
        else:
            self.file.write(msg)

    def __call__(self,
                 verbose: bool = False,
                 timeout: int = None,
                 exit_err: bool = False,
                 env: Dict[AnyStr, AnyStr] = None,
                 file: Union[IO, Path] = None) -> Tuple[Union[str, None], Union[str, None]]:

        self.verbose = verbose
        self.file = file

        # based on https://stackoverflow.com/a/28319191
        with subprocess.Popen(args=self.command,
                              shell=self.shell,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True,
                              env=env,
                              cwd=self.cwd) as proc:
            if timeout:
                timer = Timer(timeout, _timer_out, args=[proc])
                timer.start()
                self._exec(proc)
                proc.stdout.close()
                timer.cancel()
            else:
                self._exec(proc)

            if exit_err and self.err:
                print_error(self.err)
                exit(proc.returncode)

            return ''.join(self.out) if self.out is not None else self.out, self.err
