module load PrgEnvNvidia
nvcc -DNO_TRACE -O2 -Xcompiler -fopenmp -o bb_bem bb_bem.c stl_loader.c bicgstab_naive.c user_func.c bicgstab_cuda.cu bicgstab_cuda_wmma.cu -arch=sm_80
