from abc import ABC, abstractmethod
from Util import *
import logging
import copy


class AbstractScraper(ABC):

    @abstractmethod
    def index_data(self):
        logging.error("Method not implemented")

    @abstractmethod
    def scrape_data(self):
        logging.error("Method not implemented")

    @abstractmethod
    def save_raw_data_to_hdfs(self):
        logging.error("Method not implemented")

    def convert_raw_data_to_list(self, data, request_time):
        """create list of  data consisting of incidence data 

        Returns:
            list: incidence data as a list
        """
        output_list = []
        data_raw = copy.deepcopy(data)
        dict_keys = data_raw['data'].keys()
        for key in dict_keys:
            item = data_raw['data'][key]
            item['data_request_time'] = request_time
            output_list.append(item)

        return output_list

    def validate_scrape_status(self, latest_request_time):
        current_day = round_time_milli_to_day(
            current_milli_time(), milli_flag=True)
        if latest_request_time != 0:
            last_index_day = round_time_milli_to_day(
                latest_request_time, milli_flag=True)
        else:
            last_index_day = 0
        if current_day == last_index_day:
            return False
        else:
            return True
