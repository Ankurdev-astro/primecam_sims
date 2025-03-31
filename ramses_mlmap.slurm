#!/bin/bash

###############################################
###       SLURM script for ML Mapmaking    ####
###                                        ####
###    Tested on Uni koeln Ramses Cluster  ####
###             v2.0 , 19.02.2025          ####
###############################################

### This script runs the ML-pipeline for a given set of detector TODs
### *** NOTE ***: -- PARENT_DIR parameter must be set in Section 4
###		  -- Set config.yaml parameter


### section 1 - SLURM params

#SBATCH --partition=mpi
#SBATCH --account=ag-riechers # For Ramses/ CCAT
### cluster specific; ramses / mpi(mpi+multi-node), smp(no_mpi+single-node), bigsmp(big-mem)
### https://gitlab.git.nrw/uzk-itcc-hpc/itcc-hpc-ramses/-/wikis/SLURM

#SBATCH --ntasks-per-node 32  # tasks per node ; num of processes per node
#SBATCH --cpus-per-task 6     # number of cores per task ; threads per process

#SBATCH --nodes 1             # number of nodes

#SBATCH --job-name=det1000_n32c6nd1_mlTQU
### Job name, det#ndets_#ntasks#corespertask#n_nodes_ml


#SBATCH --mem=700G            # max mem requested, per node, baseline 400G
### Maximum requested time (days-hrs:min:sec)
#SBATCH --time 0-03:00:00     #estimated runtime max, baseline 0-08:00:00 
#SBATCH --exclusive

#SBATCH --output ./logs_mlmap/%j.%x.out    
#SBATCH --error ./logs_mlmap/%j.%x.err     


### section 2 - Runtime env set-up
echo ""
echo "*************"
echo "Loading Modules and Env..."
module purge
### load all modules needed for Job
module load lang/Miniconda3/23.9.0-0
module load lib/mpi4py/3.1.5-gompi-2023b
### initiate conda
conda deactivate
conda activate mlmap
echo "*************"
### Exit if a command exits with a non-zero status
set -e

### section 3 - Job Logging
echo ""
echo "*************"
echo "Running Job..."
echo "Starting at `date`"
echo "SLURM partition: $SLURM_JOB_PARTITION"
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
echo "Python version: $(python --version)"
echo "Using mpi4py: $(python -c 'import mpi4py; print(mpi4py.__file__)' 2>/dev/null || echo '!! mpi4py not found !!')"
echo "Using MPI lib: $(which mpirun)"
echo "Using mpicc lib: $(which mpicc)"
echo "Using GCC lib: $(which gcc)"
echo ""


### section 4 - Set Job parameters
### Set TOD data dir
PARENT_DIR="deep56_data_d1000"

DATA_DIR="ccat_datacenter_mock/data_testmpi/"
FULL_DATA_PATH="${DATA_DIR}${PARENT_DIR}"
ML_CONFIG="config.yaml"

### section 5 - Job Run
echo "***** EXEC SCRIPT *****"
echo `date '+%F %H:%M:%S'`
echo "***********************"
echo ""

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

### Build context data
echo ""
echo "Building context data ..."
echo ""
mpirun -np $SLURM_NTASKS python write_context_primecam_mpi.py $FULL_DATA_PATH

### Build Map Footprint
echo ""
echo "Building map footprint ..."
echo ""
mpirun -np $SLURM_NTASKS python write_footprint_primecam_mpi.py

### Build Map
echo ""
echo "Building ML map ..."
echo ""
mpirun -np $SLURM_NTASKS python make_ml_map_primecam.py --config $ML_CONFIG

echo ""
echo "******** DONE *********"
echo `date '+%F %H:%M:%S'`
echo "***********************"

