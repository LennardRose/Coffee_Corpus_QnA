from Config import *
import logging
import ssl

logger = logging.getLogger(loggerName)

class CoffeeManualScraper:
    """
    Class to scrape Manuals of Coffee Machine Manufacturers
    """
    def __init__(self, es_client, hdfs_client):
        """
        Constructor which creates an instance with given ElasticSearch Client and HDFS Client
        """
        self.es_client = es_client
        self.hdfs_client = hdfs_client
        ssl._create_default_https_context = ssl._create_unverified_context

    def scrape(self, source):
        """
        starts to scrape relevant data...
        """
        