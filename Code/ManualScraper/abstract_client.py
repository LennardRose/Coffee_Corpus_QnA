#####################################################################
#                                                                   #
#                     Lennard Rose 5122737                          #
#                     Jochen Schmidt 5122xxx                        #
#                     Esther Ademola 5122xxx                        #
#                     Marius Benkert 5122xxx                        #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2022                                  #
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


class ManualClient(ABC):
    
    @abstractmethod
    def get_manual_config(self, id):
        logging.error("Method not implemented")

    @abstractmethod
    def get_all_manual_configs(self):
        logging.error("Method not implemented")


class FileClient(ABC):

    @abstractmethod
    def save_as_file(self, file_path, filename, content):
        logging.error("Method not implemented")

    @abstractmethod
    def read_file(self, file_path):
        logging.error("Method not implemented")
