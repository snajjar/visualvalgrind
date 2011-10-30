#!/bin/bash

# find out the directory where this script is
DIR="$PWD/$(dirname ${BASH_SOURCE[@]})/../../../../.."
REALDIR=$(readlink -f $DIR)
LIBDIR="$REALDIR/visualvalgrind/libs"


rm -f *.dot 2>&1 > /dev/null
rm -rf output_dir/
mkdir output_dir
PYTHONPATH="$LIBDIR" ../../../../src/visualvalgrind.py -o output_dir build valtest.xml

# test that nothing is outputed in current directory
test=$(ls *.dot 2> /dev/null)
if [ "$test" != "" ]; then
    echo "0"
    exit 1
fi

# test that .dot are output in output_dir
test=$(ls output_dir/*.dot)
if [ "$test" = "" ]; then
    echo "0"
    exit 1
fi

echo "1"

rm -f *.dot 2>&1 > /dev/null
rm -rf output_dir/
