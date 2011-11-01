#!/bin/bash

# find out the directory where this script is
DIR="$PWD/$(dirname ${BASH_SOURCE[@]})/../../../../.."
REALDIR=$(readlink -f $DIR)
LIBDIR="$REALDIR/visualvalgrind/libs"


rm -f *.dot 2>&1 > /dev/null
PYTHONPATH="$LIBDIR" ../../../../src/visualvalgrind.py -d -finfo build valtest.xml
for file in $(ls *.dot)
do
    expected="$(basename $file .dot).expected"
    test=$(diff $file $expected)

    if [ "$test" != "" ]; then
        echo "0"
        exit 1
    fi
done
echo "1"

rm -f *.dot 2>&1 > /dev/null
