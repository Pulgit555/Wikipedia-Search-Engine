import os
import sys
import xml.sax
import re
import time
import shutil
import json
# import nltk
# nltk.download('wordnet')
# from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# from nltk.stem import SnowballStemmer
import Stemmer


wiki_dump = sys.argv[1]
# p = (os.listdir(wiki_dump))
# print(p)
# number of pages in dump
inverted_folder = (sys.argv[2])
# print(inverted_folder)
if os.path.isdir(inverted_folder):
    shutil.rmtree(inverted_folder)

os.mkdir(inverted_folder)
total_pages = 0
# number of files used in storing indexes
total_files = 1
# path_to_index = sys.argv[2]
cou = 0

# dict structure will be same as below and string will map to vector of vectors.
# dict = {"string": [[title],[infobox],[category],[link],[references],[body]]}
my_dict = {}

# mapping of original doc_id and id given by me
id_dict = {}

# for total tokens
token_dict = {}

## handler to extend custom content handler
class ContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        # current tag
        self.tag = ""
        self.title = ""
        self.text = ""
        self.doc_id = ""
        # flag to store only the first id of document
        self.id_fl = 0

    def startElement(self, name, attrs):
        self.tag = name
    
    def endElement(self, endtag):
        global my_dict
        global id_dict
        if endtag == "id":
            self.id_fl = 1
        elif endtag == "page":
            add_to_words(self.title, self.text, self.doc_id)
            self.title = ""
            self.text = ""
            self.doc_id = ""
            self.id_fl = 0
        elif endtag == "mediawiki":
            add_to_id_file(id_dict)
            id_dict = {}
            add_to_file(my_dict)
            my_dict = {}
            merge_index_files()
        self.tag = ""

    def characters(self, content):
        if self.tag == "title":
            # if content == '\n':
            #     self.title += " "
            # else:
            self.title += content
        elif self.tag == "text":
            # if content == '\n':
            #     self.text += " "
            # else:
            self.text += content
        elif self.tag == "id" and self.id_fl == 0:
            self.doc_id += content 

def add_to_words(Title, text, docid):
    global total_files
    global my_dict
    global total_pages
    global id_dict

    title = process_string(Title)
    infobox, info_st, info_en = find_infobox(text)
    category, category_st = find_category(text)
    links, link_st = find_links(text, category_st)
    references, references_st = find_references(text, category_st, link_st)
    body = find_body(text, info_st, info_en, category_st, link_st, references_st)
    # print(category_st)
    # print(info_st)
    # print(info_en)
    # print(references_st)
    # print(link_st)
    # print("Title: " + title)
    # print("infobox: " + infobox)
    # print("category: "+ category)
    # print("ext links: " + links)
    # print("references: " + references)
    # print("body: "+ body)

    token_title = removing_sw_n_stem(title)
    token_infobox = removing_sw_n_stem(infobox)
    token_category = removing_sw_n_stem(category)
    token_link = removing_sw_n_stem(links)
    token_reference = removing_sw_n_stem(references)
    token_body = removing_sw_n_stem(body)
    l = 0
    if total_files%55000 == 0:
        add_to_id_file(id_dict)
        id_dict = {}
        add_to_file(my_dict)
        my_dict = {}

    for token in token_title:
        if not token in my_dict:
            my_dict[token] = [[], [], [], [], [], []]
        l = len(my_dict[token][0])
        if (l > 0 and my_dict[token][0][l-1] != total_files) or l == 0:
            my_dict[token][0].append(total_files)
    
    for token in token_infobox:
        if not token in my_dict:
            my_dict[token] = [[], [], [], [], [], []]
        l = len(my_dict[token][1])
        if (l > 0 and my_dict[token][1][l-1] != total_files) or l == 0:
            my_dict[token][1].append(total_files)

    for token in token_category:
        if not token in my_dict:
            my_dict[token] = [[], [], [], [], [], []]
        l = len(my_dict[token][2])
        if (l > 0 and my_dict[token][2][l-1] != total_files) or l == 0:
            my_dict[token][2].append(total_files)
    
    for token in token_link:
        if not token in my_dict:
            my_dict[token] = [[], [], [], [], [], []]
        l = len(my_dict[token][3])
        if (l > 0 and my_dict[token][3][l-1] != total_files) or l == 0:
            my_dict[token][3].append(total_files)

    for token in token_reference:
        if not token in my_dict:
            my_dict[token] = [[], [], [], [], [], []]
        l = len(my_dict[token][4])
        if (l > 0 and my_dict[token][4][l-1] != total_files) or l == 0:
            my_dict[token][4].append(total_files)
    
    for token in token_body:
        if not token in my_dict:
            my_dict[token] = [[], [], [], [], [], []]
        l = len(my_dict[token][5])
        if (l > 0 and my_dict[token][5][l-1] != total_files) or l == 0:
            my_dict[token][5].append(total_files)
    # temp_dict = {}
    # for token in token_title:
    #     if not token in my_dict:
    #         my_dict[token] = ["", "", "", "", "", ""]
    #     l = len(my_dict[token][0])
    #     if (l > 0 and not token in temp_dict) or l == 0:
    #         temp_dict[token] = 1
    #         my_dict[token][0] += str(total_files) + " "
    
    # temp_dict = {}
    # for token in token_infobox:
    #     if not token in my_dict:
    #         my_dict[token] = ["", "", "", "", "", ""]
    #     l = len(my_dict[token][1])
    #     if (l > 0 and not token in temp_dict) or l == 0:
    #         temp_dict[token] = 1
    #         my_dict[token][1] += str(total_files) + " "

    # temp_dict = {}
    # for token in token_category:
    #     if not token in my_dict:
    #         my_dict[token] = ["", "", "", "", "", ""]
    #     l = len(my_dict[token][2])
    #     if (l > 0 and not token in temp_dict) or l == 0:
    #         my_dict[token][2] += str(total_files) + " "
    #         temp_dict[token] = 1
    
    # temp_dict = {}
    # for token in token_link:
    #     if not token in my_dict:
    #         my_dict[token] = ["", "", "", "", "", ""]
    #     l = len(my_dict[token][3])
    #     if (l > 0 and not token in temp_dict) or l == 0:
    #         my_dict[token][3] += str(total_files) + " "
    #         temp_dict[token] = 1

    # temp_dict = {}
    # for token in token_reference:
    #     if not token in my_dict:
    #         my_dict[token] = ["", "", "", "", "", ""]
    #     l = len(my_dict[token][4])
    #     if (l > 0 and not token in temp_dict) or l == 0:
    #         my_dict[token][4] += str(total_files) + " "
    #         temp_dict[token] = 1
    
    # temp_dict = {}
    # for token in token_body:
    #     if not token in my_dict:
    #         my_dict[token] = ["", "", "", "", "", ""]
    #     l = len(my_dict[token][5])
    #     if (l > 0 and not token in temp_dict) or l == 0:
    #         my_dict[token][5] += str(total_files) + " "
    #         temp_dict[token] = 1

    id_dict[total_files] = docid
    total_files = total_files + 1

# adding dict to file
# format - string:T1 T2&i1 i2&c1&l1&r1&b1\n
def add_to_file(mydict):
    global total_pages
    global cou
    index = ""
    listt = sorted(mydict.keys())
    for key in listt:
        # index = ""
        cou += 1
        index += key + ":"
        # if len(my_dict[key][0]) > 0:
        #     index += my_dict[key][0]
        for i in my_dict[key][0]:
            index += str(i) + " "
        index += "&"
        # if len(my_dict[key][1]) > 0:
        #     index += my_dict[key][1]
        for i in my_dict[key][1]:
            index += str(i) + " "
        index += "&"
        # if len(my_dict[key][2]) > 0:
        #     index += my_dict[key][2]
        for i in my_dict[key][2]:
            index += str(i) + " "
        index += "&"
        # if len(my_dict[key][3]) > 0:
        #     index += my_dict[key][3]
        for i in my_dict[key][3]:
            index += str(i) + " "
        index += "&"
        # if len(my_dict[key][4]) > 0:
        #     index += my_dict[key][4]
        for i in my_dict[key][4]:
            index += str(i) + " "
        index += "&"
        # if len(my_dict[key][5]) > 0:
        #     index += my_dict[key][5]
        for i in my_dict[key][5]:
            index += str(i) + " "
        index += '\n'
    with open('ind'+str(total_pages) + '.txt','w') as file:
        file.write(index)
        # file.write(json.dumps(dict(sorted(mydict.items()))))
    total_pages = total_pages + 1 

# add id_dict to idfile
def add_to_id_file(id_dict):
    global total_pages
    with open(os.path.join(inverted_folder , 'ids.txt'), 'a') as file:
        if total_pages == 0:
            file.write("[")
        else:
            file.write(",")
        file.write(json.dumps(id_dict))

def process_string(before_process):
    # unwanted = "[][}{!@#$;:,!*%)(&^~=|\/?><.+-]"
    # before_process = before_process.strip().encode("ascii",errors="ignore").decode()
    # mid_process = re.sub('&lt;|&gt;|&amp;|&quot;'," ",before_process.strip().encode("ascii",errors="ignore").decode())
    after_process = re.sub('[^a-zA-Z0-9]', " ",re.sub('&lt;|&gt;|&amp;|&quot;'," ",before_process))
    after_process = after_process.replace('  ',' ').lstrip().rstrip()
    return after_process.lower()

# finding infobox
def find_infobox(text):
    l = len(text)
    info = ""
    info_st = -1
    info_en = -1
    for match in re.finditer("{{ *[iI]nfobox",text):
        start_index = match.start()
        if info_st == -1:
            info_st = start_index
        s_ind = start_index + 8
        for i in range(s_ind, l-1):
            if text[i] == 'x':
                s_ind = i+1
                break
        e_ind = -1
        clos_brac = 0
        for i in range(s_ind, l-1):
            if text[i] == '{':
                clos_brac += 1
            elif text[i] == '}':
                if clos_brac == 0 and text[i+1] == '}':
                    e_ind = i
                    break
                clos_brac -= 1
        if e_ind != -1:
            info_en = e_ind
            info += process_string(text[s_ind:e_ind]) + " "
            # info += " "
    return info, info_st, info_en

# finding category
def find_category(text):
    l = len(text)
    category = ""
    cat_st = -1
    for match in re.finditer("\[\[ *[Cc]ategory",text):
        start_index = match.start()
        s_ind = start_index + 9
        if cat_st == -1:
            cat_st = start_index
        for i in range(s_ind, l-1):
            if text[i] == ':':
                s_ind = i+1
                break
        e_ind = -1
        clos_brac = 0
        for i in range(s_ind, l-1):
            if text[i] == '[':
                clos_brac += 1
            elif text[i] == ']':
                if clos_brac == 0 and text[i+1] == ']':
                    e_ind = i
                    break
                clos_brac -= 1
        if e_ind != -1:
            category += process_string(text[s_ind:e_ind]) + " "
            # category += " "
    return category, cat_st

# finding external links
def find_links(text, category_st):
    l = len(text)
    if category_st != -1:
        l = category_st
    links = ""
    link_st = -1
    for match in re.finditer("\=\= *[Ee]xternal *links *\=\=", text):
        start_index = match.start() 
        link_st = start_index
        start_index += 15
        p = -1
        for i in range(start_index, l):
            if (text[i] == ' ' or text[i] == '\n') and p == 0:
                start_index = i
                break
            elif text[i] == '=':
                p = 0
        links = process_string(text[start_index:l])
        break
    return links, link_st

# finding references
def find_references(text, category_st, link_st):
    l = len(text)
    if link_st != -1:
        l=link_st
    if category_st != -1 and category_st < l:
        l=category_st
    references_st = -1
    references = ""
    for match in re.finditer("\=\=*\s*[Rr]eferences\s*\=*\=", text):
        start_index = match.start()
        if references_st == -1:
            references_st = start_index
        start_index += 12
        p = -1
        for i in range(start_index, l):
            if text[i] != '=' and p == 0:
                start_index = i
                break
            elif text[i] == '=':
                p = 0
        references = process_string(text[start_index:l])
        break
    return references, references_st

# finding body
def find_body(text, info_st, info_en, category_st, link_st, references_st):
    l = len(text)
    if category_st != -1 and category_st < l:
        l = category_st
    if link_st != -1 and link_st < l:
        l = link_st
    if references_st != -1 and references_st < l:
        l= references_st
    body = ""
    if info_st != -1:
        body = process_string(text[0:info_st]) + " " + process_string(text[info_en+1:l])
    else:
        body = process_string(text[0:l])
    return body

# removing stop words and stemming
# dont use PorterStemmer it takes too much time.- 320
# dont use SnowballStemmer it takes too much time.- 273
# lemmatizer - 188, 203
# pystemmer - 177
def removing_sw_n_stem(words_string):
    global cou
    global token_dict
    tokenised_words = re.split('\s', words_string)
    stop_words = set(stopwords.words('english'))
    # stemmer = SnowballStemmer('english')
    stemmer = Stemmer.Stemmer('english')
    # lemmatizer = WordNetLemmatizer()
    words_exc_sw = []
    for  word in tokenised_words:
        l = len(word)
        if word != " " and l > 0:
            token_dict[word] = 1
            if not word in stop_words:
                word = stemmer.stemWord(word)
                # word = lemmatizer.lemmatize(word)
                words_exc_sw.append(word)
    return words_exc_sw

def merge_index_files():
    global total_pages
    if total_pages == 1:
        os.rename('ind0.txt',os.path.join(inverted_folder, 'final_index.txt'))
    else:
        files = []
        for i in range(total_pages):
            files.append(open("ind" + str(i) + ".txt", "r"))
        tokens = {}
        for i in range(total_pages):
            tokens[i] = files[i].readline()
            if tokens[i] != '':
                tokens[i] = tokens[i][:-1]
        count = 1
        index = ""
        while(1):
            words = {}
            first_word = " "
            for i in range(total_pages):
                if tokens[i] != '':
                    words[i] = tokens[i].split(":")
                    if first_word == " ":
                        first_word = words[i][0]
                    elif first_word > words[i][0]:
                        first_word = words[i][0]
            if first_word == " ":
                break
            desired_list = []
            for i in range(total_pages):
                if tokens[i]!= '':
                    if words[i][0] == first_word:
                        desired_list.append(words[i][1].split("&"))
                        tokens[i] = files[i].readline()
            index += first_word +":"
            for i in range(6):
                for j in range(len(desired_list)):
                    k = desired_list[j][i].split(" ")
                    for l in k:
                        if l != '' and l != '\n' and l != ' ':
                            index += l + " "
                if i!=5:
                    index += "&"
            index += "\n"
            if count%20000 == 0:
                with open(os.path.join(inverted_folder , 'final_index.txt'),'a') as file:
                    file.write(index)
                index = ""
            count += 1
        for i in range(total_pages):
            os.remove("ind" + str(i) + ".txt")

if __name__ == '__main__':
    # creating xml reader
    parser = xml.sax.make_parser()
    # turning off namespaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # overriding default content handler
    handler = ContentHandler()
    parser.setContentHandler(handler)
    begin = time.time()
    parser.parse(wiki_dump)
    total_files -= 1
    print(total_files)
    end = time.time()
    print(end-begin)
    # print("Finalised Tokens:" + str(cou))
    # print("Total Tokens:" + str(len(token_dict)))
    with open(os.path.join(inverted_folder , 'ids.txt'), 'a') as file:
        file.write("]")
    
    with open(sys.argv[3], "w") as file:
        file.write(str(len(token_dict)))
        file.write("\n")
        file.write(str(cou))
    # print(my_dict)