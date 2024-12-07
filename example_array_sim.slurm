#!/bin/bash

###############################################
###     SLURM script for primecam_sims     ####
###      ARRAY JOB runs all schedules      ####
###					                       ####
###     Tested on Uni Bonn Marvin Cluster  ####
###             v2.0 , 18.10.2024          ####
###############################################

### This script runs through all the schedule files
### launching SLURM ARRAY jobs for each schedule independently
### NOTE: ndets parameter must be set in Section 4

### section 1 - SLURM params

#SBATCH --partition=intelsr_devel
### cluster specific / intelsr_short, lm_short, lm_devel
### https://wiki.hpc.uni-bonn.de/en/running_jobs

### #SBATCH --ntasks 8      # number of procs to start
### or
#SBATCH --ntasks-per-node 8 # tasks per node ; num of processes per node
#SBATCH --cpus-per-task 4 # number of cores per task ; threads per process

#SBATCH --nodes 1  # number of nodes
#SBATCH --array=0-23  # Define the array size, 24 schs

#SBATCH --job-name=det200_n8c4_sim 
### Job name, det#ndets_#ntaskstotal_#corespertask_sim

### #ntasks = #nodes x #ntasks-per-node
### #ncores_total = #ntasks x #cpus-per-task
### #ncores_total_pernode = #ntasks-per-node x #cpus-per-task

#SBATCH --mem-per-cpu=8G # mem per proc
### #SBATCH --mem=130G                # max mem requested, per node
### Maximum requested time (days-hrs:min:sec)
#SBATCH --time 0-00:05:00 #DEBUG
### #SBATCH --time 0-03:00:00 #estimated runtime max 0-03:00:00

#SBATCH --output ./logs/%A_%a_%x.out 
#SBATCH --error ./logs/%A_%a_%x.err 


### section 2 - Runtime env set-up
module purge
### load all modules needed for Job
module load mpi4py
### initiate conda
### source /opt/software/easybuild-INTEL/software/Anaconda3/2022.05/etc/profile.d/conda.sh
source /opt/software/easybuild-INTEL/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda deactivate
conda activate toast3

### section 3 - Job Logging
echo ""
echo "*************"
echo "Running Job..."
echo "Starting at `date`"
echo "Hostname $HOSTNAME"
echo "Job Name: $SLURM_JOB_NAME"
echo "Job ID: $SLURM_JOB_ID"
echo "Node List: $SLURM_NODELIST"
echo "Running on $SLURM_NNODES nodes."
echo "Running on $SLURM_NPROCS processors."
echo "Slurm Ntasks: $SLURM_NTASKS"
echo "Number of Tasks per Node: $SLURM_NTASKS_PER_NODE"
echo "Number of CPUs per Task: $SLURM_CPUS_PER_TASK"
echo "Cores per Node: $SLURM_CPUS_ON_NODE"
echo "Total Number of Nodes: $SLURM_JOB_NUM_NODES"
echo "Current working directory is `pwd`"
echo "Python path: $(which python)"
echo "Using MPI lib: $(which mpirun)"
echo "Using GCC lib: $(which gcc)"
echo ""

### section 4 - Set Job parameters
### Set number of detectors
ndets=200

### section 5 - Job Run
echo "***** EXEC SCRIPT *****"
echo `date '+%F %H:%M:%S'`
echo "***********************"
echo ""

### Collect all schedule files from input dir
schedule_files_list=($(basename -a input_files/schedules/*.txt))
### Select schedule based on array index
schedule_file=${schedule_files_list[$SLURM_ARRAY_TASK_ID]}
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

echo ""
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"
echo "Running schedule file: $schedule_file"
echo "Number of dets: $ndets"
echo ""
mpirun -np $SLURM_NTASKS python3 sim_data_primecam_mpi.py -s $schedule_file -d $ndets


echo ""
echo "******** DONE *********"
echo `date '+%F %H:%M:%S'`
echo "***********************"


