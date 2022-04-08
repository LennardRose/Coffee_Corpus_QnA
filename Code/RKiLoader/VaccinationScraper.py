from AbstractScraper import AbstractScraper
import requests
from Config import *
from Util import *
from ElasticSearchWrapper import ElasticSearchClient
import copy
import logging


class VaccinationScraper(AbstractScraper):
    """Class to scrape vaccination data of rki api
    """

    def __init__(self, es_client, hdfs_client) -> None:
        """ init function to save an elasticsearch client instance and init empty vaccination data

        Args:
            es_client (ElasticsearchWrapper): a created elasticsearch client instance
            hdfs_client (HdfsClient): hdfs client 
        """
        self.vaccination_data = {}
        self.es_client = es_client
        self.hdfs_client = hdfs_client
        self.request_time = None
        self.request_time_latest = self.es_client.get_latest_document_by_index(
            elasticsearch_vaccination_index, 'data_request_time')

    def get_vaccination_data_raw(self):
        """function that returns raw vaccination data
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw vaccination data
        """
        if not self.vaccination_data or self.vaccination_data is None:
            self.vaccination_data = requests.get(
                corona_api_base_url + corona_api_vaccinations).json()
            self.request_time = current_milli_time()
        return self.vaccination_data

    def convert_raw_data_to_state_list(self):
        """create list of vaccination data consisting of vaccination data of all 16 states in germany

        Returns:
            list: vacination data per state as a list
        """
        vaccination_data = copy.deepcopy(self.get_vaccination_data_raw())
        states_list = []
        states = vaccination_data['data']['states']
        for state in german_state_list_abbreviated:
            state_object = states[state]
            state_object['data_request_time'] = self.request_time
            states_list.append(state_object)
        return states_list

    def get_meta_data_from_raw_data(self):
        """get meta data from vaccination raw data

        Returns:
            dict: meta data of vaccination request
        """
        data = copy.deepcopy(self.get_vaccination_data_raw())
        del data['data']['states']
        data['identifier'] = elasticsearch_vaccination_index
        return data

    def index_data(self):
        """index the converted vaccination data to elasticsearch 
        meta data and state data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_vaccination_index, document_list=self.convert_raw_data_to_state_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_meta_data_from_raw_data())

    def save_raw_data_to_hdfs(self):
        """Saves raw data to hdfs
        """
        self.hdfs_client.save_json_to_hdfs(
            self.vaccination_data, hdfs_vaccination_base_path+get_current_date()+'/' + str(self.request_time)+'.json')

    def scrape_data(self):
        """main function that scrapes and saves all data to all targets]
        """
        if self.validate_scrape_status(self.request_time_latest):
            logging.debug('Indexing vaccination Data')
            self.index_data()
            logging.debug('Saving raw vaccination data to hdfs')
            self.save_raw_data_to_hdfs()
        else:
            logging.info('Testing data was already scraped')
