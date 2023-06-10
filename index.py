import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json

from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from java.nio.file import Paths

def create_index(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    for data in os.listdir('data'):
        path = os.path.join('data', data)
        if os.path.isfile(path) and data.endswith('.json'):
            with open(path, 'r') as file:
                json_data = json.load(file)

                for post in json_data:
                    title = post['Title']
                    postid = post['PostID']
                    createdutc = post['CreatedUTC']
                    upvotes = post['UpVotes']
                    upvotesratio = post['UpVotesRatio']
                    posturl = post['PostURL']
                    permalink = post['PermaLink']
                    body = post['SelfText']
                    postlinktitle = post['PostLinkTitle']
                    comments = post["Comments"]
                    commentlinktitles = post["CommentLinkTitles"]

                    doc = Document()
                    doc.add(Field('Title', str(title), metaType))
                    doc.add(Field('PostID', str(postid), metaType))
                    doc.add(Field('CreatedUTC', str(createdutc), metaType))
                    doc.add(Field('UpVotes', str(upvotes), metaType))
                    doc.add(Field('UpVotesRatio', str(upvotesratio), metaType))
                    doc.add(Field('PostURL', str(posturl), metaType))
                    doc.add(Field('PermaLink', str(permalink), metaType))
                    doc.add(Field('Body', str(body), contextType))
                    #doc.add(Field('PostLinkTitle', str(postlinktitle), contextType))
                    #doc.add(Field('Comments', str(comments), contextType))
                    #doc.add(Field('CommentLinkTitles', str(commentlinktitles), contextType))
                    writer.addDocument(doc)
    
    writer.close()

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('Title', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "title": doc.get("Title"),
            "body": doc.get("Body"),
            "url": "https://www.reddit.com" + doc.get("PermaLink"),
        })
    
    print(topkdocs)

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
create_index('lucene_index/')
# in index.py, the retrieve function is just for debugging purposes (we call it with the query web data)
retrieve('lucene_index/', 'web data')
