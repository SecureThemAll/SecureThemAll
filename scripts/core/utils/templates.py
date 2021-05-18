from typing import List, AnyStr

sos_repair_description = """
\"\"\"
This file includes all the settings that could be modified for running SearchRepair/SOSRepair

* LIBCLANG_PATH: The path to libclang build. It should be either a .so or .dylib file.
* GENERATE_DB_PATH: The path where the DB should be built from. SR will enumerate all C files in this path to build the
 DB
* Z3_COMMAND: The z3 command on this machine.
* LARGEST_SNIPPET: The maximum number of lines that is considered as a snippet.
* SMALLEST_SNIPPET: The minimum number of lines that is considered as a snippet.
* DATABASE: Information about the database.
* LOGGING: Settings for logging.
* MAX_SUSPICIOUS_LINES: The number of suspicious lines tried before giving up.
* VALID_TYPES: The variable types that are right now supported by SR.
------ Settings related to file under repair -------
* TESTS_LIST: The path to a list of the tests that could be run on the file
* TEST_SCRIPT: The path to a script that will run the test
* COMPILE_SCRIPT: The path to a script that will compile the code
* FAULTY_CODE: The path to the faulty code (a C file)
* COMPILE_EXTRA_ARGS: The list of necessary arguments that should be passed to clang to properly parse the code
* MAKE_OUTPUT: The output of running `make` stored in a file (for the purpose of finding necessary arguments for compilation
automatically)
* METHOD_RANGE: The tuple of beginning and end of method with the fault (limits the search to the area)
* SOSREPAIR: If set to False it will only run SearchRepair features
* NUMBER_OF_TIMES_RERUNNING_TESTS: The number of times that the tests should be run to assure patch's correctness
* EXCLUDE_SCANF: If removing/replacing scanf in buggy code is going to be a problem, set this to True
\"\"\"
"""


def sosrepair_settings_template(db_name: str, user: str, password: str, host: str, log_path: str,
                                add_types: List[AnyStr] = None, **kwargs):
    valid_types = ['int', 'short', 'long', 'char', 'float', 'double', 'long long', 'size_t']

    if add_types:
        valid_types.extend(add_types)

    sosrepair_template = """
__author__ = 'Afsoon Afzal'

import logging

LIBCLANG_PATH = '/opt/sosrepair/llvm/lib/libclang.so'
Z3_COMMAND = '/opt/sosrepair/bin/z3'
"""
    sosrepair_template += "\nDATABASE = {"
    sosrepair_template += f"\n\t'db_name': '{db_name}',\n\t'user': '{user}',\n\t'password': '{password}',\n\t'host': '{host}'"
    sosrepair_template += "\n}\nLOGGING = {\n\t'filename': " + f"'{log_path}/repair.log',\n\t'level': logging.DEBUG\n"+"}"
    sosrepair_template += f"\nlogging.basicConfig(**LOGGING)\nVALID_TYPES = {valid_types}\n"
    sosrepair_template = sos_repair_description + sosrepair_template

    return sosrepair_template
