import numpy as np

with open("conv_v.txt",'w') as f:
    for i in range(0,100):
        for j in range(0,100):
            f.write("ans[%d]<=" % (100*i+j))
            for a in range(-1,2):
                for b in range(-1,2):
                    if (i + a >= 0) and (i + a <= 99) and (j + b >= 0) and (j + b <= 99):
                        if ((a == 1) and (b == 1 or j+b==99)) or (b == 1 and (a==1 or i+a==99)) 
                            or (j+b==99 and i+a==99):
                            f.write("tmp[%d]*kernel[%d];\n" % (100*(i+a)+j+b, 3*(a+1)+b+1))
                        else:
                            f.write("tmp[%d]*kernel[%d]+" % (100*(i+a)+j+b, 3*(a+1)+b+1))
        