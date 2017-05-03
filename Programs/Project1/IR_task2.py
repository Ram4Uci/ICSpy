
import time
import sys
import string
import re

path_ip1=str(sys.argv[1]) #Input File 1
path_ip2=str(sys.argv[2]) #Input File 2
path_op1=str(sys.argv[3]) #Output File

def commonwords(path1,path2): # Forms set of tokens and takes the intersection.
    count1=0
    set1=set()
    set2=set()
    add1=set1.add
    add2=set2.add
    with open(path1,"r") as f:
        for line in f:
            line=re.sub('[^0-9a-zA-Z]+',' ',line)
            for word in line.lower().split():
                add1(word)
    with open(path2,"r") as g:
        for line1 in g:
            line1=re.sub('[^0-9a-zA-Z]+',' ',line1)
            for word1 in line1.lower().split():
                add2(word1)
    set3=set1&set2
    with open(path_op1,"w") as o:
        for x in set3:
            o.write("%s\n" % x)
    #print(set3)
    print("\n\n Number of Common Words = %s \n\n" % len(set3) )
    return

print("\n\n Begin...")
start=time.time()
commonwords(path_ip1,path_ip2)
print(" Execution time= ", time.time()-start, " s")

