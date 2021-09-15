import os
import sys
import re
import time
import json
from nltk.corpus import stopwords
import Stemmer
from nltk.corpus.reader import lin
stop_words = set(stopwords.words('english'))
stemmer = Stemmer.Stemmer('english')

query = sys.argv[2]
tokens = query.split(" ")
for i in range(len(tokens)):
    one_point = tokens[i].split(":")
    if len(one_point) > 1:
        tokens[i] = one_point[1]
    else:
        tokens[i] = one_point[0]

output_dict = {}

index_dict = {}
inverted_folder = sys.argv[1]
file = open(os.path.join(inverted_folder,'final_index.txt'),"r")
line = ""
while 1:
    line = file.readline()
    # print(line)
    if line == "":
        break
    r = line.split(":")
    index_dict[r[0]] = r[1]

for i in tokens:
    if i not in output_dict:
        output_dict[i] = {
            "title": [],
            "body": [],
            "infobox": [],
            "categories": [],
            "references": [],
            "links": []
            }
        stemmed_word = i.lower()
        if stemmed_word not in stop_words:
            stemmed_word = stemmer.stemWord(stemmed_word)
            if stemmed_word in index_dict.keys():
                # print(stemmed_word)
                fields = index_dict[stemmed_word].split("&")
                titles = fields[0].split(" ")
                infobox = fields[1].split(" ")
                category = fields[2].split(" ")
                links = fields[3].split(" ")
                references = fields[4].split(" ")
                body = fields[5].split(" ")
                for id in titles:
                    if id != '' and id != '\n':
                        output_dict[i]['title'].append(id)
                for id in infobox:
                    if id != '' and id != '\n':
                        output_dict[i]['infobox'].append(id)  
                for id in category:
                    if id != '' and id != '\n':
                        output_dict[i]['categories'].append(id)
                for id in links:
                    if id != '' and id != '\n':
                        output_dict[i]['links'].append(id)
                for id in references:
                    if id != '' and id != '\n':
                        output_dict[i]['references'].append(id)
                for id in body:
                    if id != '' and id != '\n':
                        output_dict[i]['body'].append(id) 
print(output_dict)