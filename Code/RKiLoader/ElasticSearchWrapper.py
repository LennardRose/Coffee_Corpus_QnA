import logging
import copy
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from Config import *


class ElasticSearchClient:
    """
    Wrapper Class for the elasticsearch client
    offers all functionality concerning communication with the elasticsearch server
    """

    def __init__(self):
        """constructor which crates ElasticSearchClient with the elasticsearch
        url from the config file
        """
        logging.info('Init Elasticsearch client with url: ' +
                     elasticsearch_url + ':' + elasticsearch_port)
        self.es_client = Elasticsearch(
            [elasticsearch_url + ':' + elasticsearch_port])

    def get_es_client(self):
        """get the created es client for own use

        Returns:
            elasticsearch instance: the elasticsearch client
        """
        return self.es_client

    def index_single_document(self, index, document):
        """index weather data to elasticsearch

        Args:
            index (string): the target index as a string representation
            document (object/dict): document you want to index
        """
        self.es_client.index(index=index, body=document,
                             doc_type='_doc')

    def bulk_index_list(self, index_name, document_list, chunk_size=1000):
        """indexes a list of documents using the bulk index api
        converts list of objects to a bulk index command
        make sure index exists before using this method

        Args:
            index_name (string): name of the es index
            document_list (list): python list containing all documents you want to index
            chunk_size (int, optional): how many docs per bulk request shall be added to the request. Defaults to 10000.
        """
        if document_list:
            base_map = {}
            base_map['_index'] = index_name
            items = []
            for elem in document_list:
                base_map['_source'] = elem
                items.append(copy.copy(base_map))
            helpers.bulk(self.es_client, items, chunk_size=chunk_size)

    def get_latest_document_by_index(self, index_name, date_field_name):
        """ Executes a query that returns the timestamp of the latest document in an index based
        on the specified time field

        Args:
            index_name (string): name of the elasticsearch index
            date_field_name (string): name of the date field you want to check
        """
        search_body = {'size': 1, 'sort': {
            date_field_name: 'desc'}, 'query': {'match_all': {}}}
        search_result = self.es_client.search(
            body=search_body, index=index_name)
        if not search_result['hits'] or not search_result['hits']['hits'] or not search_result['hits']['hits'][0] or not search_result['hits']['hits'][0]['_source']:
            logging.error('No date time field found')
            return 0
        else:
            document = search_result['hits']['hits'][0]['_source']
            return document[date_field_name]
