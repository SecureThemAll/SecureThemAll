#!/usr/bin/env python3

import os
import time

from pathlib import Path
from config import configuration
from core.input_parser import parser
from core.runner.repair_task import RepairTask
from core.runner.local_runner import LocalRunner
from core.benchmark import Benchmark

if __name__ == "__main__":
    args = parser.parse_args()

    if args.working_dir:
        configuration.set_working_dir(args.working_dir)

    if args.bench_root:
        configuration.set_bench_root(args.bench_root)

    tasks = []
    var_args = dict(vars(args))

    benchmark = Benchmark(config=configuration, **var_args)

    challenges = benchmark.get_challenges()

    if args.challenges is not None:
        challenges = args.challenges
    start = time.time()

    for challenge in challenges:
        #try:
        tool = args.repair_tool(benchmark=benchmark, challenge_name=challenge, config=configuration,
                                timeout=configuration.tools_timeout, **var_args)

        task = RepairTask(config=configuration, tool=tool, challenge_name=challenge)

        if not args.continue_execution or not os.path.exists(os.path.join(task.log_dir(), "repair.log")):
            tasks.append(task)
        #except Exception as e:
        #    print(e)
        #    with open("repair_exceptions.log", "w") as f:
        #        f.write(challenge + ": " + str(e.__traceback__)+"\n")

    LocalRunner(tasks, configuration.local_threads, args).execute()

    if args.time:
        end = time.time()
        hours, rem = divmod(end - start, 3600)
        minutes, seconds = divmod(rem, 60)
        duration = "Duration: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
        file_path = Path(args.time)
        print(duration)

        with file_path.open(mode="w") as f:
            f.write(duration)
