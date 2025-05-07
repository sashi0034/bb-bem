nvcc -o bb_bem bb_bem.c bicgstab_naive.c user_func.c bicgstab_cuda.cu bicgstab_cuda_wmma.cu -arch=sm_80
