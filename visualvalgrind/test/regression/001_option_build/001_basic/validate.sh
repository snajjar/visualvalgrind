#!/bin/bash

# find out the directory where this script is
DIR="$PWD/$(dirname ${BASH_SOURCE[@]})/../../../../.."
REALDIR=$(readlink -f $DIR)
LIBDIR="$REALDIR/visualvalgrind/libs"


rm -f Leak_DefinitelyLost.dot 2>&1 > /dev/null
PYTHONPATH="$LIBDIR" ../../../../visualvalgrind.py build valtest.xml
test=`diff expected Leak_DefinitelyLost.dot`

if [ "$test" = "" ]; then
    echo "1"
else
    echo "0"
fi

rm -f Leak_DefinitelyLost.dot 2>&1 > /dev/null
