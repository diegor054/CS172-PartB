## In the terminal, "export FLASK_APP=flask_demo" (without .py)
## flask run -h 0.0.0.0 -p 8888

import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from flask import request, Flask, render_template

app = Flask(__name__)

sample_doc = [
    {
        'title' : 'A',
        'context' : 'lucene is a useful tool for searching and information retrieval'
        },
    {
        'title' : 'B',
        'context' : 'Bert is a deep learning transformer model for encoding textual data'
    },
    {
        'title' : 'C',
        'context' : 'Django is a python web framework for building backend web APIs'
    }
]      

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('Context', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "text": doc.get("Context")
        })
    return topkdocs
    #print(topkdocs)

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
        docs = retrieve('sample_lucene_index/', str(query))
        print(docs)
        
        return render_template('output.html',lucene_output = docs)
    
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    
if __name__ == "__main__":
    app.run(debug=True)

# create_index('sample_lucene_index/')
# retrieve('sample_lucene_index/', 'web data')


