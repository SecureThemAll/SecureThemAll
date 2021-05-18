#!/usr/bin/env python3
import argparse

#from core.repair_tools import RepairTool


parser = argparse.ArgumentParser(prog="repair", description='Repair bugs')
challenge_parser = argparse.ArgumentParser(add_help=False)
challenge_parser.add_argument("--continue",
                              help="Continue the previous execution",
                              action='store_true',
                              dest='continue_execution',
                              default=False)
challenge_parser.add_argument("--endTime", help="Specify an hour to stop the execution (hh:mm)", dest="end_time",
                              default=None)

challenge_parser.add_argument("--challenges", "-c", nargs='+', help="The challenge name")
challenge_parser.add_argument("--ssh_bench", type=str, help="SSH connection to the benchmark on remote host")
challenge_parser.add_argument("--ssh_tool", type=str, help="SSH connection to the tool on remote host")
# TODO: remove bench_root, this must be done inside configs, there are the paths
challenge_parser.add_argument("--bench_root", type=str, help="Updates benchmark's root path (for remote usage)")
challenge_parser.add_argument("--working_dir", type=str, help="Sets the working directory (default: /tmp)")
challenge_parser.add_argument("--seed", help="The random seed", default=0, type=int)
challenge_parser.add_argument("--debug", help="Debug mode", action='store_true')
challenge_parser.add_argument("--time", type=str, help="Save duration of the repair to specified file")
challenge_parser.add_argument('-v', '--verbose', help='Verbose output.', action='store_true')


subparsers = parser.add_subparsers()


def add_repair_tool(name, tool, description):
    tool_parser = subparsers.add_parser(name, help=description, parents=[challenge_parser])
    tool_parser.set_defaults(repair_tool=tool)
    return tool_parser


import core.repair_tools.ae
import core.repair_tools.kali
import core.repair_tools.genprog
import core.repair_tools.flexirepair
import core.repair_tools.mut_apr
import core.repair_tools.spr
import core.repair_tools.cquencer
import core.repair_tools.prophet
import core.repair_tools.sosrepair
import core.repair_tools.searchrepair
