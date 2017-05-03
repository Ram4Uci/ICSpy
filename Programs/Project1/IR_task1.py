#Documentation referred from docs.python.org

import time 
import string
import re
import sys
import operator
import json


path=str(sys.argv[1]) # Input file name
op_path=str(sys.argv[2]) # Output file name

def Tokens(paths): # To create a list of words 
    list1=[]
    extend=list1.extend
    with open(paths,"r") as f:
        for line in f:
            line=re.sub('[^0-9a-zA-Z]',' ',line)
            extend(line.lower().split())
    return list1

def CountTokens(lists): # To map the word-count frequency
    dict1={}
    keys=dict1.keys
    for word in lists:
        if (word not in keys()) :
            dict1[word]=1;
        else:
            dict1[word]+=1;
    del lists
    return dict1;

def printTokens(dict2): #To print the tokens after sorting into a file.
    with open(op_path,"w") as f:
        write=f.write
        dictz=sorted(dict2.items(),key=operator.itemgetter(1),reverse=True)
        dict3 = {k:v for k,v in dictz }
        dict4={}
        dict4["keys"]=dict3
        json_array=json.dumps(dict4)
        print json_array
        data=json.loads(json_array)
        print data["keys"]
        for key,value in sorted(dict2.items(),key=lambda x:x[1],reverse=True):
            #print("%s = %s" % (key,value) Print to Console
            write("%s,%s\n" %(key,value)) #Print to File
    #print(len(dict2))
    del dict2
    return

print("\n\n Begin...")
start=time.time()
printTokens(CountTokens(Tokens(path)))
print("\n Finished !!! \n\n Execution time = " , time.time()-start," s")


