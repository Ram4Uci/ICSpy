from pymongo import MongoClient
import pprint
import json
client = MongoClient()

db = client[raw_input("DB")]
with open("Docdump.json","w") as docj:
    while raw_input("Continue ? Y / N ") != "n":
        dicct = {}
        index =  raw_input("Letter")
        coll = db[index]
        cursor = coll.find({"word":raw_input("word")})
        for doc in cursor:
            pprint.pprint(doc)
