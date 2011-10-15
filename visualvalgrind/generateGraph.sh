#!/bin/sh

#clean up
rm file.dot 2>/dev/null
rm tmp.dot 2>/dev/null
rm file.svg 2>/dev/null 
rm graph.dot 2>/dev/null 

# build graph dot file
python visualvalgrind.py $1
# create svg file
dot -Tsvg graph.dot > graph.svg

#clean up
rm file.dot 2>/dev/null
rm tmp.dot 2>/dev/null
rm graph.dot 2>/dev/null 
