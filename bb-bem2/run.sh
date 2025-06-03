#!/bin/bash

# -----------------------------------------------
#SBATCH -t 12:00:00
#SBATCH --rsc p=1:t=64:c=64:m=500G
#SBATCH -o out/%x.%j.out # %x: job name, %j: job id
# -----------------------------------------------

# ./bb_bem ../input_data/cube_100x100x100.stl -o ../output_data/cube_100x100x100.out -m cuda_wmma
# ./bb_bem ../input_data/cube_100x100x100.stl -o ../output_data/cube_100x100x100.out

# Simulation 6/3
./bb_bem ../input_data/torus-sd.stl -o ../output_data/torus-sd.out -m cuda_wmma
