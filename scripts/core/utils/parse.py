#!/usr/bin/env python3
import re


def c_to_cpp(c_file: str):
    if '.cc' in c_file:
        return re.sub(r'.cc$', '.ii', c_file)
    return re.sub(r'.c$', '.i', c_file)


def cpp_to_c(ccp_file: str):
    if '.ii' in ccp_file:
        return re.sub(r'.ii$', '.cc', ccp_file)
    return re.sub(r'.i$', '.c', ccp_file)


def cpp_to_obj(ccp_file: str):
    if '.ii' in ccp_file:
        return re.sub(r'.ii$', '.cc.o', ccp_file)
    return re.sub(r'.i$', '.c.o', ccp_file)
