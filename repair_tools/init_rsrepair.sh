#!/bin/bash

CURRENT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DOWNLOAD_DIR="/tmp/rsrepair"

mkdir $DOWNLOAD_DIR -p
pushd $DOWNLOAD_DIR || (echo "Failed to move to download folder." && exit 1)
echo "Downloading MUT-APR source code."
wget wget -O rsrepair.tar.bz2   https://sourceforge.net/projects/rsrepair/files/RSRepair.tar.bz2 || (echo "Failed to download source code." && exit 1)
command -v bzip2 > /dev/null
[[ $? -eq 1 ]] && (echo "Installing bzip2 to extract source files." && apt install bzip2)
echo "Unzipping source code."
bzip2 -d rsrepair.tar.bz2 || (echo "Failed to extract downloaded bz2 file." && exit 1)
mv .* "$CURRENT_DIR"/rsrepair || (echo "Failed to move files from download folder." && exit 1)
popd || exit
rm -rf $DOWNLOAD_DIR
echo "Successfully initialized RSRepair"