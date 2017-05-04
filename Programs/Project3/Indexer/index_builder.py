from __future__ import division
import os
import string
import json
from urlparse import urlparse
from bs4 import BeautifulSoup
from lxml.html import soupparser
import nltk, re, pprint
from nltk.corpus import stopwords
import magic
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer

path = "WEBPAGES_RAW"
bad_count=0
key_dict={}
file_handle_list = list()
curr_file_count = 0
doc_dict=dict()
index_dict = dict()
file_count=0
curr_url_count = 0
token_count=0
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
    global bad_count
    with open("bookkeeping.json") as json_data:        
        data=json.load(json_data)
        for pathname in os.listdir(path):
            for filename in os.listdir(path+"/"+pathname):
                url ="//"+ data[pathname+'/'+filename]
                if(isValid(url)):
                    process_files(path+'/'+pathname+'/'+filename)
               
def process_files(file_name):
    
    ''' Read the files based on the file type .
        Parse and Process the HTML files here
        Call the Key_Indexer to Index key content
        Call the Base_Indexer to Index Text content
        Tag the Key Dictionary with the Key List
        Tag the Base Dictionary with the Base List
    '''
    
    #print file_name
    global bad_count
    global file_count
    fileName = file_name
    fileName = fileName.strip()

    f = open(fileName)
    type_of_content = magic.from_file(fileName, mime = True)
    content = f.read()

    tokens = list()

    if type_of_content.strip().startswith('text') or type_of_content.strip().startswith('application') :	#Parseable Data
    	if type_of_content.strip() in ['text/html', 'text/xml', 'application/xml']: #HTML data
            try:
        	   root = BeautifulSoup(content)
            except (Exception, UnicodeDecodeError) as e:
                print e
                return

           # for script in root(["script", "style"]):
           #     script.extract()    #extract these unnecessary tags
            docID = getDocID(file_name)
            tokenizeHTML(root,docID)
'''
            text = root.get_text()  # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())    # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))  # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            tokens = tokenizeText(text,file_name)
            fancyTokens = tokenizeHTML(root)
            file_count +=1


    elif type_of_content.strip() in ['text/richtext', 'text/plain', 'text/csv', 'text/tab-separated-values']:
        file_count +=1
        tokens = tokenizeText(content)

    else:
        bad_count+=1
        f.close()
        return

     #Returns document ID in the form 22/150 or 0/278
    print docID
    index_tokens(tokens, docID)
    f.close()

'''
def stem_tokens(tokens):
    stemmer = PorterStemmer()
    stemmed = []
    stop_words = set(stopwords.words('english'))
    filtered = [w for w in tokens if not w in stop_words]
    fil=len(set(tokens))-len(set(filtered))
    for item in filtered:
        try:
            stemmed.append(stemmer.stem(item))
        except UnicodeDecodeError:
            pass
    return stemmed,fil
    

def getDocID(file_name):
	text = file_name
	pattern = "/"
	pos = text.rfind(pattern, 0, text.rfind(pattern))
	return text[pos + 1:]



def tokenizeText(content,file_name):
	'''Tokenize text by removing punctuations '''
	
        with open ("tokens.txt","a") as f:
            processed_tokens = list()
            token_cnt=0
            stem_diffcnt=0
            stop_cnt=0
            if content and content.strip():
                    content = content.strip()
                    lines = content.split('\n')
                    lines = [line.strip().lower() for line in lines]
                    for line in lines:
                        text = "".join([ch for ch in line if ch not in string.punctuation])
                        #text = re.sub(r'\W+', ' ', text)
                        text=text.strip().encode('utf-8').decode("ascii","ignore")
                        tokens = nltk.word_tokenize(text)
                        token_cnt+=len(tokens)
                        stems,fil = stem_tokens(tokens)
                        stop_cnt +=fil
                        stem_diffcnt += len(set(tokens)) - fil - len(set(stems)) 
                        processed_tokens.extend(stems)
            f.write(" File Name = " + getDocID(file_name) + "\tNo. of tokens = " + str(token_cnt) + "\tNo of Stopwords =" + str(stop_cnt) + "\t No of Stemmed words " + str(stem_diffcnt) + "\n")
            f.write("-------------------------------------------------------------------------------------------------------------------\n")

	return processed_tokens


def tokenizeHTML(root,doc_ID):
        key_list=[]
        lists=[]
        global key_dict
	for header in root.findAll('h1') or root.findAll('h2') or root.findAll('h3') or root.findAll('h4') or root.findAll('h5') or root.findAll('h6'):
            key_list.append(header.get_text().replace('\r','').replace('\n','').encode('utf-8').decode("ascii","ignore"))
        for word in key_list:
            lines = word.split('\n')
            lines = [line.strip().lower() for line in lines]
            for line in lines:
                text = "".join([ch for ch in line if ch not in string.punctuation])
                text = text.strip().encode('utf-8').decode("ascii","ignore")
                tokens = nltk.word_tokenize(text)
                stems,fil = stem_tokens(tokens)
                lists.extend(stems)
        for key in lists:
            newdict={}
            doc_dicts=key_dict.get(key,newdict)
            doc_dicts[doc_ID]=doc_dicts.get(doc_ID,0)+1
            key_dict[key]= doc_dicts
        print doc_ID
        

            
     
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
    
def Inverted_Indexer(Key_List,Base_List):
    
    '''
    Form the Inverted Index for the Key_List and the Base_List
    '''
def Statistics():

    '''
    For Analytics
    '''


def create_Index():

    #create_letter_index()
    crawl_files()
    #ret_val = mergeIndexes()
    shutdown()
    #return ret_val

'''

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


'''

def index_tokens(tokens, doc_ID):
    '''Index Token list by adding them to the dictionary. Also, write the tokens to file when each set of 5000 files are processed.'''
    global curr_file_count
    global index_dict
    global curr_url_count 
    for token in tokens:
        newdict={}
        doc_dicts=index_dict.get(token,newdict)
        doc_dicts[doc_ID]=doc_dicts.get(doc_ID,0)+1
        index_dict[token]= doc_dicts
    #print len(index_dict)
        
   
'''
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
    #open_letter_index()
    curr_file_count=7
    external_index_handles = list()
    for i in range(1, curr_file_count + 1):
        fileName = "index_file_" + str(i)
        f = open(fileName, 'r')
        external_index_handles.append(f)

	#Merge all the sorted index files into the alphabetical inverted index form
	for handle in external_index_handles:
            for line in handle:
                start_letter = getLetter(line)
                #print start_letter
                #raw_input("Start Letter")
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

    #print "letter is: ", letter
    return letter


def sort_letter_indexes():
    global file_handle_map
    global token_count
    print "\n\nin sort letter indexes\n\n"
	
    read_map = read_letter_index()

    for letter in read_map:
        handle = read_map[letter]
        # print handle
        #raw_input("Letter Handle")
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

        fileName = "index_" + letter.strip().upper()
        f = open(fileName, "w")
        raw_input(fileName)
        for word in sorted(wordDict):
            token_count+=1
            json.dump([word, wordDict[word]], f)
            
            f.write("\n")
        f.close()
'''
def shutdown():
    with open("Analytics.txt","a") as Analytics:
        Analytics.write(" ------------------------------------------ Analytics File ----------------------------------------------\n")
        Analytics.write("Total number of Files Indexed  :  " + str(file_count)+ "\n")
        Analytics.write("Total number of Files Ignored  :  " + str(bad_count) + "\n")
        Analytics.write("Total number of Tokens Indexed :  " + str(len(index_dict)) + "\n")
    print "Analytics Done "
    '''
    with open("Dictionary.json","w") as dictf:
        for word in sorted(index_dict):
            json.dumps([word,index_dict[word]],dictf)
    '''
    global key_dict
    #pprint.pprint(key_dict)
    with open("heads.txt","w") as heads:
                for word in sorted(key_dict):
                    json.dump([word,key_dict[word]],heads)
                    heads.write('\n')
if __name__ == '__main__':
	create_Index()









	





	
