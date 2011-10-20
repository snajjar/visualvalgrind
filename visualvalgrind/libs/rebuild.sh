#!/bin/sh

rm -f *.py
files=`find ../.. -name "*.py"`

for file in $files
do
    bname=`basename $file`
    ln -s $file $bname
done
