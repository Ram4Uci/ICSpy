from lxml import html,etree
from urlparse import urlparse, parse_qs, urljoin
import string
import json
import magic
from lxml.html import soupparser
from bs4 import BeautifulSoup
from lxml.html import soupparser
import os,re
urldict=dict()
path = "../WEBPAGES_RAW"
PR=dict()
urlist=list()
global url_count
def crawl_files():
    url_count=0
    with open("../bookkeeping.json") as json_data:
        data=json.load(json_data)
        for pathname in os.listdir(path):
            if pathname == ".DS_Store":
                continue

            for filename in os.listdir(path+"/"+pathname):
                if filename == ".DS_Store":
					continue

                url ="https://"+ data[pathname+'/'+filename]

                if(isValid(url)):
                    if pathname+'/'+filename == "39/373":
                        pass

                    else:
                        fileName = path + '/' + pathname + '/' + filename
                        #print fileName
                        f = open(fileName.strip())
                        type_of_content = magic.from_file(fileName, mime = True)
                        if type_of_content.strip().startswith('text') or type_of_content.strip().startswith('application') :	#Parseable Data
                            if type_of_content.strip() in ['text/html', 'text/xml', 'application/xml']: #HTML data
                                content = f.read()
                                url_count+=1
                                if url_count>30000:
                                    return

                                print url_count
                                try:
                                    root = BeautifulSoup(content,"lxml")

                                except (Exception, UnicodeDecodeError) as e:
                                    return

                                links = [link['href'] for link in root.findAll('a',href=True)]
                                absoluteLinks = convertToAbsolute(url, links)
                                results = set(absoluteLinks)
                                inverted(url,results)
                                urlist.append(url.strip().rstrip('/'))
   
                                                    
                                                
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
			#if not return_val:
				#bad_count+=1     #For Logistics          
			return return_val
		else:
			return return_val
	except TypeError:
                pass
                #print url
                #raw_input()
		#print "Error1"

def convertToAbsolute(url, links):
    '''
        <scheme>://<username>:<password>@<host>:<port>/<path>;<parameters>?<query>#<fragment>
        Not handled mailto and fragments(#)
        Also, javascript needs to be handled
    '''

    global subdomains_visited
    parsed_url = urlparse(url)
    # print "Here in convert to absolute"

    base_url = parsed_url.scheme +"://"+ parsed_url.netloc + parsed_url.path
    absolutelinks = list()
    for link in links:
        link = link.strip().lower()

        if link.find('http') == 0 and isValid(link):
            #print "Absolute = " + link 
            absolutelinks.append(link)

        elif link.find('//') == 0 and isValid(link):
            #print "Second Absolute = " + link
            absolutelinks.append(link)

        elif link.find('#') == 0 or link.find("javascript") == 0 or link.find("mailto") == 0: #****
            #print "#"
            pass

        else:
            result = urljoin(base_url,link)
            if(isValid(result)):
                #print "Else = " + result
                absolutelinks.append(result)

    return absolutelinks


def is_url_absolute(url):
    '''
        <scheme>://<username>:<password>@<host>:<port>/<path>;<parameters>?<query>#<fragment>
        Not handled mailto and fragments(#)
        Also, javascript needs to be handled
    '''
    
    link = url.strip()
    is_valid_scheme = False
    relative_path_present = False

    if link.find('http') == 0:
        is_valid_scheme = True
    elif link.find('//') == 0 :
        is_valid_scheme = True
    if "/../" in link:
        relative_path_present = True
    if not relative_path_present and is_valid_scheme:
        return True
    else:
        return False

def inverted(url,links):
   
    if url.startswith("https://"):
            url = url[8:]
    elif url.startswith("http://"):
            url = url[7:]
    
    
    
    global urldict
    urldict[url] = urldict.get(url,dict())
    urldict[url]["outgoing"]=len(links)
    urldict[url]["incoming"] = urldict.get("incoming",set())
    for link in links:
        link = link.strip().rstrip('/')
        if link.startswith("https://"):
            link = link[8:]
        elif link.startswith("http://"):
            link = link[7:]
        urldict[link] = urldict.get(link,dict())
        urldict[link]["incoming"] = urldict[link].get("incoming",set())
        urldict[link]["incoming"].add(url)
        urldict[link]["outgoing"] = urldict[link].get("outgoing",0)
        

def prcalc():
    global urlist
    global PR
    print "here",len(urldict)
    #raw_input()
    for url in urldict.keys():
        PR[url]=float(1)/float(29390) #Initialization
    for i in range(0,50):
        for link in urldict.keys():
            score = 0
            incoming = urldict[link]["incoming"]
            if len(incoming) != 0:
                for inlink in incoming:
                    score+= (float(PR[inlink])/float(urldict[inlink]["outgoing"]))
                PR[link] = 0.15 + 0.85 * score
            


    
import pprint

crawl_files()
prcalc()
print len(urldict)
print "\n\n"
#for url in urlist:
#    pprint.pprint((url,urldict[url]))
#pprint.pprint([(x,urldict[x]) for x in sorted(urldict,key=urldict.get("outgoing"),reverse = True)])
#pprint.pprint(PR)
print len(PR)
with open("pr.json","w") as pr:
        json.dump(PR,pr)

with open("pr_new.json", "w") as f:
    for key in PR:
        PR[key] = PR[key] / len(PR)

    json.dump(PR, f)

    f.close()
