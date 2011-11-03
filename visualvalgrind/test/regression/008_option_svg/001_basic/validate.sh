#!/bin/bash

# find out the directory where this script is
DIR="$PWD/$(dirname ${BASH_SOURCE[@]})/../../../../.."
REALDIR=$(readlink -f $DIR)
LIBDIR="$REALDIR/visualvalgrind/libs"


rm -f *.dot 2>&1 > /dev/null
PYTHONPATH="$LIBDIR" ../../../../src/visualvalgrind.py -svg build valtest.xml
for file in $(ls *.svg)
do
    expected="$(basename $file .svg).expected"
    test=$(diff $file $expected)

    if [ "$test" != "" ]; then
        echo "0"
        exit 1
    fi
done
echo "1"

rm -f *.svg 2>&1 > /dev/null
