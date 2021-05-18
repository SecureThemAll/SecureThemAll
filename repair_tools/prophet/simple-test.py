#!/usr/bin/env python
from sys import argv
from os import system, environ
import getopt
import subprocess
from shutil import copyfile

if __name__ == "__main__":
    if len(argv) < 4:
        print "Usage: php-tester.py <src_dir> <test_dir> <work_dir> [cases]";
        exit(1);

    opts, args = getopt.getopt(argv[1:], "p:");
    profile_dir = "";
    #out_file = open("/home/fanl/Workspace/mut.txt", "a")
    for o, a in opts:
        if o == "-p":
            profile_dir = a;

    src_dir = args[0];
    test_dir = args[1];
    work_dir = args[2];
    if profile_dir == "":
        cur_dir = src_dir;
    else:
        cur_dir = profile_dir;
    if len(args) > 3:
        ids = args[3:];
        #track_id = open("{wd}/stats/track.txt".format(wd=cur_dir), "r")
        #mut_id = ""
        #if 'MUTANT_ID' in environ:
        #    mut_id = environ['MUTANT_ID'] 
        for i in ids:
            cmd = "python3 {cb_repair} test -wd {wd} -cn None -tn {tn} -v -ef --only_numbers --print_ids --cores_path -l {wd}/tlog.txt 1> __out".format(cb_repair=environ["CBREPAIR"], wd=cur_dir, tn=i)
            ret = subprocess.call(cmd, shell=True, env = environ);
            #tid = track_id.read()
            
            #print >> out_file, tid, str(i), str(ret), mut_id
            
            if (ret == 0):
            #    print >> out_file, tid, str(i), mut_id
                print i
            
            system("rm -rf __out");
        print;
    if profile_dir != "":
        copyfile(profile_dir+"/.tracker", '/'.join(profile_dir.split("/")[:-1])+"/src/.tracker")

        #track_id.close()
    #out_file.close()
