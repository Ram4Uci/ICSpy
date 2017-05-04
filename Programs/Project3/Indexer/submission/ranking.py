import index
import os
import string
import json
from urlparse import urlparse
from flask import Flask, render_template,redirect,request

from bs4 import BeautifulSoup
from lxml.html import soupparser
import nltk, re, pprint
import magic
from nltk.util import ngrams 
from pprint import pprint
from nltk import word_tokenize,sent_tokenize          
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
import math
from nltk.corpus import stopwords
from collections import Counter


client = MongoClient()
db = client.new_index
fancy_db = client.fancy_index
stemmer = PorterStemmer()
query = ""
urls_dict = dict()
docDict=dict()

url_list = []

PR=dict()
with open("pr_new.json") as prj:
    PR = json.load(prj)
json_data = dict()    
with open("../bookkeeping.json") as jsonf:
    json_data = json.load(jsonf)

app = Flask(__name__)

@app.route('/query', methods = ['POST'])
def signup():
    global query
    global url_list
    global file_list
    url_list = []
    query= request.form['query']
    file_list = find_best_ranked(query)
    loadjson(file_list)
    #print file_list
    print("The Query is :- " + query + "\n")
    return redirect('/results')

@app.route('/')
def hello_world():
    return render_template('index.jsp')

@app.route('/results')
def results():
    global file_list
    global url_list
    author = "Ramkumar"
    name = "Yashaswini"
    return render_template('results.html', title=author,url_list = url_list,url_dict=urls_dict)



def docList(word):
	global docDict
	word_list = list()
	if word =="":
            return
	word_list.append(word.lower())
	letter = index.getLetter(word) #+ "_new"
	# print letter
	index_file = index.getIndexName(letter) + "_new"
	my_collection = db[index_file]
	result = my_collection.find({"word": word}).limit(1)
	res = list(result)
	# print "res:", res
	doc_result = list()

	if res: 
		# print "index: ", res[0]['index']
		#print "word: ", res[0]['word']
		#print "df: ", res[0]['df']

		for document in res[0]['index']:
			# print "Here"
			# print res[0]['word']
			doc_result.append((document, res[0]['index'][document][1]))
			docDict[res[0]['word']] = docDict.get(res[0]['word'], {})
			docDict[res[0]['word']][document] = res[0]['index'][document][0]
			# print docDict

		ret_val = res[0]['index']

	else:
		ret_val = {}

	# print docDict
	return doc_result


def get_key_docList(word):
	word_list = list()
	word_list.append(word.lower())
	
	my_collection = db["title_index"]
	# print "\n\n",word, "\n\n"
	result = my_collection.find({"word": word}).limit(1)
	res = list(result)
	# print "res:", res
	doc_result = list()

	if res: 
		# print "index: ", res[0]['index']
		#print "word: ", res[0]['word']
		#print "idf: ", res[0]['idf']

		for document in res[0]['index']:
			doc_result.append((document, res[0]['index'][document]))

		# ret_val = res[0]['index']

	
	return doc_result
    
def get_base_docList(word):
	word_list = list()
	word_list.append(word.lower())
	
	my_collection = db["tag_index"]
	
	# print "\n\n",word, "\n\n"
	result = my_collection.find({"word": word}).limit(1)
	res = list(result)
	# print "res:", res
	doc_result = list()

	if res: 
		# print "index: ", res[0]['index']
		#print "word: ", res[0]['word']
		#print "idf: ", res[0]['idf']

		for document in res[0]['index']:
			doc_result.append((document, res[0]['index'][document]))

		# ret_val = res[0]['index']

	#print len(doc_result)
	#raw_input()
	return doc_result

def rank_results(results):
	pass

def process_query(query):
	stop_words = set(stopwords.words('english'))
	query = re.sub(r'[\W_]+', ' ', query)
	words = [word.strip().lower() for word in query.split(" ") if word not in stop_words]
	# print words
	wordDict = dict()
	intersection = set()
	results = list()
	unionDict = dict()

	for word in words:
            word = stem_word(word, stemmer)
            # print word
            # print "Here"
            wordDict[word] = docList(word) #Should get back a list of form : [(docID1, tf-IDF1), (docID2, tf-IDF2).....]
            # print wordDict[word]
            for doc in wordDict[word]:
		unionDict[doc[0]] = unionDict.get(doc[0], 0)
		unionDict[doc[0]] += doc[1]	#Add Tf-idf values for that doc
        #print unionDict
        #print "\n\n\nUnionDict",query,"\n\n\n"
        #raw_input()
	return [(x, unionDict[x]) for x in sorted(unionDict, key = unionDict.get, reverse = True)]



def process_key_query(query):
	stop_words = set(stopwords.words('english'))
	query = re.sub(r'[\W_]+', ' ', query)
	words = [word.strip().lower() for word in query.split(" ") if word not in stop_words]
	# print words
	wordDict = dict()
	intersection = set()
	results = list()
	unionDict = dict()

        for word in words:
            word = stem_word(word, stemmer)
	    # print word
            wordDict[word] = get_key_docList(word) #Should get back a list of form : [(docID1, tf-IDF1), (docID2, tf-IDF2).....]
            # print wordDict[word]
            for doc in wordDict[word]:
                unionDict[doc[0]] = unionDict.get(doc[0], 0)
		unionDict[doc[0]] += doc[1]	#Add Tf-idf values for that doc
        #pprint (unionDict)
        #raw_input()
	return [(x, unionDict[x]) for x in sorted(unionDict, key = unionDict.get, reverse = True)]
def process_base_query(query):
	stop_words = set(stopwords.words('english'))
	query = re.sub(r'[\W_]+', ' ', query)
	words = [word.strip().lower() for word in query.split(" ") if word not in stop_words]
	# print words
	wordDict = dict()
	intersection = set()
	results = list()
        unionDict = dict()


	for word in words:
            word = stem_word(word, stemmer)
            # print word
            wordDict[word] = get_base_docList(word) #Should get back a list of form : [(docID1, tf-IDF1), (docID2, tf-IDF2).....]
            # print wordDict[word]
            for doc in wordDict[word]:
                
		unionDict[doc[0]] = unionDict.get(doc[0], 0)
		unionDict[doc[0]] += doc[1]	#Add Tf-idf values for that doc
       
	return [(x, unionDict[x]) for x in sorted(unionDict, key = unionDict.get, reverse = True)]

def compare(x, y):
	if x[1] > y[1]:
		return -1

	elif x[1] == y[1]:
		return 0

	return 1

def stem_word(word, stemmer):

	try:
		stemmed = stemmer.stem(word)
		
	except UnicodeDecodeError:
		pass
	
	# print "stemmed: ", stemmed
	return stemmed
def combine(result, key_result, base_result):
	tf_idf = 0
	alpha = 20
	gamma = 20
	beta = 30
	delta = 10
	epsilon = 20
	global query
	global flag
	scoreDict = proximity_search(query)
	global PR
	global json_data
	tf_idf_res = dict()
	sets = set(result) | set(key_result) | set(base_result)
	
            
	for doc in sets:
                urls = json_data.get(doc,"Error")
                if urls == "Error":
                    continue
                urls = urls.strip().rstrip('/')
                pr_score = PR.get(urls,0)
                prox_score = scoreDict.get(doc,0)
                #print pr_score
                #raw_input()
                a = result.get(doc,0) *  alpha
                b = key_result.get(doc,0)  * beta
                c = base_result.get(doc,0) * gamma
                d = pr_score * delta
                e = prox_score * epsilon
                
                tf_idf = a + b + c + d + e
                if doc == "49/98":
                    print "a" + str(a) + "b" + str(b) + "c" + str(c) + "d" + str(d) + "e" + str(e)
		#print str(base_result.get(doc,0))
		tf_idf_res[doc] = tf_idf
	
	
	for x in sorted(tf_idf_res,key = tf_idf_res.get, reverse = True):
            #pprint(str(x) + " " + str(tf_idf_res[x]))
            pass


	return [x for x in sorted(tf_idf_res, key = tf_idf_res.get, reverse = True)][:20]

abrv = dict()
abrv["machine learning"] = "ml"
abrv["artificial intelligence"] = "ai"
abrv["information retrieval"] = "ir"

def find_best_ranked(query):
	query = query.lower()
	if query in abrv.keys():
		query += " " + abrv[query]
		print query

	result = process_query(query)
	print "One"
	key_result = process_key_query(query)
	base_result = process_base_query(query)
	# print dict(result)
	# print "-----------------" * 10
	# print dict(fancy_result)
	#pprint(result)
	#print "\n\n\n"
	#pprint(key_result)
	#print "\n\n\n"
	#pprint (base_result)
	#print "\n\n\n"

	return combine(dict(result), dict(key_result), dict(base_result))

def loadjson(file_list):
        global url_list
        global json_data
        global urls_dict
        for f in file_list:
            url_dict={}
            urls = json_data.get(f,"Does not exist")
            if(urls != "Does not exist"):
                urls = "https://" + urls
                #print urls
                url_list.append(urls.strip().rstrip('/'))
                urls_dict[urls] = getsnippet(f,query)
        lists = list()
        for url in url_list:
            if url not in lists:
                lists.append(url)
                
        url_list = lists[:15]

def proximity_search(query):
	query = re.sub(r'[\W_]+', ' ', query)
        global docDict
	token = nltk.word_tokenize(query.lower())
	token = [stemmer.stem(x) for x in token]
	bigrams = ngrams(token, 2)

	scoreDict = dict()

	for bigram in bigrams:
		d1 = docDict.get(bigram[0],[])
		d2 = docDict.get(bigram[1],[])

		common_docs = set(d1) & set(d2)
		for doc in common_docs:
			pos_d1 = d1[doc]
			pos_d2 = d2[doc]

			results = [(x, y) for x in pos_d1 for y in pos_d2 if y == x + 1]
			scoreDict[doc] = scoreDict.get(doc, 0)
			scoreDict[doc] += len(results)

	return scoreDict

def getsnippet(fileName, query):
	query = re.sub(r'[\W_]+', ' ', query)
	token = nltk.word_tokenize(query)
	# token = [stemmer.stem(x) for x in token]
	token = [x.lower() for x in token]
        if len(token) > 1:
            bigrams = list(ngrams(token, 2))
            bigram = bigrams[0]
        else:
            bigram = token
	res = ""

	with open("../WEBPAGES_RAW/" + fileName, "r") as f:
		content = f.read()
		try:
			root = BeautifulSoup(content,"lxml")

		except (Exception, UnicodeDecodeError) as e:
			return res

		for script in root(["script", "style"]):
			script.extract()    #extract these unnecessary tags

                text = root.find('body')
                text = text.get_text()
                

		sentences =list( sent_tokenize(text))
                
                lists = list()
                
                for sentence in sentences:
                     sentence=re.sub(r'[\W_]+',' ',sentence)
                     sentence = sentence.strip()
                    
                     if len(bigram) == 1:
                         if bigram[0] in sentence:
                             lists.append(sentence )
                     else:
                         if bigram[0] in sentence or bigram[1] in sentence:
                             lists.append(sentence )
                     #print sentence + "\n"
                     if len(lists) > 2:
                         break
                result ='.'.join(lists)
                try :
                    tit = root.find('title').get_text().strip()              
                    if result == "":
                        result = tit
                        result = re.sub(r'[\W_]+',' ',result).strip()
                    return result[:250]
                except AttributeError:
                    return result[:250]
		#raw_input()
                '''
		i = 0
		sent_index = -1
		
		for sentence in sentences:
			tokens = word_tokenize(sentence)

			if len(bigram) == 1 and bigram[0] in tokens:
				sent_index = i
				break

			elif len(bigram) == 2 and bigram[0] in tokens and bigram[1] in tokens:
				sent_index = i
				break
                        elif sent_index == -1 and len(bigram) == 2 and (bigram[0] in tokens or bigram[1] in tokens):
                            sent_index = i
                            break
			else:
				i += 1

		if sent_index != -1:
			if sent_index == 0:
				if len(sentences) != 1:
					res = " ".join([sentences[0], sentences[1]])

				else:
					res = sentences[0]

			else:
				res = " ".join([sentences[i - 1], sentences[i]])

		else:
			res = ""
        print res

	return res
'''
if __name__ == '__main__':

        app.run()
	# result = docList('retrieval')
	# print result
	# query = raw_input()
	# result = process_query(query)
	# print result
