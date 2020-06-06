#!/bin/bash
#SBATCH --job-name=TBA1                   # Job name
#SBATCH --time=10:15:00
#SBATCH --nodes=1                               # Number of nodes
#SBATCH --ntasks-per-node=36                    # Number of processors per node
#SBATCH -A bar                           # Allocation
##SBATCH --account=bar                           # Allocation
#SBATCH --mail-user emmanuel.branlard@nrel.gov  # E-mail adres
#SBATCH --mail-type BEGIN,END,FAIL              # Send e-mail when job begins, ends or fails

export n=3
python -u GenerateTurbBox.py A1 133 1 $n  &
python -u GenerateTurbBox.py A1 133 2 $n  &
python -u GenerateTurbBox.py A1 133 3 $n 
