#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
from abc import ABC, abstractmethod
import logging

class MetaClient(ABC):
    
    @abstractmethod
    def index_meta_data(self, metadata_json):
        logging.error("Method not implemented")

    @abstractmethod
    def get_latest_entry_URL(self, source_URL, region):
        logging.error("Method not implemented")

    @abstractmethod
    def delete_meta_data(self, id):
        logging.error("Method not implemented")


class ArticleClient(ABC):
    
    @abstractmethod
    def get_article_config(self, id):
        logging.error("Method not implemented")

    @abstractmethod
    def get_all_article_configs(self):
        logging.error("Method not implemented")


class FileClient(ABC):

    @abstractmethod
    def save_as_file(self, file_path, filename, content):
        logging.error("Method not implemented")

    @abstractmethod
    def read_file(self, file_path, filename):
        logging.error("Method not implemented")
