#!/bin/sh

#clean up
rm *.dot 2> /dev/null
rm *.svg 2> /dev/null

# build graph dot file
for rep in `ls examples`
do
    python visualvalgrind.py examples/$rep/valtest.xml
    # create svg file
    for dotfile in `ls *.dot` 
    do 
        base=`basename $dotfile .dot`
        dot -Tsvg $dotfile > $base.svg 
    done
    mv *.svg *.dot examples/$rep
done

#clean up
rm *.dot 2> /dev/null
rm *.svg 2> /dev/null
