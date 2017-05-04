from __future__ import division
import os
# import feedparser
import string
import json
from urlparse import urlparse
from bs4 import BeautifulSoup
from lxml.html import soupparser
import nltk, re, pprint
from bs4 import BeautifulSoup
import magic
import pprint
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
import pymongo
from pymongo import MongoClient


path = "WEBPAGES_RAW"
bad_count=0
file_handle_list = list()
curr_file_count = 0
index_dict = dict()
curr_url_count = 0
file_handle_map = dict()
N = 0
document_map = dict()
client = MongoClient('localhost', 27017)
db = client.inverted_index


def isValid(url):
	global bad_count 
	parsed = urlparse(url)
	try:
		return_val=False
		return_val = ".ics.uci.edu" in parsed.hostname \
		and not re.match(".*\.(css|js|pdf|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
		+ "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
		+ "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
		+ "|thmx|mso|arff|rtf|jar|csv"\
		+ "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
					  
		if return_val: #Only if the url is valid check for the traps
		# 1. Repeating directories
			url_str = parsed.path.lower().rstrip("/") + "/"
			if re.match("^.*?(/.+?/).*?(.*\\1){3,}.*$|^.*?/(.+?/)(.*/?\\1){3,}.*$", url_str):
				return_val = False        
			if "cgvw.ics.uci.edu" in parsed.hostname:
				return_val=True
			if not return_val:
				bad_count+=1     #For Logistics          
			return return_val
		else:
			return return_val
	except TypeError:
		print "Error"

def crawl_files():
	''' Crawl the Files domain and retrieve the information from each file.
		Classify the file type and call the Read_file
		Call the Inverted_Indexer
	'''
        global N
	limit = 70
        with open("bookkeeping.json") as json_data:        
                data=json.load(json_data)
		for pathname in os.listdir(path):
			for filename in os.listdir(path+"/"+pathname):
				if filename == ".DS_Store":
					continue

				url ="//"+ data[pathname+'/'+filename]
				if(isValid(url)):
					if pathname+'/'+filename == "39/373":
						pass
					else:
						N += 1
						process_files(path+'/'+pathname+'/'+filename)
                        if N > limit:
                                return
	print "N value: ", N
        

def process_files(file_name):
	
	''' Read the files based on the file type .
		Parse and Process the HTML files here
		Call the Key_Indexer to Index key content
		Call the Base_Indexer to Index Text content
		Tag the Key Dictionary with the Key List
		Tag the Base Dictionary with the Base List
	'''

	global document_map
	print file_name
	fileName = file_name
	fileName = fileName.strip()

	f = open(fileName)
	type_of_content = magic.from_file(fileName, mime = True)
	content = f.read()

	tokens = list()

	pos_count = 0

	# if fileName.endswith([".html", ".htm", "xhtml", "jhtml", "txt"]):
	if type_of_content.strip().startswith('text') or type_of_content.strip().startswith('application') :	#Parseable Data
		if type_of_content.strip() in ['text/html', 'text/xml', 'application/xml']: #HTML data
			try:
			   root = BeautifulSoup(content)
			except (Exception, UnicodeDecodeError) as e:
				print e
				return

			
			text = root.getText(separator=' ')
			# break into lines and remove leading and trailing space on each
			lines = (line.strip() for line in text.splitlines())
			tokens = tokenizeText(text)
			fancyTokens = tokenizeHTML(root)


	elif type_of_content.strip() in ['text/richtext', 'text/plain', 'text/csv', 'text/tab-separated-values']:
		tokens = tokenizeText(content)

	else:
		f.close()
		return



	docID = getDocID(file_name) #Returns document ID in the form 22/150 or 0/278
	document_map[docID] = sum([len(tokens[x]) for x in tokens ])
	index_tokens(tokens, docID)
	f.close()


def stem_tokens(tokens, stemmer):

	stemmed = []
	for item in tokens:
		try:
			stemmed.append(stemmer.stem(item))
		except UnicodeDecodeError:
			pass
	return stemmed
	

def getDocID(file_name):
	text = file_name
	pattern = "/"
	pos = text.rfind(pattern, 0, text.rfind(pattern))
	return text[pos + 1:]



def tokenizeText(content):
	'''Tokenize text by removing punctuations '''
	stemmer = PorterStemmer()

	processed_tokens = list()
	stems_list = list()
	tokenDict = dict()
	curr_pos = 0

	if content and content.strip():
		content = content.strip()
		lines = content.split('\n')
		lines = [line.strip().lower() for line in lines]


		for line in lines:
			#text = "".join([ch for ch in line if ch not in string.punctuation])
			#text = re.sub(r'[\W_]+', ' ', line)
                        text = re.sub('[!#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]+',' ',line) 
                	try:
				text = text.strip().encode('utf-8').decode("ascii","ignore")
			
			except UnicodeDecodeError:
				pass
                        
                        line_sub = text
			tokens = nltk.word_tokenize(text)
			stems = stem_tokens(tokens, stemmer)
			stems_list.extend(stems)
			processed_tokens.extend(tokens)

			tokenDict = findPosition(curr_pos, line_sub, set(tokens), tokenDict)
			curr_pos += len(line_sub.split(" "))
			# print "Curr_pos = ", curr_pos

			

	# print "Num of tokens: " , len(set(map(lambda x: x.lower(), processed_tokens))), len(set(map(lambda x: x.lower(), stems_list)))

	# print "\n Tokendict: \n", tokenDict
	# return (set([x.lower() for x in processed_tokens]), set([x.lower() for x in stems_list]))
	return tokenDict


def findPosition(curr_pos_val, line, tokens, tokDict):
	stemmer = PorterStemmer()
	l = line.split(" ")

	for token in tokens:
		stem = stemmer.stem(token.lower())
		stemmed_l = [stemmer.stem(x.lower()) for x in l]
		pos = [curr_pos_val + i for i, x in enumerate(stemmed_l) if x == stem]

		tokDict[stem] = tokDict.get(stem, [])
		tokDict[stem].extend(pos)

	return tokDict



def tokenizeHTML(root):
	pass


def index_tokens(tokens, doc_ID):
	'''Index Token list by adding them to the dictionary. Also, write the tokens to file when each set of 5000 files are processed.'''
	global curr_file_count
	global index_dict
	global curr_url_count 

	print "index_tokens"
	curr_url_count += 1

	if curr_url_count % 5000 == 0:
		#close curr_file by writing contents of the dict to the file and open new file
                #add values to the dictionary

		# curr_file_count += 1
		# index_name = "index_file_" + str(curr_file_count)
		print "write_file"
		print len(index_dict)
		# raw_input("Enter to continue")

		# f = open(fileName, 'w')
		# f.write(str(len(index_dict)) + '\n') #1st line of the file is the number of entries in the file
		for word in sorted(index_dict): 
			letter = getLetter(word)
			index_name = getIndexName(letter)
			my_collection = db[index_name]
			my_record = dict()
			my_record["word"] = word
			my_record["index"] = index_dict[word]
			# record_id = my_collection.insert(my_record)

			result = my_collection.find({"word": word}).limit(1)
			res = list(result)
			if res != []:
				# print "existing value"
				existing = res[0]['index']
				existing.update(my_record['index'])
				record_id = my_collection.update({
				'word' : word },
				{
					'$set': {
    				'index': existing
  					}
				})
			else:
				existing = dict()
				record_id = my_collection.insert(my_record)

			
			# print "record ID: ", record_id
		# 	json.dump([word, index_dict[word]], f)
		# 	f.write("\n")

		# f.close()

		print "\n Written \n"	
		index_dict = dict()
		
	for token in tokens:
		token = token.lower()
		index_dict[token] = index_dict.get(token, dict())
		word_chain = index_dict[token]
		word_chain[doc_ID] = word_chain.get(doc_ID, [])
		word_chain[doc_ID].extend(tokens[token])


#To dump the remaining values in index_dict into the database
def dump_indexes():
	global index_dict

	for word in sorted(index_dict): 
			letter = getLetter(word)
			index_name = getIndexName(letter)
			my_collection = db[index_name]
			my_record = dict()
			my_record["word"] = word
			my_record["index"] = index_dict[word]
			# record_id = my_collection.insert(my_record)

			result = my_collection.find({"word": word}).limit(1)
			res = list(result)
			if res != []:
			  # print "existing value", result
				existing = res[0]['index']
				existing.update(my_record['index'])
				record_id = my_collection.update({
				'word' : word },
				{
					'$set': {
    				'index': existing
  					}
				})
			else:
				existing = dict()
				record_id = my_collection.insert(my_record)

			# print "record ID in dump: ", record_id

	index_dict = dict()



def getLetter(line):
	if line[0].strip():
		letter = line[0][0]
	letter = letter.lower()
	if letter.isdigit():
			letter = "NUM"

	elif letter in "~`!@#$%^&*()_-+={}[]:>;',</?*-+":
			letter = "SYM"

	# print "letter is: ", letter
	return letter



def create_index():
	for coll in db.collection_names():
		collection = db[coll]
		collection.drop()  
        print "Crawling completed"
	crawl_files()
	pprint.pprint( index_dict )
	print "Crawling completed1"
	dump_indexes()
	# sort_indexes()

	client.close()


def getIndexName(letter):
	if letter == "NUM":
		return "index_file_NUM"

	if letter == "SYM":
		return "index_file_SYM"

	return "index_file_" + letter.upper()


def reverseDocMap(docID):
	pass

if __name__ == '__main__':
	create_index()



