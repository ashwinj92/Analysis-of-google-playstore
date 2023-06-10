import sys
sys.path.append(r'C:\Users\ashwi\Documents\Playstorecrawler')
import re
from utils.apps import PlayApps
from collections import deque
from threading import Thread
from time import sleep
from utils.console import Console

#Replace list
def listToString(list_n):
    return str(list_n.replace('[','').replace(']','')

#Tuples of Latin characters to replace in text. 
LATIN_1_CHARS = (
    ('â\x80\x99', "'"),
    ('\xc3\xa9', 'e'),
    ('\xe2\x80\x90', '-'),
    ('\xe2\x80\x91', '-'),
    ('\xe2\x80\x92', '-'),
    ('\xe2\x80\x93', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x98', "'"),
    ('\xe2\x80\x9b', "'"),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9d', '"'),
    ('\xe2\x80\x9e', '"'),
    ('\xe2\x80\x9f', '"'),
    ('\xe2\x80\xa6', '...'),
    ('\xe2\x80\xb2', "'"),
    ('\xe2\x80\xb3', "'"),
    ('\xe2\x80\xb4', "'"),
    ('\xe2\x80\xb5', "'"),
    ('\xe2\x80\xb6', "'"),
    ('\xe2\x80\xb7', "'"),
    ('\xe2\x81\xba', "+"),
    ('\xe2\x81\xbb', "-"),
    ('\xe2\x81\xbc', "="),
    ('\xe2\x81\xbd', "("),
    ('\xe2\x81\xbe', ")")
)


def clean_latin1(data):
    try:
        return data.encode('utf-8')
    except UnicodeDecodeError:
        data = data.decode('iso-8859-1')
        for _hex, _char in LATIN_1_CHARS:
            data = data.replace(_hex, _char)
        return data.encode('utf8')


my_dict = {}
with open("uniqueNodes.txt", 'r') as f:
    for line in f:
        items = line.split(",")
        key, values = items[1].strip(), items[0]
        my_dict[key] = values
f.close()

#for key, value in my_dict.items():
 #   print(key,value)
    
f1 = open("newEdge.txt", 'w')    
with open("EdgePairs.txt", 'r') as f2:
    for line in f2:
        items = line.split(",")
        src, dest = items[0], items[1]
        if (src in my_dict) and (dest in my_dict):
           e1 = my_dict[src]
           e2 = my_dict[dest]
           #print("Key exists")
           f1.write("%s,%s\n" %(e1,e2))           
f2.close()
f1.close()

root_app = 'com.whatsapp'
root_url = f'https://play.google.com/store/apps/details?id={root_app}'

## url read xpath
gplay = PlayApps()

feat1= open("title.txt", 'w',encoding="utf-8")    
feat2= open("app_desc.txt", 'w',encoding="utf-8")    
feat3= open("app_tag.txt", 'w',encoding="utf-8") 
feat4 = open("publisher.txt", 'w',encoding="utf-8")
feat5= open("content_class.txt", 'w',encoding="utf-8")    
feat6= open("ratings.txt", 'w',encoding="utf-8")    
feat7= open("agg_r.txt", 'w',encoding="utf-8")    
feat8= open("installs.txt", 'w',encoding="utf-8")

for key, value in my_dict.items():
    data = gplay.read_page_content(key)
    fin, app_title, appName_tag,publisher_tag,content_class,ratings,agg_r,installs = gplay.read_app_desc(root_app, data)
    #test = gplay.read_app_title(root_app, data)
    print("\n")
    #print(test)
    fin = re.sub('[-><!,*)@#%(&$_?.^]', '', fin)
    #ratings = re.sub('[\+]', '', ratings)
    #installs = re.sub('[\+]', '', installs)
    fin = re.sub('[^^(éèêùçà)\x20-\x7E]', '', fin)
    #finlin = str(value)+ '~|~' +listToString(app_title)+'~|~' + str(fin) + '~|~' +str(appName_tag)+'~|~'+str(publisher_tag)+"~|~"+listToString(content_class)+"~|~"+ listToString(ratings)+"~|~"+listToString(agg_r) +"~|~"+str(installs) +"\n"
    fe2 = str(value)+ "," + listToString(app_title)+"\n"
    fe3 = str(value)+ "," + str(appName_tag)+"\n"
    fe4 = str(value)+ "," + str(publisher_tag)+"\n"
    fe5 = str(value)+ "," +listToString(content_class)+"\n"
    fe6 = str(value)+ "|" +listToString(ratings)+"\n"
    fe7 = str(value)+ "," +listToString(agg_r)+"\n"
    fe8 = str(value)+ "|" +listToString(installs)+"\n"
    print(fe2)
    feat1.write(str(fe2))
    feat2.write(str(str(value)+ "," + str(fin)+"\n"))
    feat3.write(str(fe3))
    feat4.write(str(fe4))
    feat5.write(str(fe5))
    feat6.write(str(fe6))
    feat7.write(str(fe7))
    feat8.write(str(fe8))    
    #print(finlin)
    #print(str(app_title),fin,str(appName_tag), str(publisher_tag), str(content_class), str(ratings),str(installs))
feat1.close()
feat2.close()
feat3.close()
feat4.close()
feat5.close()
feat6.close()
feat7.close()
feat8.close()



