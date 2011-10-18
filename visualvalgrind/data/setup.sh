#!/bin/sh
rm -rf pygraph
source /projects/seidelde/local/etc/zsh/zshenv.sei
virtualenv pygraph
source pygraph/bin/activate
easy_install distribute
sleep 1
easy_install python-graph-core
sleep 1
easy_install python-graph-dot
