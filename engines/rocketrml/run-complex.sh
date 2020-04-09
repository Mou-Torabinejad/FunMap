#!/bin/bash


declare -a mappings=("complex_sameFunction.ttl" "complex_sameFunction2.ttl" "complex_sameFunction3.ttl" "complex_sameFunction4.ttl")
declare -a dataArray=("veracity25.csv" "veracity50.csv"  "veracity75.csv" "veracity100.csv")
echo "engine,dataset,mapping,time,results" > results.csv

for data in "${dataArray[@]}"
do
	echo "---------Running transformation for $data------------"
	for mapping in "${mappings[@]}"
	do
		echo "-----Running $mapping------"
		echo "Copying $data to data.csv"
		for i in 1 #2 3 4 5
		do
			cp $data data.csv
			cp $mapping mapping.rml.ttl
			start=$(date +%s.%N)
			node --max-old-space-size=32000  index.js
			dur=$(echo "$(date +%s.%N) - $start" | bc)
			noutput=$(wc -l output.nt | cut -d " " -f 1)
			echo "rocketrml,$data,$mapping,$dur,$noutput"  >> results.csv
			rm output.nt
			rm data.csv
		done
	done
done