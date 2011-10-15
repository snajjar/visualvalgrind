#!/bin/sh

#clean up
rm *.dot 2> /dev/null
rm *.svg 2> /dev/null

# build graph dot file
python visualvalgrind.py $1

# create svg file
for dotfile in `ls *.dot` 
do 
    base=`basename $dotfile .dot`
    dot -Tsvg $dotfile > $base.svg 
done

#clean up
rm *.dot 2> /dev/null
