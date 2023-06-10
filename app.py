## In the terminal, "export FLASK_APP=app" (without .py)
## flask run -h 0.0.0.0 -p 8888

import lucene
import os
import datetime

from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query, BooleanQuery, BooleanClause
from org.apache.lucene.search.similarities import BM25Similarity
from java.nio.file import Paths
from flask import request, Flask, render_template

app = Flask(__name__)

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))

    boosts = {"Title": 2.0, "Body": 1.0}
    analyzer = StandardAnalyzer()

    titleBoost = boosts.get("Title", 1.0)
    titleQuery = QueryParser("Title", analyzer).parse(QueryParser.escape(query))
    boostedTitleQuery = BoostQuery(titleQuery, titleBoost)

    bodyBoost = boosts.get("Body", 1.0)
    bodyQuery = QueryParser("Body", analyzer).parse(QueryParser.escape(query))
    boostedBodyQuery = BoostQuery(bodyQuery, bodyBoost)

    booleanQuery = BooleanQuery.Builder()
    booleanQuery.add(boostedTitleQuery, BooleanClause.Occur.SHOULD)
    booleanQuery.add(boostedBodyQuery, BooleanClause.Occur.SHOULD)
    combinedQuery = booleanQuery.build()

    topDocs = searcher.search(combinedQuery, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "title": doc.get("Title"),
            "date": datetime.datetime.fromtimestamp(float(doc.get("CreatedUTC"))).strftime("%B %d, %Y"),
            "upvotes": doc.get("UpVotes"),
            "url": "https://www.reddit.com" + doc.get("PermaLink"),
            "body": doc.get("Body"),
        })

    return topkdocs

@app.route("/")
def home():
    return 'hello!~!!'

@app.route("/abc")
def abc():
    return 'hello alien'

@app.route('/input', methods = ['POST', 'GET'])
def input():
    return render_template('input.html')

@app.route('/output', methods = ['POST', 'GET'])
def output():
    if request.method == 'GET':
        return f"Nothing"
    if request.method == 'POST':
        form_data = request.form
        query = form_data['query']
        print(f"this is the query: {query}")
        lucene.getVMEnv().attachCurrentThread()
        docs = retrieve('lucene_index/', str(query))
        print(docs)
        return render_template('output.html',lucene_output = docs)
    
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    
if __name__ == "__main__":
    app.run(debug=True)