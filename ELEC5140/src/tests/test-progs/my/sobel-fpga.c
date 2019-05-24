/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* 2mm.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
// #include "../../../utilities/polybench.h"

/* Include benchmark-specific header. */
// #include "2mm.h"
#include <new>
using namespace std;
unsigned long long *p0;

/* Array initialization. */
static
void init_array(int *array)
{
    FILE *fp;
    int i,j;
    fp=fopen("image.txt","r");
    for (i=0;i<100;i++){
        for (j=0;j<99;j++){
            fscanf(fp, "%d,", &(array[j+100*i]));
        }
        j = 99;
        fscanf(fp, "%d,\n", &(array[j+100*i]));
    }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int *array)
{
  FILE *fp;
  int i, j;
    fp=fopen("image_out.txt","w");
    for (i=0;i<100;i++){
        for (j=0;j<99;j++){
            fprintf(fp, "%d,", array[j+100*i]);
        }
        j = 99;
        fprintf(fp, "%d\n", array[j+100*i]);
    }
}


int mulD(int a,int b)
{
	int tmp;
//#pragma HLS RESOURCE variable=tmp core=Mul
	tmp=a*b;
	return tmp;
}

int addD(int a,int b)
{
	int tmp;
//#pragma HLS RESOURCE variable=tmp core=AddSub
	tmp=a+b;
	return tmp;
}

/* Main computational kernel. The whole function will be timed,
   including the call and return. */
//static

  int indata[100*100];

int main(int argc, char** argv)
{
    p0 =(unsigned long long *) new((unsigned long long *)0xc0000000) unsigned long long[10];//Contro Port
    //printf("111111");
    p0[1] = (unsigned long long)indata;//ReadBase
    p0[2] = (unsigned long long)indata;//WriteBase
    p0[0] = 81;	
    p0[8] = 1;
    p0[3] = 9;//CurrentThreadID
    p0[4] = 100*100+2;//Memory Range
    p0[5] = 4;//MemorySize
    p0[7] = 0;//Terminat
    /* Initialize array(s). */
    p0[6]=0;p0[6]=0;
    init_array (indata);
    //Strating occupy FPGA
    p0[6]=1;    
    //Wait for release
    while(p0[6]); 
    //Save for data
    print_array(indata);

    return 0;
}
