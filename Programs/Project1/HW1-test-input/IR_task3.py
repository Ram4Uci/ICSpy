
import time
import string
import sys
import re

path1=str(sys.argv[1]) #Input Path1
path2=str(sys.argv[2]) #Input Path2
path3=str(sys.argv[3]) #Output Path

def Creator():      # Creates a word frequecies of file 1
    dict1={}
    with open(path1,"r") as f:
        for line in f:
            line=line.split(',')
            dict1[line[0]]=int(line[1])
    return dict1

def Comparer(dict2): # Creates a word frequencies combining both files
    with open(path2,"r") as g:
        for line in g:
            line=line.split(',')
            if(line[0] not in dict2.keys()):
                dict2[line[0]]=int(line[1])
            else:
                dict2[line[0]]+=int(line[1])
    return dict2

def Compiler(dict3): # Writes the word frequencies to the file
    with open(path3,"w") as h:
        for key,value in sorted(dict3.items()):
            h.write("%s,%s\n"%(key,value))
    return

print("\n\n Begin ...")
start=time.time()
Compiler(Comparer(Creator()))
print("\n\n Finished !!! \n\n Exeution Time=",time.time()-start," s")        
    
