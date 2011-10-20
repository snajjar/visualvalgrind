#!/bin/bash

rm -f Leak_DefinitelyLost.dot 2>&1 > /dev/null
../../../../visualvalgrind.py build valtest.xml
test=`diff expected Leak_DefinitelyLost.dot`

if [ "$test" = "" ]; then
    echo 1
else
    echo 0
fi

rm -f Leak_DefinitelyLost.dot 2>&1 > /dev/null
