#!/bin/bash
#SBATCH --job-name=TBB1                   # Job name
#SBATCH --time=01:59:00
#SBATCH --nodes=1                               # Number of nodes
#SBATCH --ntasks-per-node=36                    # Number of processors per node
#SBATCH -A bar                           # Allocation
#SBATCH --mail-user emmanuel.branlard@nrel.gov  # E-mail adres
#SBATCH --mail-type BEGIN,END,FAIL              # Send e-mail when job begins, ends or fails
#SBATCH -o slurm-%x-%j.log                      # Output

python -u GenerateTurbBox.py B1 161 F  &
python -u GenerateTurbBox.py B1 161 F  &
python -u GenerateTurbBox.py B1 161 T 
