#!/usr/bin/env python
import getopt
from sys import argv
import subprocess
from os import chdir, getcwd, path, environ, pardir, chmod
from tester_common import extract_arguments
from shutil import copyfile


def write_build_file(workdir):
    parent_dir = path.abspath(path.join(workdir, pardir))
    build_cmd = "python3 {cb_repair} compile -wd {wd} -cn None -B {pd}/patches --gcc --exit_err -l {wd}/clog.txt".format(cb_repair=environ["CBREPAIR"], wd=workdir, pd=parent_dir)
    sh_script = "#!/bin/bash\n" + build_cmd
    makefile =  ".PHONY: do_script\n\ndo_script:\n\t./build.sh\n\nprerequisites: do_script\n\ntarget: prerequisites\n"
    build_file_path = workdir+"/build.sh"
    makefile_path = workdir+"/Makefile"

    with open(build_file_path, "w") as bfp, open(makefile_path, "w") as mfp:
        bfp.write(sh_script)
        mfp.write(makefile)
    
    chmod(build_file_path, 0o755)
    chmod(makefile_path, 0o755)

def tobuild(src_dir, write_build_args):
    ori_dir = getcwd();
    print "Path env: ", environ["PATH"];
    my_env = environ;
    chdir(src_dir);

    if 'profile' in src_dir:
        copyfile('/'.join(src_dir.split("/")[:-1])+"/src/.tracker", src_dir+"/.tracker")

    cmd = "python3 {cb_repair} compile -wd {wd} -cn None -fl -sc --gcc --no_status --exit_err -l {wd}/clog.txt".format(cb_repair=environ["CBREPAIR"], wd=src_dir)

    if write_build_args is not None:
        cmd += " --write_build_args {wba}; rm -rf {wd}/build".format(wba=ori_dir+ "/" + write_build_args, wd=src_dir)
        write_build_file(src_dir)
        
    print cmd
    ret = subprocess.call(cmd, shell=True, env = my_env);

#    if 'profile' in src_dir:
#        copyfile(src_dir+"/.tracker", '/'.join(src_dir.split("/")[:-1])+"/src/.tracker")

    if write_build_args and path.exists(write_build_args):
        with open(write_build_args, "r") as f:
            print f.read()

    #ret |= subprocess.call("cmake --build {wd}/build".format(wd=src_dir), shell=True, env = my_env);
    #ret |= subprocess.call("{wd}/build.sh".format(wd=src_dir), shell=True, env = my_env);
    #ret |= subprocess.call("echo {res} >> {wd}/stats/compile.txt".format(wd=src_dir, res=ret), shell=True, env = my_env);
    chdir(ori_dir);
    return ret == 0;

if __name__ == "__main__":
    opts, args = getopt.getopt(argv[1:], "cd:hx");

    dryrun_src = "";
    compile_only = False;
    print_usage = False;
    config_only = False;
    for o, a in opts:
        if o == "-x":
            config_only = True;
        if o == "-d":
            dryrun_src = a;
        elif o == "-c":
            compile_only = True;
        elif o == "-h":
            print_usage = True;

    if config_only:
        exit(0);

    if ((len(args) < 1) or (print_usage)):
        print "Usage: simple-build.py <dirctory> [-d src_file | -c] [-h]";
        exit(0);

    out_dir = args[0];
    # fetch from github if the directory does not exist
    if (not path.exists(out_dir)):
        print "Directory does not exist!";
        exit(1);

    if (not tobuild(out_dir, args[1] if dryrun_src != "" else None)):
        print "Build failed!";
        exit(1);

    #if dryrun_src != "":
    #    build_dir, build_args = extract_arguments(out_dir, dryrun_src);

