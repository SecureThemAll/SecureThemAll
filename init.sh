#!/bin/bash
# from https://github.com/program-repair/RepairThemAll/blob/master/init.sh

# modified to accept equal major version
do_version_check() {
    [ "$1" == "$2" ] && return 10

    ver1front=$(echo "$1" | cut -d "." -f -1)
    ver1back=$(echo "$1" | cut -d "." -f 2-)
    ver2front=$(echo "$2" | cut -d "." -f -1)
    ver2back=$(echo "$2" | cut -d "." -f 2-)

    if [ "$ver1front" != "$1" ] || [ "$ver2front" != "$2" ]; then
        [ "$ver1front" -lt "$ver2front" ] && return 9

        [ "$ver1front" == "$1" ] || [ -z "$ver1back" ] && ver1back=0
        [ "$ver2front" == "$2" ] || [ -z "$ver2back" ] && ver2back=0
        do_version_check "$ver1back" "$ver2back"
        return $?
    else
        [ "$1" -gt "$2" ] && return 11 || return 9
    fi
}

# Symlink sh to to bash
sym_sh(){
  mv /bin/sh /bin/sh.orig
  ln -s /bin/bash /bin/sh
}

link=/bin/sh

if [ -L ${link} ] ; then
   if [ "$(readlink $link)" != "/bin/sh" ] ; then
      sym_sh
   else
     echo "good"
   fi
else
   sym_sh
fi

echo "Installing SecureThemAll dependencies"
apt-get install python3 python3-pip python3-dev -y

command -v python3 > /dev/null
[[ $? -eq 1 ]] && echo "[Error] python3 not installed" && exit 1 ;

python3_version=$(python3 -c 'import platform; print(platform.python_version())')

do_version_check "$python3_version" "3.7"
[[ $? -eq 9 ]] && echo "[Error] python3 version >= 3.7" && exit 1 ;

echo "Installing python packages"
pip3 install -r requirements.txt

# Initializing Benchmark
./benchmark/cb-repair/init.sh
[[ $? -eq 1 ]] && echo "[Error] Benchmark initialization failed" && exit 1 ;

# Installing Repair Tools
# MUT-APR
./repair-tools/init_mut_aprfl.sh
[[ $? -eq 1 ]] && echo "[Error] MUT-APR initialization failed" && exit 1 ;
# CquenceR
./repair-tools/CquenceR/init.sh
[[ $? -eq 1 ]] && echo "[Error] CquenceR initialization failed" && exit 1 ;
# GenProg
./repair-tools/init_genprog.sh
[[ $? -eq 1 ]] && echo "[Error] GenProg initialization failed" && exit 1 ;
