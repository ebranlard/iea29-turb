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


export n=10
python -u GenerateTurbBox.py 1  $n  &
python -u GenerateTurbBox.py 2  $n  &
python -u GenerateTurbBox.py 3  $n  &
python -u GenerateTurbBox.py 4  $n  &
python -u GenerateTurbBox.py 5  $n  &
python -u GenerateTurbBox.py 6  $n  &
python -u GenerateTurbBox.py 7  $n  &
python -u GenerateTurbBox.py 8  $n  &
python -u GenerateTurbBox.py 9  $n  &
python -u GenerateTurbBox.py 10 $n 

