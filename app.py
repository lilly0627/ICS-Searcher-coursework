"""
    web app based on flask
"""
from flask import Flask, request, redirect, url_for, render_template
import search

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def webSearch():
    if request.method == 'POST':
        query = request.form['query']
        if query:
            print(query)
        results = search.runSearch(query=query, urlIndexer=search.urlIndexer)
        return render_template("Homepage.html", data = results)
    else:
        return render_template("index.html")


# @app.route('/home')
# def showResult():
#     searchResult = ["www.google.com", "www.apple.com", "www.uci.edu"]
#     return render_template("Homepage.html", data = searchResult)

if __name__ == '__main__':
    app.debug = True
    app.run()