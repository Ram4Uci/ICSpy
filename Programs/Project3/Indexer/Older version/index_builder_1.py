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
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer

path = "WEBPAGES_RAW"
bad_count=0
file_handle_list = list()
curr_file_count = 0
index_dict = dict()
curr_url_count = 0
file_handle_map = dict()


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
    limit = 10000
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
                        process_files(path+'/'+pathname+'/'+filename)
                limit -= 1
                if limit == 0:
                    break

            if limit == 0:
                break

def process_files(file_name):
    
    ''' Read the files based on the file type .
        Parse and Process the HTML files here
        Call the Key_Indexer to Index key content
        Call the Base_Indexer to Index Text content
        Tag the Key Dictionary with the Key List
        Tag the Base Dictionary with the Base List
    '''
    print file_name
    fileName = file_name
    fileName = fileName.strip()

    f = open(fileName)
    type_of_content = magic.from_file(fileName, mime = True)
    content = f.read()

    tokens = list()

    # if fileName.endswith([".html", ".htm", "xhtml", "jhtml", "txt"]):
    if type_of_content.strip().startswith('text') or type_of_content.strip().startswith('application') :	#Parseable Data
    	if type_of_content.strip() in ['text/html', 'text/xml', 'application/xml']: #HTML data
            try:
        	   root = BeautifulSoup(content)
            except (Exception, UnicodeDecodeError) as e:
                print e
                return

            for script in root(["script", "style"]):
                script.extract()    #extract these unnecessary tags
            
            text = root.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            #print(text)
            #If no exception occured:
            tokens = tokenizeText(text)
            fancyTokens = tokenizeHTML(root)


    elif type_of_content.strip() in ['text/richtext', 'text/plain', 'text/csv', 'text/tab-separated-values']:
        tokens = tokenizeText(content)

    else:
        f.close()
        return

    docID = getDocID(file_name) #Returns document ID in the form 22/150 or 0/278
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
	if content and content.strip():
		content = content.strip()
		lines = content.split('\n')
		lines = [line.strip().lower() for line in lines]

		for line in lines:
			text = "".join([ch for ch in line if ch not in string.punctuation])
                text = re.sub(r'\W+', ' ', text)
                try:
                    text=text.strip().encode('utf-8').decode("ascii","ignore")
                except UnicodeDecodeError:
                    pass
                tokens = nltk.word_tokenize(text)
                stems = stem_tokens(tokens, stemmer)
                processed_tokens.extend(stems)

	return processed_tokens


def tokenizeHTML(root):
	pass
                



            
     
def Key_Indexer(content):
    
    '''
    Remove stopwords  with caution . If the stop words have a frequency of more than 2/5 of total word count.
    Stem the words.
    Call the Tokenizer function
    Index the content in this field as very important and given a higher priority
    Return a dictionary of Word,Frequency
    '''
    
def Base_Indexer(content):
    
    '''
    Index the general text content here
    Remove Stopwords and Stem words
    Return a dictionary of Word,Frequency
    '''
    
def Tokenizer(words):
    
    '''
    Implement the Tokenizer and tokenize the content.
    Sort the tokens as per the frequency and return the dictionary of words-frequency
    '''
    
def Inverted_Indexer(Key_List,Base_List):
    
    '''
    Form the Inverted Index for the Key_List and the Base_List
    '''
def Statistics():

    '''
    For Analytics
    '''


def create_Index():

    create_letter_index()
    crawl_files()
    ret_val = mergeIndexes()
    return ret_val



def create_letter_index():
    letters = string.ascii_uppercase
    letter_file_map = map(lambda x: "index_" + x, list(letters))

    print "create_letter_index"
    for name in letter_file_map:
	try:
            os.remove(name)
	except OSError:
            pass
        f = open(name, 'a').close()
	f = open("index_NUM", 'a').close()


def open_letter_index():
    global file_handle_list
    global file_handle_map
    print "open_index"
    letters = string.ascii_uppercase
    letter_file_map = map(lambda x: "index_" + x, list(letters))
    for name in letter_file_map:
	file_handle = open(name, 'a')
	#file_handle_list.append(file_handle)
	file_handle_map[name[-1].lower()] = file_handle
	# file_handle_list.append(open("index_NUM", 'a')) #Index File for numbers
	file_handle_map["NUM"] = open("index_NUM", 'a')
	file_handle_map["SYM"] = open("index_SYM", 'a')


def close_letter_index():
    global file_handle_list
    print "close_index"
    for handle_name in file_handle_map:
	file_handle_map[handle_name].close()


def read_letter_index():
    read_file_map = dict()
    letters = string.ascii_uppercase
    letter_file_map = map(lambda x: "index_" + x, list(letters))
    for name in letter_file_map:
    	file_handle = open(name, 'r')
	#file_handle_list.append(file_handle)
	read_file_map[name[-1].lower()] = file_handle
	# file_handle_list.append(open("index_NUM", 'a')) #Index File for numbers
    read_file_map["NUM"] = open("index_NUM", 'r')
    read_file_map["SYM"] = open("index_SYM", 'r')

    return read_file_map


def close_files(file_handles):

    for handle_name in file_handles:
	file_handle_map[handle_name].close()




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

	curr_file_count += 1
	fileName = "index_file_" + str(curr_file_count)
        print "write_file"
        print(str(len(index_dict)))
        # raw_input("Enter to continue")
	f = open(fileName, 'w')
	# f.write(str(len(index_dict)) + '\n') #1st line of the file is the number of entries in the file
	for word in sorted(index_dict): 
            json.dump([word, index_dict[word]], f)
            f.write("\n")

        f.close()
        index_dict = dict()
    for token in tokens:
	token = token.lower()
	index_dict[token] = index_dict.get(token, dict())
	word_chain = index_dict[token]
	word_chain[doc_ID] = word_chain.get(doc_ID, 0) + 1

def mergeIndexes():
    global curr_file_count
    global index_dict
    global curr_url_count
    global file_handle_map

    #First write the remaining values in the index_dict to the last file

    if curr_url_count % 5000 != 0:	#Write only if its already not written
    	curr_file_count += 1
	fileName = "index_file_" + str(curr_file_count)
	print "merge_index"
        f = open(fileName, 'w')
        # f.write(str(len(index_dict)) + '\n') #1st line of the file is the number of entries in the file
        for word in sorted(index_dict): 
            json.dump([word, index_dict[word]], f)
            f.write("\n")
        f.close()
    open_letter_index()
    external_index_handles = list()
    for i in range(1, curr_file_count + 1):
        fileName = "index_file_" + str(i)
        f = open(fileName, 'r')
        external_index_handles.append(f)

	#Merge all the sorted index files into the alphabetical inverted index form
	for handle in external_index_handles:
            for line in handle:
                start_letter = getLetter(line)
                f_handle = file_handle_map[start_letter]
                res = json.loads(line)
                json.dump(res, f_handle)
                # json.dump(line.strip(), f_handle)
                f_handle.write("\n")
    print "Completed writing"		

    close_letter_index()

    ret_val = sort_letter_indexes()	

    return ret_val	



def getLetter(json_line):
    line = json.loads(json_line)
    if line[0].strip():
    	letter = line[0][0]
	letter = letter.lower()
	if letter.isdigit():
            letter = "NUM"

	elif letter in "~`!@#$%^&*()_-+={}[]:>;',</?*-+":
            letter = "SYM"

    print "letter is: ", letter
    return letter


def sort_letter_indexes():
    global file_handle_map
    print "\n\nin sort letter indexes\n\n"
	
    read_map = read_letter_index()

    for letter in read_map:
        handle = read_map[letter]
        # print handle
        # lines = handle.readlines()
        # lines = [line.strip() for line in lines if line.strip() != ""]
        wordDict = dict()
        for line in handle:
            # print "line: ", line
            json_str = json.loads(line)
            key = json_str[0]
            value = json_str[1]
            key = key.lower()
            val_dict = wordDict.get(key, dict())
            val_dict.update(value)
            wordDict[key] = val_dict

        handle.close()

        fileName = "index_" + letter.strip()
        f = open(fileName, "w")
        for word in sorted(wordDict):
            json.dump([word, wordDict[word]], f)
            f.write("\n")
        f.close()


if __name__ == '__main__':
	create_Index()









	





	
