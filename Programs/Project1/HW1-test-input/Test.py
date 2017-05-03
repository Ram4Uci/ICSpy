import string
#from lxml import html,etree
def getURL(page):
    begin = page.find("<a href=")
    if(begin ==-1):
        return None
    begin1=page.find('"',begin+1)
    if(page[begin1+1]=="B"):
        begin1=-1
    if(begin1==-1):
        begin1=page.find("'",begin+1)
        end=page.find("'",begin1+1)
    else:
        end=page.find('"',begin1+1)
    url= page[begin1+1:end]
    print url
    return url


with open("Out_Text.txt","w") as outfiles:
    with open("Raw_Data.txt","r") as reads:
        for line in reads.readlines():
            url = getURL(line)
            if(url!=None):
                outfiles.write("\n %s" % str(url))
    

