#! /bin/bash

## mappings to be applied in the experiments
declare -a mappings=("sameFunction_4.ttl" "sameFunction_6.ttl" "sameFunction_8.ttl" "sameFunction_10.ttl" "complex_sameFunction4.ttl" "complex_sameFunction6.ttl" "complex_sameFunction8.ttl" "complex_sameFunction10.ttl")
## datasets to be applied in the experiments
declare -a dataArray=("veracity75.csv" "veracity25.csv")

echo "dataset,mapping,time,iteration" > results-funmap-rmlmapper.csv
echo "dataset,mapping,time,iteration" > results-funmap-basic-rmlmapper.csv
echo "dataset,mapping,time,iteration" > results-rmlmapper.csv
############################################################################################
############################### Running FunMap+RMLMapper ###################################
############################################################################################

echo "---------Running experiments over RMLMapper---------"

echo "---------Running first FunMap over RMLMapper---------"

for mapping in "${mappings[@]}"
do
    for data in "${dataArray[@]}"
    do
        echo "Running experiment for $mapping and $data"
        for i in 1 2 3 4 5
        do
            cp ./data/$data data.csv
            cp ./mappings/$mapping mapping.ttl
            
            echo "FunMap+RMLMapper: iteration $i"
            start=$(date +%s.%N)
            python3 ./FunMap/run_translator.py config.ini
            java -jar rmlmapper.jar -m ./output/transfered_mapping.ttl -o output.nt
            dur=$(echo "$(date +%s.%N) - $start" | bc)
            echo "$data,$mapping,$dur,$i"  >> results-funmap-rmlmapper.csv

            echo "FunMap-Basic+RMLMapper: iteration $i"
            start=$(date +%s.%N)
            python3 ./FunMap/run_translator.py config-basic.ini
            java -jar rmlmapper.jar -m ./output/transfered_mapping.ttl -o output.nt
            dur=$(echo "$(date +%s.%N) - $start" | bc)
            echo "$data,$mapping,$dur,$i"  >> results-funmap-basic-rmlmapper.csv

            rm data.csv
            rm mapping.ttl
        done
    done
done

##########################################################################################
######################### Running RMLMapper + simple functions ###########################
##########################################################################################

## mappings to be applied in the experiments
declare -a mappings=("sameFunction_4_rmlmapper.ttl" "sameFunction_6_rmlmapper.ttl" "sameFunction_8_rmlmapper.ttl" "sameFunction_10_rmlmapper.ttl")

## Running FunMap+RMLMapper with simple functions
echo "---------Running RMLMapper with simple function---------"

for mapping in "${mappings[@]}"
do     
    for data in "${dataArray[@]}"
    do
        echo "Running experiment for $mapping and $data"
        for i in 1 2 3 4 5
        do
            cp ./data/$data data.csv
            cp ./mappings/$mapping mapping.ttl
            echo "RMLMapper simple functions: iteration $i"
            start=$(date +%s.%N)
            java -jar rmlmapper.jar -m mapping.ttl -f functions_grel.ttl -o output.nt -d
            dur=$(echo "$(date +%s.%N) - $start" | bc)
            echo "$data,$mapping,$dur,$i"  >> results-rmlmapper.csv
            rm data.csv
            rm mapping.ttl
        done
	done
done

##########################################################################################
####################### Running RMLMapper + complex functions ############################
##########################################################################################

## mappings to be applied in the experiments
declare -a mappings=("complex_sameFunction4_rmlmapper.ttl" "complex_sameFunction6_rmlmapper.ttl" "complex_sameFunction8_rmlmapper.ttl" "complex_sameFunction10_rmlmapper.ttl")

## Running FunMap+RMLMapper with complex functions
echo "---------Running RMLMapper with complex function---------"

for mapping in "${mappings[@]}"
do
    for data in "${dataArray[@]}"
    do
        echo "Running experiment for $mapping and $data"
        for i in 1 2 3 4 5
        do
            cp ./data/$data data.csv
            cp ./mappings/$mapping mapping.ttl
            echo "RMLMapper complex functions: iteration $i"
            start=$(date +%s.%N)
			java -jar rmlmapper.jar -m mapping.ttl -f functions_complex.ttl -o output.nt -d
			dur=$(echo "$(date +%s.%N) - $start" | bc)
			echo "$data,$mapping,$dur"  >> results-rmlmapper.csv
            rm data.csv  
            rm mapping.ttl
        done                                                                                                                                                                                                                           rm mapping.ttl                                                                                                                                                                                                                   done
    done
done








