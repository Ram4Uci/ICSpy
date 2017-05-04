#import index
import os
import string
import json
from urlparse import urlparse
from flask import Flask, render_template,redirect,request

from bs4 import BeautifulSoup
from lxml.html import soupparser
import nltk, re, pprint
import magic
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
import math
from nltk.corpus import stopwords
from collections import Counter


client = MongoClient()
db = client.inverted_index_new
fancy_index = client.fancy_index
stemmer = PorterStemmer()
query = ""
url_list = []

app = Flask(__name__)

@app.route('/query', methods = ['POST'])
def signup():
    global query
    global url_list
    global file_list
    url_list = []
    query= request.form['query']
    file_list = find_best_ranked(query)
    print file_list
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
    return render_template('results.html', title=author,url_list = url_list)



def docList(word):
	word_list = list()
	word_list.append(word.lower())
	letter = index.getLetter(word)
	index_file = index.getIndexName(letter)
	my_collection = db[index_file]
	result = my_collection.find({"word": word}).limit(1)
	res = list(result)
	# print "res:", res
	doc_result = list()

	if res: 
		# print "index: ", res[0]['index']
		print "word: ", res[0]['word']
		print "df: ", res[0]['df']

		for document in res[0]['index']:
			doc_result.append((document, res[0]['index'][document][1]))

		ret_val = res[0]['index']

	else:
		ret_val = {}
	return doc_result


def get_key_docList(word):
	word_list = list()
	word_list.append(word.lower())
	
	my_collection = fancy_db["key_index"]
	# print "\n\n",word, "\n\n"
	result = my_collection.find({"word": word}).limit(1)
	res = list(result)
	# print "res:", res
	doc_result = list()

	if res: 
		# print "index: ", res[0]['index']
		print "word: ", res[0]['word']
		print "idf: ", res[0]['idf']

		for document in res[0]['index']:
			doc_result.append((document, res[0]['index'][document]))

		# ret_val = res[0]['index']

	
	return doc_result
def get_base_docList(word):
	word_list = list()
	word_list.append(word.lower())
	
	my_collection = fancy_db["base_index"]
	# print "\n\n",word, "\n\n"
	result = my_collection.find({"word": word}).limit(1)
	res = list(result)
	# print "res:", res
	doc_result = list()

	if res: 
		# print "index: ", res[0]['index']
		print "word: ", res[0]['word']
		print "idf: ", res[0]['idf']

		for document in res[0]['index']:
			doc_result.append((document, res[0]['index'][document]))

		# ret_val = res[0]['index']

	
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
	


	for word in words:
		word = stem_word(word, stemmer)
		# print word
		wordDict[word] = docList(word) #Should get back a list of form : [(docID1, tf-IDF1), (docID2, tf-IDF2).....]
		# print wordDict[word]
		if intersection == set():
			# print "\n\nWord: " + word + "\n\n"
			# print wordDict[word] 
			# print "\n\n"
			intersection.update([x[0] for x in wordDict[word]])

		else:
			# print "Here"
			intersection = intersection & set([x[0] for x in wordDict[word]])

	# print intersection
	print "SIZE: ", len(intersection)

	# if intersection != set():
	# 	results.extend([(x, getTF_IDF(query, x)) for x in intersection])

	tf_idfDict = dict()
	result_dict = dict()
	counter = Counter()

	for word in words:
		result = dict([x for x in wordDict[stem_word(word, stemmer)] if x[0] in intersection])
		counter.update(result)

	return [(x, counter[x]) for x in sorted(counter, key = counter.get, reverse = True)][:20]



def process_key_query(query):
	stop_words = set(stopwords.words('english'))
	query = re.sub(r'[\W_]+', ' ', query)
	words = [word.strip().lower() for word in query.split(" ") if word not in stop_words]
	# print words
	wordDict = dict()
	intersection = set()
	results = list()
	


	for word in words:
		# word = stem_word(word, stemmer)
		# print word
		wordDict[word] = get_key_docList(word) #Should get back a list of form : [(docID1, tf-IDF1), (docID2, tf-IDF2).....]
		# print wordDict[word]
		if intersection == set():
			# print "\n\nWord: " + word + "\n\n"
			# print wordDict[word] 
			# print "\n\n"
			intersection.update([x[0] for x in wordDict[word]])

		else:
			# print "Here"
			intersection = intersection & set([x[0] for x in wordDict[word]])

	# print intersection
	print "SIZE: ", len(intersection)

	# if intersection != set():
	# 	results.extend([(x, getTF_IDF(query, x)) for x in intersection])

	tf_idfDict = dict()
	result_dict = dict()
	counter = Counter()

	for word in words:
		result = dict([x for x in wordDict[word] if x[0] in intersection])
		counter.update(result)

	return [(x, counter[x]) for x in sorted(counter, key = counter.get, reverse = True)][:20]

def process_base_query(query):
	stop_words = set(stopwords.words('english'))
	query = re.sub(r'[\W_]+', ' ', query)
	words = [word.strip().lower() for word in query.split(" ") if word not in stop_words]
	# print words
	wordDict = dict()
	intersection = set()
	results = list()
	


	for word in words:
		# word = stem_word(word, stemmer)
		# print word
		wordDict[word] = get_base_docList(word) #Should get back a list of form : [(docID1, tf-IDF1), (docID2, tf-IDF2).....]
		# print wordDict[word]
		if intersection == set():
			# print "\n\nWord: " + word + "\n\n"
			# print wordDict[word] 
			# print "\n\n"
			intersection.update([x[0] for x in wordDict[word]])

		else:
			# print "Here"
			intersection = intersection & set([x[0] for x in wordDict[word]])

	# print intersection
	print "SIZE: ", len(intersection)

	# if intersection != set():
	# 	results.extend([(x, getTF_IDF(query, x)) for x in intersection])

	tf_idfDict = dict()
	result_dict = dict()
	counter = Counter()

	for word in words:
		result = dict([x for x in wordDict[word] if x[0] in intersection])
		counter.update(result)

	return [(x, counter[x]) for x in sorted(counter, key = counter.get, reverse = True)][:20]


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
	alpha = 4
	gamma = 4
	beta = 8
	tf_idf_res = dict()
	for doc in result:
		tf_idf = alpha * result[doc] + beta * key_result.get(doc, 0) + gamma * base_result.get(doc,0)
		tf_idf_res[doc] = tf_idf
	
	for doc in key_result:
		if doc not in tf_idf_res:
			tf_idf_res[doc] = beta * fancy_result.get(doc, 0)

	return [x for x in sorted(tf_idf_res, key = tf_idf_res.get, reverse = True)][:5]

def find_best_ranked(query):
	result = process_query(query)
	key_result = process_key_query(query)
        base_result = process_base_query(query)
	# print dict(result)
	# print "-----------------" * 10
	# print dict(fancy_result)
	return combine(dict(result), dict(key_result), dict(base_result) )

def loadjson(file_list):
        global url_list
        with open("../Indexer/bookkeeping.json") as jsonf:
                json_data = json.load(jsonf)
                for f in file_list:
                    url_dict={}
                    urls = json_data.get(f,"Does not exist")
                    if(urls != "Does not exist"):
                        urls = "https://" + urls
                        #print urls
                        url_list.append(urls)
                    print urls , "\n"



if __name__ == '__main__':
	
        app.run()
	# result = docList('retrieval')
	# print result
	# query = raw_input()
	# result = process_query(query)
	# print result
