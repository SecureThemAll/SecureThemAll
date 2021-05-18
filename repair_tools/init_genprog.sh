#!/bin/bash

CURRENT_DIR=$(pwd)
WORKING_DIR=$CURRENT_DIR/genprog-code

echo "Installing Genprog dependencies..."
apt -y install opam
[[ $? -ne 0 ]] && echo "[Error] Failed to install opam." && exit 1
echo "yes" > /tmp/yes.txt
opam init -y < /tmp/yes.txt && \
[[ $? -ne 0 ]] && echo "[Error] Opam init failed." && exit 1
opam switch create 4.04.0
[[ $? -ne 0 ]] && echo "[Error] Creating opam switch for older version of ocaml." && exit 1
eval $(opam config env)
[[ $? -ne 0 ]] && echo "[Error] Failed to update the current shell environment." && exit 1
opam install -y cil
[[ $? -ne 0 ]] && echo "[Error] Failed to install CIL with opam ." && exit 1
echo "Building GenProg..."
cd "$WORKING_DIR/src" || exit 1
[[ $? -ne 0 ]] && echo "[Error] Failed to move to GenProg's source directory." && exit 1
opam init -y < /tmp/yes.txt && \
[[ $? -ne 0 ]] && echo "[Error] Opam init failed." && exit 1
eval $(opam config env)
[[ $? -ne 0 ]] && echo "[Error] Failed to update the current shell environment." && exit 1
opam switch 4.04.0
[[ $? -ne 0 ]] && echo "[Error] Failed to switch to older compiler version." && exit 1
make
[[ $? -ne 0 ]] && echo "[Error] Failed make GenProg." && exit 1
echo "Successfully initialized GenProg"