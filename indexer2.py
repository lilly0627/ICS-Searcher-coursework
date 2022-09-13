from collections import defaultdict
import json
import html
from operator import invert
import os
from bs4 import BeautifulSoup
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import sys


sys.setrecursionlimit(100000) # to handle json recursion error I met

html_tag = {"title": 6, "h1": 5, "h2": 4, "h3": 3, "strong": 2, "b": 1}  #  Important text: other tages should be zero.

# GOAL after merge file: {token: {docID: doc_score = tf-idf + html_tage_score } }
class SearchEngine():
    token = []
    content = str()

    def convert(self, path):
        """"Convert the path directly to a dictionary of {token: [freq, tag_score], ...} """
        self.token = []
        self.url = str()
        with open(path, encoding='utf-8') as f:
            line = f.readline()
            d = json.loads(line)
            self.content = d["content"]  # html format content
            bs = BeautifulSoup(self.content, "lxml")
            self.token = self.tokenize(bs) # a list of perfect token

            # calculate word importance
            dic = computeWordFrequencies(self.token) # {token : count}
            new_dic = {}
            for tag in bs.find_all():
                all_text = re.split("[^a-zA-Z0-9]+", tag.get_text().lower())
                for word in all_text:
                    word = PorterStemmer().stem(word)
                    if word in dic.keys():
                        new_dic[word] = [dic[word], html_tag.get(tag.name, 0)]  # a list: [freq, tag_score]
        return new_dic


    # tokenize the text and return a stemmed token
    def tokenize(self, beautifulS):
        self.token = word_tokenize(beautifulS.get_text(strip=True))
        tokenized_list = []
        for token in self.token:
            if token not in stopwords.words('english') and re.match('[a-zA-Z0-9]', token):  # Token and removing stopwords.
                token = token.lower()
                tokenized_list.append(PorterStemmer().stem(token))  # Stemming
        return tokenized_list

def computeWordFrequencies(lis): 
    dic = defaultdict(int)
    for i in lis:
        dic[i] += 1
    return dic


"""
    Give each document a unique identifier
    
    Params:
        path - the path that stores all documents
    Return: a dictionary - 
"""
def documentIndexer(path):
    docindex = {}
    count = 1
    for dir in os.listdir(path):
        if dir == ".DS_Store":
            continue
        for fname in os.listdir(path + '/' + dir):
            a = str(path + '/' + dir + '/' + fname)
            docindex[count] = a
            count += 1
    with open('docindex_adv.json', 'w') as f:
        json.dump(docindex, f)
    num_of_doc = len(docindex)
    print(num_of_doc)
    return docindex
    
if __name__ == '__main__':
    search = SearchEngine()

    path = "/Users/Hanting Li/Desktop/desk/CS121/Assignment3/analyst/ANALYST"
    all_token = set() #token from all path
    inverted = {} # inverted index - {token1: [[url position, freq]], token2: [[url position, freq]],[url position, freq]]]....} previous one
    try:
        numdict = {} # data structure dictionary--- {id : path}
        numdict = documentIndexer(path)
        for id, file in numdict.items():
            if id % 500 == 0:
                print("finishing 500 documents")
            if id > 1 and (id-1) % 2000 == 0:
                indexerId = (id-1) / 2000
                # sort the inverted before dump to json file
                # ============ sort by freq ============
                for k,_ in inverted.items():
                    inverted[k] = dict(sorted(inverted[k].items(), key=lambda x: x[1][0], reverse=True))
                # ============ sort by word ============
                inverted = dict(sorted(inverted.items()))

                with open('INDEX/indexerfile_%d.txt' %indexerId, 'w') as f:
                    for key in inverted:
                        line = json.dumps({key: inverted[key]})
                        # line = '{"' + str(key) + '": ' + str(inverted[key]) + '}'
                        f.writelines(line)
                        f.write('\n')
                inverted = {}
                print("finishing 2000 documents")
            if id == 55393:
                indexerId = int((id-1) / 2000) + 1
                # ============ sort by freq ============
                for k,_ in inverted.items():
                    inverted[k] = dict(sorted(inverted[k].items(), key=lambda x: x[1][0], reverse=True))
                # ============ sort by word ============
                inverted = dict(sorted(inverted.items()))

                # with open('inverted/advIndexer_%d.json' %indexerId, 'w') as f:
                #     json.dump(inverted, f)
                with open('INDEX/indexerfile_%d.txt' %indexerId, 'w') as f:
                    for key in inverted:
                        line = json.dumps({key: inverted[key]})
                        # line = '{"' + str(key) + '": ' + str(inverted[key]) + '}'
                        f.writelines(line)
                        f.write('\n')
                inverted = {}
                print("finishing last documents")


            freqStemToken = search.convert(file)  # the updated structure: {token1: {docid: [freq, tag_score]},...
            all_token = all_token.union(set(freqStemToken.keys()))
            for i in freqStemToken:
                if i not in inverted.keys():
                    inverted[i] = defaultdict()
                inverted[i][id] = freqStemToken[i]  # freqStemToken[i]: [freq, tag_score] ---> new structure- {token1: {docid: [freq, tag_score]}, ...}


        print(len(all_token))


    except Exception as err:
        print(err)
        raise err

    # data structure dictionary--- {number No.: path}
    #and count not in [item[0] for item in inverted[i]]



    
    
