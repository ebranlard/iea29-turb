#!/bin/bash
#SBATCH --job-name=TB                   # Job name
#SBATCH --time=3:30:00
#SBATCH --nodes=1                               # Number of nodes
#SBATCH --ntasks-per-node=36                    # Number of processors per node
#SBATCH -A bar                           # Allocation
##SBATCH --account=bar                           # Allocation
#SBATCH --mail-user emmanuel.branlard@nrel.gov  # E-mail adres
#SBATCH --mail-type BEGIN,END,FAIL              # Send e-mail when job begins, ends or fails

python --version
python -c 'import struct;print( 8 * struct.calcsize("P"))'
ls
python GenerateTurbBox.py
