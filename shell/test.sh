#!/bin/bash
#
#./test.sh -f config.conf -v --prefix=/home
#
#
for arg in "$*"
do
	echo $arg
done

echo

for arg in "$@"
do
	echo $arg
done