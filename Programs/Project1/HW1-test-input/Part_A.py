#!/usr/bin/env python
import sys
import re
import time
import os
def tokenize(path):
    if os.path.isfile(path):
        Token = []
        with open(path,"r") as fh:
            for line in fh:
                line = re.sub('[^0-9a-zA-Z]',' ',line)
                Token.extend(line.lower().split())
        return Token
    else:
         sys.exit("Input File does not exits")
def computeWordFrequencies(Token):
    freq = {}
    for word in Token:
        if word in freq:
            freq[word] += 1
        else:
            freq[word] = 1
    #print("Unique Word Count: ", len(freq))
    del Token
    return freq

def printWordFrequencies(Frequencies,path):
    with open(path,'w') as filewrite:
        for key,value in sorted(Frequencies.items(),key=lambda k:k[1],reverse = True):
            #print("%s : %s \n" %(key,value))
            filewrite.write("%s,%s\n" %(key,value))
    del Frequencies

if __name__=="__main__":
    if (len(sys.argv) != 3):
        print("Number of arguments is wrong")
        print("1.Input file    2. Output file ")
    else:
        start = time.time()
        output_path1 = sys.argv[2]
        print("@@@@@ Tokenization @@@@")
        printWordFrequencies(computeWordFrequencies(tokenize(sys.argv[1])),output_path1)
        end = time.time()
        elapsed = end - start
        print("Time elapsed(sec) ", elapsed)

     
         
