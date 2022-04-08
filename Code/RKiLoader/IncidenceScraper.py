from requests.api import get
from AbstractScraper import AbstractScraper
import requests
import requests
import pandas as pd
from Config import *
from Util import *
from ElasticSearchWrapper import ElasticSearchClient
from HdfsClient import HdfsClient
import copy
import logging


class IncidenceScraper(AbstractScraper):
    """Class to scrape incidence data of rki api
    """

    def __init__(self, es_client, hdfs_client) -> None:
        """ init function to save an elasticsearch client instance and init empty incidence data

        Args:
            es_client (ElasticsearchWrapper): a created elasticsearch client instance
            hdfs_client (HdfsClient): hdfs client 
        """
        self.incidence_district_data = {}
        self.incidence_states_data = {}
        self.es_client = es_client
        self.hdfs_client = hdfs_client
        self.request_time_states = None
        self.request_time_districts = None
        self.city_df = pd.read_csv(path_to_city_csv, header=0, sep=';')
        self.request_time_latest = self.es_client.get_latest_document_by_index(
            elasticsearch_incidence_index, 'data_request_time')

    def get_district_incidence_data_raw(self):
        """function that returns raw incidence data for all districts
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw incidence data per district
        """
        if not self.incidence_district_data or self.incidence_district_data is None:
            self.incidence_district_data = requests.get(
                corona_api_base_url + corona_api_districts).json()
            self.request_time_districts = current_milli_time()
        return self.incidence_district_data

    def get_state_incidence_data_raw(self):
        """function that returns raw incidence data for all states
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw incidence data per state
        """
        if not self.incidence_states_data or self.incidence_states_data is None:
            self.incidence_states_data = requests.get(
                corona_api_base_url + corona_api_states).json()
            self.request_time_states = current_milli_time()
        return self.incidence_states_data

    def convert_raw_district_data_to_district_list(self):
        """create list of incidence data consisting of incidence data per district
        Returns:
            list: incidence data per district as a list
        """
        district_list = self.convert_raw_data_to_list(
            self.get_district_incidence_data_raw(), self.request_time_districts)

        return district_list

    def convert_raw_state_data_to_state_list(self):
        """create list of incidence data consisting of incidence data per state
        Returns:
            list: incidence data per state as a list
        """
        state_list = self.convert_raw_data_to_list(
            self.get_state_incidence_data_raw(), self.request_time_states)

        return state_list

    def get_district_meta_data_from_raw_data(self):
        """get district meta data from district incidence raw data

        Returns:
            dict: meta data of district incidence request
        """
        data = copy.deepcopy(self.get_district_incidence_data_raw())
        del data['data']
        data['identifier'] = elasticsearch_incidence_index
        return data

    def get_state_meta_data_from_raw_data(self):
        """get state meta data from state incidence raw data

        Returns:
            dict: meta data of state incidence request
        """
        data = copy.deepcopy(self.get_state_incidence_data_raw())
        del data['data']
        data['identifier'] = elasticsearch_incidence_index
        return data

    def index_data(self):
        """index the converted incidence data to elasticsearch 
        meta data and district data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_incidence_index, document_list=self.convert_raw_state_data_to_state_list())
        self.es_client.bulk_index_list(
            index_name=elasticsearch_incidence_index, document_list=self.convert_raw_district_data_to_district_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_district_meta_data_from_raw_data())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_state_meta_data_from_raw_data())

    def save_raw_data_to_hdfs(self):
        """Saves raw data to hdfs
        """
        self.hdfs_client.save_json_to_hdfs(self.incidence_district_data, hdfs_incidence_district_base_path +
                                           get_current_date()+'/'+str(self.request_time_districts)+'.json')
        self.hdfs_client.save_json_to_hdfs(self.incidence_states_data, hdfs_incidence_state_base_path +
                                           get_current_date()+'/'+str(self.request_time_districts)+'.json')

    def scrape_data(self):
        """main function that scrapes and saves all data to all targets]
        """
        if self.validate_scrape_status(self.request_time_latest):
            logging.debug('Indexing incidence Data')
            self.index_data()
            logging.debug('Saving raw incidence data to hdfs')
            self.save_raw_data_to_hdfs()
        else:
            logging.info('Incidence data was already scraped')
