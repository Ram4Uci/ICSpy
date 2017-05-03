#!/usr/bin/env python
from Part_A import tokenize
import re
import time
import sys
if (len(sys.argv) != 4):
    print("Number of arguments is wrong")
    print("1.Input file 1    2.Input file 2  3. Output file ")
else:
    start = time.time()
    Token1 = tokenize(sys.argv[1])
    Token2 = tokenize(sys.argv[2])
    st1 = set(Token1)
    st2 = set(Token2)
    common = st1.intersection(st2)
    print("Number of matching occurences: ",len(common))
    with open(sys.argv[3],'w') as filehandle:
           for token in sorted(common):
               filehandle.write("%s\n" % token)
    end = time.time()
    elapsed = end - start
    print("Time elapsed(sec) ",elapsed)
