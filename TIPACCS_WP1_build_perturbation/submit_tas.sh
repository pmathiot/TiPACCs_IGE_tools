#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=3 
#SBATCH --ntasks-per-node=3
#SBATCH --constraint=BDW28
#SBATCH --threads-per-core=1
#SBATCH -J JRA_pert_1978
#SBATCH -e JRA_pert.e%j
#SBATCH -o JRA_pert.o%j
#SBATCH --time=04:30:00
#SBATCH --exclusive
module purge 
module load intel/17.0 
module load openmpi/intel/2.0.1 
module load pserie

ulimit -s unlimited

. ~/.bashrc

conda activate A1B_perturbation
echo $CONDA_DEFAULT_ENV

set -x

EXT=20602100-19792019
YEARS=1978
YEARE=2018

rm job_tas.dat
echo "python Add_A1B_HadCM3_anomaly_to_JRA_data.py --yeare $YEARE --years $YEARS --fileext 20602100-19792019 > log_tas_20602100-19792019 2>&1" >> job_tas.dat
echo "python Add_A1B_HadCM3_anomaly_to_JRA_data.py --yeare $YEARE --years $YEARS --fileext 21602200-19792019 > log_tas_21602200-19792019 2>&1" >> job_tas.dat

srun -n 3 pserie_lb < job_tas.dat
