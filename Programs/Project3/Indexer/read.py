import json
import math
from math import log10
N = 29390
with open("heads.json") as head:
    for line in json.loads(head,'\n'):
        n=json.dumps(line)
        print type(n)
        raw_input()
    '''
    for line in lines:
        js = line
        print type(line)
        df = log10(N/len(js))
        print "df = ",df
        #print line
        print line[0]
        raw_input (line[1])
        
        for key,value in js:
            val= js[key]
            tf = log10( 1 + val )
            print tf
            tfidf = tf * df
            print tfidf
            raw_input()
    
    '''
