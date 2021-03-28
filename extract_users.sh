#!/bin/bash

FL=$1

[[ -z $FL ]] && echo "ERROR: filename is not given" && echo "USAGE: extract_users.sh <stream.html>" && exit

[[ ! -f $FL ]] && echo "ERROR: file '$FL' not found" && exit

filenamea=$(basename -- "$FL")
filename="${filenamea%.*}"

FL_O=${filename}_users.csv

grep -o 'data-username="[a-z0-9_]*"' $FL | grep -o '".*"' | sed 's/"//g' > $FL_O
