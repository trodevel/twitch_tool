#!/bin/bash

FL=$1

[[ -z $FL ]] && echo "ERROR: filename is not given" && echo "USAGE: extract_users.sh <stream.html>" && exit

[[ ! -f $FL ]] && echo "ERROR: file '$FL' not found" && exit

filenamea=$(basename -- "$FL")
filename="${filenamea%.*}"

FL_O=${filename}_users.csv

echo "input  = $FL"
echo "output = $FL_O"

channel=$( grep -o 'content="https://www.twitch.tv/[a-z0-9_]*"' $FL | sed "s~.*/~~" | sed 's/"//g' )

echo "DEBUG: channel = $channel"

grep -o 'id="chat-viewers-list-header-[a-zA-Z0-9_]*"' $FL | grep -o '\-[a-zA-Z0-9_]*"' | sed 's/"//g' | sed 's/^-//g'
grep -o 'data-username="[a-z0-9_]*"' $FL | grep -o '".*"' | sed 's/"//g' | sed "s/^/$channel;/" > $FL_O

lines=$( cat $FL_O | wc -l )

echo "INFO: $lines lines written to $FL_O"
