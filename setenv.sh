#!/bin/bash

# find out the directory where this script is
DIR=$PWD/`dirname ${BASH_SOURCE[@]}`
REALDIR=$(readlink -f $DIR)
LIBDIR=$REALDIR/visualvalgrind/libs

# export lib dir in PYTHONPATH if not already in there
test=$(echo $PYTHONPATH | sed "s/:/\n/g")
if [ "$test" = "" ]; then
   export PYTHONPATH=$PYTHONPATH:$LIBDIR
fi
alias vv="$REALDIR/visualvalgrind/visualvalgrind.py"
alias visualvalgrind="$REALDIR/visualvalgrind/visualvalgrind.py"

