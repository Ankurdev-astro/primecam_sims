#!/bin/bash

# Submit the Slurm job and capture the job ID
JOB_SUBMIT_OUTPUT=$(sbatch marvin_run.slurm)
JOB_ID=$(echo "$JOB_SUBMIT_OUTPUT" | awk '{print $4}')

# Display job ID and name on screen
echo "Submitted job ID: $JOB_ID"

### Start a background process to wait for the job to finish and append resource usage
(
    # Wait for the job to finish
    while squeue -j $JOB_ID > /dev/null 2>&1; do
        sleep 1
    done

    JOB_NAME=$(sacct -j $JOB_ID --format=JobName%20 --noheader | head -n 1 | awk '{$1=$1};1')
    ### echo "Job Name: $JOB_NAME"

    # Define the log file name based on the Job ID and Job Name
    LOG_FILE="./logs/${JOB_ID}.${JOB_NAME}.out"

    # Append resource usage to the dynamically named log file
    sacct -j $JOB_ID --format=JobID,JobName,Partition,AllocCPUS,Elapsed,State,ExitCode,NodeList,MaxRSS,MaxVMSize,TotalCPU,CPUTime,ReqMem,AveRSS,AveVMSize \
        >> "$LOG_FILE"
) &

# Detach from the login shell after submitting
exit 0

