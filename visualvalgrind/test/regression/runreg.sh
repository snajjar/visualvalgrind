#!/bin/sh

# colors
white='\033[37m'
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
        echo "   Playing test $sd:" 
        sleep 2
        res=`./validate.sh`
        if [ "$res" = "1" ]; then
            echo -e \\033[A"Playing test $sd:$green OK$white"
        else
            echo -e \\033[A"Playing test $sd:$red KO$white"
        fi
        cd ..
    done
    cd ..
done
