#!/bin/sh

# colors
red='\033[31m'   # Red
green='\033[32m'   # Green

echo "$white"
echo "Regression started"

DIRS=`find . -type d | grep "./"  | sed "s/\.\///" | grep -v "/" | sort`

for d in $DIRS
do
    cd $d
    echo " Playing directory $d:" 
    subdirs=`find . -type d | grep "./" | sed "s/\.\///" | grep -v "/" | sort`
    for sd in $subdirs
    do
        cd $sd
        echo -n "   Playing test $sd:" 
        res=`./validate.sh`
        if [ "$res" = "1" ]; then
            echo "$green OK"
        else
            echo "$red KO"
        fi
        tput sgr0 #reset color to normal
        cd ..
    done
    cd ..
done

echo "Regression ended"
