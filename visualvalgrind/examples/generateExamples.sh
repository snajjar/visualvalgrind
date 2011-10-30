#!/bin/sh

#clean up
rm *.dot 2> /dev/null
rm *.svg 2> /dev/null

# build graph dot file
for rep in `find . -type d | grep "./"  | sed "s/\.\///" | grep -v "/" | sort`
do
    ../src/visualvalgrind.py build $rep/valtest.xml
    # create svg file
    for dotfile in `ls *.dot` 
    do 
        base=`basename $dotfile .dot`
        dot -Tsvg $dotfile > $base.svg 
    done
    mv *.svg *.dot $rep
done

#clean up
rm *.dot 2> /dev/null
rm *.svg 2> /dev/null
