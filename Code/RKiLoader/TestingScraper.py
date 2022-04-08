from AbstractScraper import AbstractScraper
import requests
import copy
import logging
from Config import *
from Util import *
from ElasticSearchWrapper import ElasticSearchClient


class TestingScraper(AbstractScraper):
    """Class to scrape testing data of rki api
    """

    def __init__(self, es_client, hdfs_client) -> None:
        """ init function to save an elasticsearch client instance and init empty testing data

        Args:
            es_client (ElasticsearchWrapper): a created elasticsearch client instance
            hdfs_client (HdfsClient): hdfs client 
        """
        self.testing_data = {}
        self.es_client = es_client
        self.hdfs_client = hdfs_client
        self.request_time = None
        self.request_time_latest = self.es_client.get_latest_document_by_index(
            elasticsearch_testing_index, 'data_request_time')
        self.latest_week = self.get_latest_week_from_es()

    def get_testing_data_raw(self):
        """function that returns raw testing data
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw testing data
        """
        if not self.testing_data or self.testing_data is None:
            self.testing_data = requests.get(
                corona_api_base_url + corona_api_testing).json()
            self.request_time = current_milli_time()
        return self.testing_data

    def convert_raw_data_to_week_list(self):
        """create list of testing data consisting of testing data for x last calendarweeks

        Returns:
            list: testing data per state as a list
        """
        data = copy.deepcopy(self.get_testing_data_raw())
        week_list = []
        for week in data['data']['history']:
            week_date = week['calendarWeek']
            if '/' in week_date:
                splitted = week_date.split('/')
            else:
                continue
            week['week'] = splitted[0]
            week['year'] = splitted[1]
            week['unique_sort_order'] = splitted[1] + splitted[0]
            week['data_request_time'] = self.request_time
            del week['calendarWeek']
            if int(week['unique_sort_order']) > self.latest_week:
                week_list.append(week)
        return week_list

    def get_meta_data_from_raw_data(self):
        """get meta data from testing raw data

        Returns:
            dict: meta data of testing request
        """
        data = copy.deepcopy(self.get_testing_data_raw())
        del data['data']
        data['identifier'] = elasticsearch_testing_index
        return data

    def index_data(self):
        """index the converted testing data to elasticsearch
        meta data and week data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_testing_index, document_list=self.convert_raw_data_to_week_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_meta_data_from_raw_data())

    def get_latest_week_from_es(self):
        """Get the latest indexed week from elasticsearch

        Returns:
            int: the year+week thats the biggest ergo the newest
        """
        search_result = self.es_client.get_es_client().search(
            index=elasticsearch_testing_index, body='{"size":0,"aggs":{"max_unique_sort_order":{"top_hits":{"sort":[{"unqiue_sort_order":{"order":"desc"}}],"size":1}}}}')
        if not search_result['aggregations']['max_unique_sort_order']['hits']['hits']:
            return 0
        else:
            return search_result['aggregations']['max_unique_sort_order']['hits']['hits'][0]['_source']['unique_sort_order']

    def save_raw_data_to_hdfs(self):
        """Saves raw data to hdfs
        """
        self.hdfs_client.save_json_to_hdfs(
            self.testing_data, hdfs_testing_base_path+get_current_date()+'/' + str(self.request_time)+'.json')

    def scrape_data(self):
        """main function that scrapes and saves all data to all targets]
        """
        if self.validate_scrape_status(self.request_time_latest):
            logging.debug('Indexing Testing Data')
            self.index_data()
            logging.debug('Saving raw testing data to hdfs')
            self.save_raw_data_to_hdfs()
        else:
            logging.info('Testing data was already scraped')
