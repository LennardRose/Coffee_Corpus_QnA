#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
from hdfs_client import HDFSClient, MOCKHDFSClient
from abstract_client import *
from elastic_search_client import ElasticSearchClient, MockElasticSearchClient
import utils

_file_client = None
_manual_client = None
_meta_client = None


def get_meta_client() -> MetaClient:
    """
    returns a client for metadata
    """
    global _meta_client
    if _meta_client == None:
        _meta_client = _read_client_from_config("META_CLIENT")
    return _meta_client

def get_manual_client() -> ManualClient:
    """
    returns a client for article_configs
    """
    global _manual_client
    if _manual_client == None:
        _manual_client = _read_client_from_config("MANUAL_CLIENT")
    return _manual_client

def get_file_client( ) -> FileClient:
    """
    returns a client for files
    """
    global _file_client
    if _file_client == None:
        _file_client = _read_client_from_config("FILE_CLIENT")
    return _file_client


def _read_client_from_config(client_type):
    """
    returns an client based on its type and the class as set in the config file
    """
    client_name = utils.config["CLIENTS"][client_type]

    if client_name == "elastic":
        return ElasticSearchClient()
    elif client_name == "mock_elastic":
        return MockElasticSearchClient()
    elif client_name == "hdfs":
        return HDFSClient()
    elif client_name == "mock_hdfs":
        return MOCKHDFSClient()
    else:
        logging.error("Unable to find client: " + client_name)
