#!/bin/bash
#SBATCH --job-name=TBA2                   # Job name
#SBATCH --time=38:15:00
#SBATCH --nodes=1                               # Number of nodes
#SBATCH --ntasks-per-node=36                    # Number of processors per node
#SBATCH -A bar                           # Allocation
##SBATCH --account=bar                           # Allocation
#SBATCH --mail-user emmanuel.branlard@nrel.gov  # E-mail adres
#SBATCH --mail-type BEGIN,END,FAIL              # Send e-mail when job begins, ends or fails

export n=3
python -u GenerateTurbBoxA2.py 1  $n  &
python -u GenerateTurbBoxA2.py 2  $n  &
python -u GenerateTurbBoxA2.py 3  $n 
# python -u GenerateTurbBox.py 4  $n  &
# python -u GenerateTurbBox.py 5  $n  &
# python -u GenerateTurbBox.py 6  $n 
# python -u GenerateTurbBox.py 7  $n  
# python -u GenerateTurbBox.py 8  $n  &
# python -u GenerateTurbBox.py 9  $n  

#python -u GenerateTurbBox.py 10 $n > slurm-10.out &
# python -u GenerateTurbBox.py 11 $n > slurm-11.out &
# python -u GenerateTurbBox.py 12 $n > slurm-014.out &
# python -u GenerateTurbBox.py 13 $n > slurm-015.out &
# python -u GenerateTurbBox.py 14 $n > slurm-016.out &
# python -u GenerateTurbBox.py 15 $n > slurm-017.out &
# python -u GenerateTurbBox.py 16 $n > slurm-020.out &
# python -u GenerateTurbBox.py 17 $n > slurm-021.out &
# python -u GenerateTurbBox.py 18 $n > slurm-022.out 

