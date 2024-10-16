#!/bin/bash
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
export OMP_NUM_THREADS=8

echo "$(which python)"
echo "$(python --version)"

###### DEBUG ######
###################
#echo ""
#echo "****************"
#echo ""
#echo "Running DEBUG simulation for 1 scan"
#echo ""
#echo "****************"
#
#mpirun -np 16 python sim_data_primecam_mpi.py -s schedule_1scan.txt.bck -d 500
#exit 1
#
###################
###################


# Directory containing the schedule files
SCHEDULE_DIR="input_files/schedules"
SCHEDULE_FILES=("$SCHEDULE_DIR"/*.txt)

# Default values for start and stop indices
START_IDX=0
STOP_IDX=${#SCHEDULE_FILES[@]}  # By default, go to the end of the array

# Read optional start and stop indices from command-line arguments
if [[ ! -z $1 ]]; then
    START_IDX=$1
fi

if [[ ! -z $2 ]]; then
    STOP_IDX=$2
fi

# Simulation info from user
echo "Running with 488 Hz sampling rate, scanning CES 0.75 deg/s, 2 deg/s^2 acc"

# Loop through the specified range of schedule files
for ((i=START_IDX; i<STOP_IDX; i++))
do
    # Get the current schedule file name
    SCH_NAME=$(basename "${SCHEDULE_FILES[$i]}")
    echo ""
    echo "****************"
    echo ""
    echo "Running simulation for schedule file: $SCH_NAME (Index: $i)"
    echo ""
    echo "****************"
    # Run the MPI command with the current schedule file
    # (nice -n 10 bash -c "echo -e '\n****************\n' ; /usr/bin/time -v mpirun -np 16 python sim_data_primecam_mpi.py -s \"$SCH_NAME\"") 2>&1 | tee -a toast_270924_arc10.log
    mpirun -np 16 python sim_data_primecam_mpi.py -s $SCH_NAME -d 400

    # Sleep for 5 sec before next simulation
    sleep 5
done

### End of script ###
### Notes:
# ./run_primecam_schedules.sh START_IDX STOP_IDX
# ./run_primecam_schedules.sh 2 5
# This will run the schedule files at indices 2, 3, and 4 in the array of schedule files.
# Default START_IDX=0 and STOP_IDX=length of the array of schedule files.
# Run as:
# /usr/bin/time -v ./run_primecam_schedules.sh 2>&1 | tee -a toast_270924_arc10.log
