#Stem the query
from cProfile import run
from collections import defaultdict
import json
import math
import re
import string
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import time
import numpy as np


def stemQuery(texts):
    stemmedQuery = []
    token = word_tokenize(texts.strip())  # tokenize
    for token in token:
        if token not in stopwords.words('english') and re.match('[a-zA-Z0-9]', token):
            token = token.lower()
            stemmedQuery.append(PorterStemmer().stem(token))  # stem
    return stemmedQuery


def advLookUp(word, filepath, secondary_index_filepath):
    try:
        with open(filepath, 'r') as f, open(secondary_index_filepath, 'r') as fs:
            # check secondary index
            skip = 0
            line = f.readline()
            if len(word) > 1:
                secondaryIndex = json.load(fs)
                skip = secondaryIndex[word[0]].get(word[1], 0)  # default is 0

            while skip != 0:
                line = f.readline()
                skip -= 1
            
            while line:
                content = json.loads(line)
                key = list(content.keys())[0]
                if word == key:
                    return content[key]
                line = f.readline()
            return {}

    except Exception as err:
        print(err)
        raise err


def runSearch(query, urlIndexer): 
    num_of_total_docs = 55393
    searchResult = []
    intersection = {}
    matrix = defaultdict(lambda: defaultdict(float))
    firstToken = True
    stemmed_tokens = stemQuery(query)
    for word in stemmed_tokens:
        print(word)
        # 0 for query (query as a document)
        matrix[0][word] += 1

        """
            optimize the efficiency and effectiveness
            1. only return the first 100 docs or smaller
            2. cosine similarity
        """
        indexList = advLookUp(word, 'ROOT/indexfile_%s.txt' %word[0], 'ROOT/secondaryIndex.txt')
        if firstToken:
            intersection = indexList
            firstToken = False
        else:
            for key, val in indexList.items(): # key is the docId; val is the doc score
                if key in intersection:
                    intersection[key] += val
                else:
                    intersection[key] = val

        for key, val in indexList.items():
            matrix[key][word] += val # key is the docId; val is the doc score

    for term, freq in matrix[0].items():
        # change to tf-idf score
        matrix[0][term] = (1+np.log(freq)) * np.log(num_of_total_docs)

    # cosine similarity
    for docId in matrix:
        sq = 0
        for _, score in matrix[docId].items():
            sq += score**2
            # print(score)
        for term, score in matrix[docId].items():
            matrix[docId][term] = round(float(score)/float(math.sqrt(sq)), 3)
            # print("scores is:", float(score))
            # print(round(float(math.sqrt(sq)), 3))
    
    matrixScore = {}
    for docId in matrix:
        if docId == 0:
            continue
        cos_similarity = 0
        for term, score in matrix[docId].items():
            cos_similarity += score * matrix[0][term]
        matrixScore[docId] = cos_similarity

    matrixScore = dict(sorted(matrixScore.items(), key = lambda x: x[1], reverse = True))
    # print(matrixScore)
    count = 0
    print("Top 10 Results:")
    for docId in matrixScore:  # top 10 results
        if count == 10:
            break
        searchResult.append(urlIndexer[str(docId)])
        print(urlIndexer[str(docId)])
        print(matrixScore[docId])
        count += 1
    print("total results: ", len(matrixScore))
    return searchResult


try:
    with open("url_index_adv.json", encoding='utf-8') as f:
        urlIndexer = json.loads(f.readline().strip())
except Exception as err:
    raise err    

           
if __name__ == '__main__':
    try:
        while True:      
            query = input("query: ")
            if query == 'q':
                break

            start_time = time.time()
            runSearch(query=query, urlIndexer=urlIndexer)
            end_time = time.time()

            print('time cost:', round((end_time - start_time) * 1000, 2), 'ms')
                 
    except Exception as err:
        raise err    

