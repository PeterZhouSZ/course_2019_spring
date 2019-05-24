"""
This script it to use PAAS framework to perfom a sobel filter on image

Author: CHENG Wei
Contact: wchengad@connect.ust.hk
"""
print(__doc__)

import numpy as np
import cv2
import argparse

def write_text(im):
    with open('image.txt', 'w') as f:
        for i in range(0,100):
            for j in range(0, 100):
                f.write("%d," % (im[i,j]))
            f.write("\n")

def read_text(f):
    im = []
    for line in f:
      for data in line.split(','):
            im.append(data)
    im = np.reshape(im, (100,100))
    return im



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PASS')
    parser.add_argument('--input',type=str, nargs='+',
                        help='input image')
    parser.add_argument('--output', type=str, nargs='+',
                        help='input image')
    args = parser.parse_args()
    print(args)

    # read input data and transfer it to plain txt
    im = cv2.imread(args.input[0])
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im = cv2.resize(im, (100,100))
    cv2.imwrite('resize.png', im)
    write_text(im)

    # system command call PAAS to run sobel-fpga.py
    os.system("./build/X86/gem5.opt configs/my/sobel-fpga.py --ruby --num-cpus=1 --num-fpgas=1")

    # wait until data ready
    while(1):
        try: 
            with open('image_out.txt', 'r+') as f:
                sobely = read_text(f)
                sobely = cv2.resize(sobely, (100,100))
                cv2.imwrite(args.output[0], sobely)
        except EnvironmentError:
            # File not ready, wait
            sleep(0.01)


