icc -c bb_bem.c
ifort -c user_func.f90
icc bb_bem.o user_func.o -o bb_bem
