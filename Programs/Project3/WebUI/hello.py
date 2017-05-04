from flask import Flask, render_template,redirect,request
import json
import urllib2
from bs4 import BeautifulSoup
app = Flask(__name__)
query=""
@app.route('/query', methods = ['POST'])
def signup():
    global query
    global url_list
    global file_list
    url_list = []
    query= request.form['query']
    file_list = mapquery(query)
    loadjson ()
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
file_list1=['19/404', '20/58', '10/183', '17/330', '10/316']
file_list2=['13/59', '13/474', '12/91', '25/119', '12/454']
file_list3=['18/406', '17/452','24/301', '13/223', '19/80']
file_list4=['20/131', '17/104','24/290', '2/96', '16/412']
file_list5=['23/282', '22/134', '13/464', '16/228', '17/142']
file_list6=['20/397', '22/381', '13/428', '17/150', '17/477']
file_list7=['20/58', '19/404', '10/308', '22/51', '13/339']
file_list8=['16/141', '13/443', '10/406', '17/452', '15/162']
file_list9=['16/412', '20/69', '16/107', '13/59', '26/286']
file_list10=['10/239','19/21', '20/58', '12/285', '20/131']
file_list= []
def mapquery(query):
    print query
    return{
        'mondengo' : file_list1,
        'machine learning' : file_list2,
        'Software Engineering' : file_list3,
        'Security' : file_list4,
        'Student affairs' : file_list5,
        'graduate courses' : file_list6,
        'Crista Lopes' : file_list7,
        'REST' : file_list8,
        'Computer Games' : file_list9,
        'Information Retrieval': file_list10,}[query]
        
        
            
url_list = []
def loadjson():
    global file_list
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

if __name__ == "__main__":
  
    app.run()
