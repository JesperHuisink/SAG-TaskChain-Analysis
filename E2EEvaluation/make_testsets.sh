#!/bin/bash

# Check if command is provided
if [ -z "$1" ]; then
	echo "Usage: $0 '<taskset_generation_command>'"
	exit 1
fi
if [ -z "$2" ]; then
	echo "Usage: $0 '<amount of tasksets to be created>'"
	exit 1
fi
# Get command from first argument
command="$1"

# Nr of test sets generated
nr_sets="$2"

max_jobs=100 # Max concurrent generations
job_count() {
    jobs -rp | wc -l
}

# Create the parent folder
parent_folder="testsets"
mkdir -p "$parent_folder"
file1="cli_cause_effect_chains.pickle"
file2="cli_cause_effect_chains.yaml"
for ((i=1;i<=nr_sets; i++)); do
# Wait for an available job slot
    while (( $(job_count) >= max_jobs )); do
        sleep 1
    done
	(
	subfolder="$parent_folder/testset-$i"
	mkdir -p "$subfolder"

	echo "Making taskset $i"
	eval "$command -o $subfolder/cli_" || { echo "Command failed"; exit 1; }
	#sleep 1
	
	eval "python3 ./parser/parse.py $subfolder/$file2 $subfolder"
	) &
done

wait
echo "Completed."
