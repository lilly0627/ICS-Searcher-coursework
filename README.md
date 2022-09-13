# ICS-Searcher-coursework

This is a web search engine, written in Python3, capable of handling over 60,000 web pages created by the School of ICS, UCI.

The query response time is under 200ms.

Installation: 
    python3==3.8.0
    pip install -r requirements.txt
    (OR pip install the following:
        beautifulSoup==4.11.0
        Flask==2.1.2
        nltk==3.7)


Setup:  
1.  Open indexer2.py, merge.py, and search.py, change the path to your local directory to DEV. (default path is ../DEV)
    
2.  If not, create new folder INDEX, Merge2, ROOT. (mkdir INDEX, mkdir Merge2, mkdir ROOT)
    
3.  Build the index in "INDEX" directory, which takes 6 hours. After finishing building the index, there will be 28 indexer files in the "INDEX" directory.
    Command: python indexer2.py
    
4.  After finishing Setup 1, merge the index files, storing them in "Merge" directory, a few minutes, 
    Command: python merge.py


Search:
After setup, 
    1.  Search using the terminal and command line: start running search.py, and enter your query after the "Query" prompt, enter "q" to quit the search
        command: python search.py
    2.  Search using the Web GUI: run app.py, open http://localhost:5000, and enter your query in the search box and click "Go". 
        command: python app.py (ctrl + c to quit the app)
        

