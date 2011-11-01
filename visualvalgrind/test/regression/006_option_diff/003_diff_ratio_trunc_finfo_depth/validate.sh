#!/bin/bash

# find out the directory where this script is
DIR="$PWD/$(dirname ${BASH_SOURCE[@]})/../../../../.."
REALDIR=$(readlink -f $DIR)
LIBDIR="$REALDIR/visualvalgrind/libs"


rm -f *.dot 2>&1 > /dev/null
PYTHONPATH="$LIBDIR" ../../../../src/visualvalgrind.py -t 4 -depth 3 -finfo diff -r 1 -new valtest2.xml -old valtest1.xml
mv Leak_DefinitelyLost.dot Leak_DefinitelyLost_r1.dot

PYTHONPATH="$LIBDIR" ../../../../src/visualvalgrind.py -t 4 -depth 3 -finfo diff -r 10 -new valtest2.xml -old valtest1.xml
mv Leak_DefinitelyLost.dot Leak_DefinitelyLost_r10.dot

PYTHONPATH="$LIBDIR" ../../../../src/visualvalgrind.py -t 4 -depth 3 -finfo diff -r 11 -new valtest2.xml -old valtest1.xml

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
