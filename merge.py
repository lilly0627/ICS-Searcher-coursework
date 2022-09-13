"""
    merge all index files into a large one

    assume each index file is sorted (in fact they are sorted during construction)
"""
import time
import sys
from collections import defaultdict
import os
import json
import numpy as np
sys.setrecursionlimit(100000)  # handle json recursion error


class IndexMerger():
    path = ''
    advIndex = {}
    def merge(self, file1, file2, outputFile):
        try:
            with open(file1, 'r') as f1, open(file2, 'r') as f2, open(outputFile, 'w') as f3:
                line1 = f1.readline()
                line2 = f2.readline()
                while True:
                    if not line1 or not line2:
                        break
                    c1 = json.loads(line1)
                    c2 = json.loads(line2)
                    key1 = list(c1.keys())[0]
                    key2 = list(c2.keys())[0]
                    if key1 < key2:
                        f3.writelines(line1)
                        line1 = f1.readline()
                    elif key1 > key2:
                        f3.writelines(line2)
                        line2 = f2.readline()
                    else:
                        c1[key1].update(c2[key1])
                        c1[key1] = dict(sorted(c1[key1].items(), key=lambda x: x[1], reverse=True))
                        # print(c1)
                        f3.writelines(json.dumps(c1))
                        f3.write('\n')
                        line1 = f1.readline()
                        line2 = f2.readline()
                while line1:
                    f3.writelines(line1)
                    line1 = f1.readline()
                while line2:
                    f3.writelines(line2)
                    line2 = f2.readline()

        except Exception as err:
            print(err)
            raise err

    """
        separate index files by character

        Params:
            file: input file
            char: the beginning character of tokens (separate by the character)
            outputFile: output file

        Return:
            None
            [advIndex]: a secondary index of the index, store the #line of tokens starting at aa, ab, ac ... ba, bb, ...
    """
    def separate(self, file, char, outputFile):
        try:
            self.advIndex[char] = dict() # {'a': {'a': #line(usually 1), {'b': #line}, ...}, ...}
            self.advIndex[char]['0'] = 1
            ab = '0123456789abcdefghijklmnopqrstuvwxyz'
            i = 0
            with open(file, 'r') as f, open(outputFile, 'w') as fout:
                line = f.readline()
                lineCount = 1
                reach = False
                while line:
                    content = json.loads(line)
                    key = list(content.keys())[0]
                    if key[0] == char:
                        if len(key) > 1 and key[1] > ab[i]:
                            for ch in ab:
                                if ch > ab[i] and ch <= key[1]:
                                    self.advIndex[char][ch] = lineCount
                                    # print("%s %s %s" %(ab[i], ch, key[1]))
                                    i += 1         
                            
                        reach = True
                        fout.writelines(line)
                        lineCount += 1
                    # reach the next char, stop current advIndex and break
                    if key[0] != char and reach:
                        for ch in ab:
                            if ch > ab[i]: # usually not true
                                self.advIndex[char][ch] = lineCount-1       
                        break
                    line = f.readline()
                    
        except Exception as err:
            print(err)
            raise err



def tfidf_and_tagScore(merged_file):
    """finalmergefile.txt --> merge_file_with_score, [freq, tag] --> score"""
    num_of_files = 55393  # hard code number
    newfile = open('Merge2/merge_file_with_score.txt', 'w+')  # result file
    with open(f"{merged_file}") as f:
        line = f.readline().strip()
        while line:
            result = defaultdict(dict)
            res = defaultdict(int)
            content = json.loads(line)
            token = list(content.keys())[0]
            doc_freq = len(content[token])
            for docID, freq_tag in content[token].items():
                tf = 1 + np.log(freq_tag[0])  # log
                idf = np.log(num_of_files / doc_freq)
                tf_idf = tf * idf
                res[docID] = round(tf_idf + freq_tag[1], 2)  # tf-idf + word importance score, round 2
            result[token] = res
            result = json.dumps(result)
            newfile.write(result)
            newfile.write('\n')
            # print("finish writing: "+token)

            line = f.readline().strip()

    newfile.close()


def urlIndexer(path):
    """Generate a url indexer, {doc id: url}, similar to docindex_adv"""
    urlindex = {}
    count = 1
    for dir in os.listdir(path):
        if dir == ".DS_Store":
            continue
        for fname in os.listdir(path + '/' + dir):
            a = str(path + '/' + dir + '/' + fname)
            f = open(a)
            jsonText = json.load(f)
            url = jsonText['url']
            urlindex[count] = url
            # print("finish writing: "+url)
            count += 1
    with open('url_index_adv.json', 'w') as f:  # result file
        json.dump(urlindex, f)
    print(len(urlindex))
    return urlindex


if __name__ == '__main__':
    mg = IndexMerger()
# ======================== Test Only =================================
    # mg.merge('INDEX/indexerfile_1.txt', 'INDEX/indexerfile_2.txt', 'TEST/indexfile_12.txt')
    # mg.separate('TEST/indexfile_12.txt', 'a', 'TEST/indexfile_a.txt')
    # print(mg.advIndex)

# ========================= Uncomment to Run ===================================
    totalFileNum = 28
    path = "/Users/Hanting Li/Desktop/desk/CS121/Assignment3/analyst/ANALYST"
    for i in range(int(totalFileNum/2)):
        startTime = time.time()
        mg.merge('INDEX/indexerfile_%d.txt' %(i+1), 'INDEX/indexerfile_%d.txt' %(totalFileNum-i), 'Merge2/indexfile_%d.txt' %(totalFileNum+1+i))
        endTime = time.time()
        print("merge %d cost %ds" %(i+1, endTime-startTime))
    for i in range(int(totalFileNum/4)):
        startTime = time.time()
        mg.merge('Merge2/indexfile_%d.txt' %(totalFileNum+i+1), 'Merge2/indexfile_%d.txt' %(int(totalFileNum*1.5)-i), 'Merge2/mergefile_%d.txt' %(i+1))
        endTime = time.time()
        print("next merge %d cost %ds" %(i+1, endTime-startTime))

    for i in range(3):
        startTime = time.time()
        mg.merge('Merge2/mergefile_%d.txt' %(i+1), 'Merge2/mergefile_%d.txt' %(7-i), 'Merge2/merge2file_%d.txt' %(i+1))
        endTime = time.time()
        print("next2 merge %d cost %ds" %(i+1, endTime-startTime))

    # final merge starts here
    startTime = time.time()
    mg.merge('Merge2/merge2file_1.txt', 'Merge2/merge2file_2.txt', 'Merge2/merge3file_1.txt')
    mg.merge('Merge2/merge2file_3.txt', 'Merge2/mergefile_4.txt', 'Merge2/merge3file_2.txt')
    mg.merge('Merge2/merge3file_1.txt', 'Merge2/merge3file_2.txt', 'Merge2/finalmergefile.txt')
    endTime = time.time()
    print("final merge %d cost %ds" %(i+1, endTime-startTime))


    # Generate merged file with score based on final mered file.
    mergefile = 'Merge2/finalmergefile.txt'
    print("Start to generate merge_file_with_score.txt")
    tfidf_and_tagScore(mergefile)  # calculate score
    print("Finish generating merge_file_with_score.txt")


    #Generate json file with structure {docID: url}, similar to docIndexer
    print("Start to generate url_indexer.json")
    urlIndexer(path)
    print("Finish generating url_indexer.json")


    # Separate final merged file into 36 files, with name starting with one alphanum characters, for quick search.
    print("Start to generate separated files")
    ab = 'abcdefghijklmnopqrstuvwxyz0123456789'
    startTime = time.time()
    for i in range(len(ab)):
        char = ab[i]
        mg.separate('Merge2/merge_file_with_score.txt', char, 'ROOT/indexfile_%s.txt' %char)
    endTime = time.time()
    print("Finish generating separated files")
    with open('ROOT/secondaryIndex.txt', 'w') as f:
        json.dump(mg.advIndex, f)

    print("cost %ds" %(endTime-startTime))


