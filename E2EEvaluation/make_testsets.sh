#!/bin/bash

POSITIONAL_ARGS=()

outtype="active"
intype="event"
nr_sets=10

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--count)
      nr_sets="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--OutputType)
      outtype="$2"
      shift # past argument
      shift # past value
      ;;
    -i|--InputType)
      intype="$2"
      shift # past argument
	  shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

# Check if command is provided
if [ -z "$1" ]; then
	echo "Usage: $0 '<taskset_generation_command>'"
	exit 1
fi

# Get command from first argument
command="$1"

max_jobs=100 # Max concurrent generations
job_count() {
    jobs -rp | wc -l
}

echo "Creating $nr_sets testsets using $intype input and $outtype output"

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
	
	eval "python3 ./parser/parse.py $subfolder/$file2 --out_path $subfolder/ --InputType $intype --OutputType $outtype --prio TLFP"
	) &
done

wait
echo "Completed."
