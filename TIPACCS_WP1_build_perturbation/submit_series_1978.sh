#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=5 
#SBATCH --ntasks-per-node=5 
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

YEARE=$((YEARS+9))
LSTYEAR=`eval echo {${YEARS}..${YEARE}}`
rm job_${YEARS}-${YEARE}_${EXT}.dat
for YEAR in $LSTYEAR; do
   echo "./Add_A1B_HadCM3_anomaly_to_JRA_data.py --years $YEAR --yeare $YEAR --fileext ${EXT} > log_$YEAR-${EXT} 2>&1" >> job_${YEARS}-${YEARE}_${EXT}.dat
done

srun -n 4 pserie_lb < job_${YEARS}-${YEARE}_${EXT}.dat
