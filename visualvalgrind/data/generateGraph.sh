#!/bin/sh

rm file.dot
rm tmp.dot
rm file.png
python findSuppMatch.py $1 > tmp.dot

# add option rankdir=LR so the graph is left right (more readable) 
HEAD=`cat tmp.dot | head -n 1`

echo $HEAD > file.dot
echo "rankdir=LR" >> file.dot
cat tmp.dot | grep -v digraph >> file.dot
dot -Tpng file.dot > file.png

