#! /bin/bash

set -x -e

input=$1

pydump $input -fi1 > dumporig.txt

py2py $input | tee pretty.txt | pydump -fi1 | tee dump2.txt | diff dumporig.txt -

rm dumporig.txt pretty.txt dump2.txt
