from elasticsearch import Elasticsearch
import logging
from Config import *

logger = logging.getLogger(loggerName)

class ElasticSearchClient:
    """
    Wrapper Class for the elasticsearch client
    offers all functionality concerning communication with the elasticsearch server
    """

    def __init__(self):
        """
        constructor which creates an instance of ElasticSearchClient with the url from the config
        """
        logger.info("Initializing ElasticSearch Client with URL: %s:%s", es_url, es_port)
        self.es_client = Elasticsearch([es_url + ':' + es_port])

        self.initIndex()

    def initIndex(self):
        """
        initializes required indices if not already existing
        """
        if not self.es_client.indices.exists(index=indexName):
            logger.info("Index %s not found - initializing index", indexName)
            self.es_client.indices.create(index=indexName, body=indexMapping, ignore=400)

        if not self.es_client.indices.exists(index=metaIndexName):
            logger.info("Index %s not found - initializing index", metaIndexName)
            self.es_client.indices.create(index=metaIndexName, body=metaIndexMapping, ignore=400)

    def getAllSources(self):
        """
        search elasticsearch for all federalState configs

        Args:
            result (list): all source elements - can be empty
        """
        query = {"size": 100, "query": {"match_all":{}}}
        docs = self.es_client.search(index=metaIndexName, body=query)
        result = []
        for doc in docs['hits']['hits']:
            result.append(doc["_source"])
        return result

    def checkExistance(self, id):
        """
        checks if an document with @id exists

        Args:
            result (boolean): True/False if document with @id is existing
        """
        return self.es_client.exists(index=indexName, id=id)

    def indexDoc(self, id, doc):
        """
        does index a single doc of metadata for restriction/measures

        Args:
            id (string): id of the document
            doc (object/dict): document to insert
        """
        self.es_client.index(index=indexName, id=id, body=doc)

    def indexConfig(self, id, doc):
        """
        does index a single doc of scraping config of a state

        Args:
            doc (object/dict): document to insert
        """
        self.es_client.index(index=metaIndexName, id=id, body=doc)

class MOCKElasticSearchClient():

    def __init__(self):
        pass