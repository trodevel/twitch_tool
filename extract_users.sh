#!/bin/bash

FL=$1

[[ -z $FL ]] && echo "ERROR: filename is not given" && echo "USAGE: extract_users.sh <stream.html>" && exit

[[ ! -f $FL ]] && echo "ERROR: file '$FL' not found" && exit

filenamea=$(basename -- "$FL")
filename="${filenamea%.*}"

FL_O=${filename}_users.csv

echo "input  = $FL"
echo "output = $FL_O"

grep -o 'data-username="[a-z0-9_]*"' $FL | grep -o '".*"' | sed 's/"//g' > $FL_O

lines=$( cat $FL_O | wc -l )

echo "INFO: $lines lines written to $FL_O"
