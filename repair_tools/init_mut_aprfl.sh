#!/bin/bash

CURRENT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DOWNLOAD_DIR="/tmp/mutapr"

mkdir $DOWNLOAD_DIR -p
pushd $DOWNLOAD_DIR || (echo "Failed to move to download folder." && exit 1)
echo "Downloading MUT-APR source code."
wget -O mutaprfl.zip  http://www.cs.colostate.edu/~bieman/MutAPR/mutaprfl-code.zip || (echo "Failed to download source code." && exit 1)
echo "Unzipping source code."
unzip mutaprfl.zip || (echo "Failed to extract downloaded zip." && exit 1)
mv mutaprfl-code "$CURRENT_DIR"/mut-aprfl || (echo "Failed to move files from download folder." && exit 1)
popd || exit
rm -rf $DOWNLOAD_DIR
echo "Successfully initialized MUT-APR"