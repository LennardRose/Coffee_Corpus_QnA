from IncidenceScraper import IncidenceScraper
from TestingScraper import TestingScraper
from VaccinationScraper import VaccinationScraper
from IncidenceScraper import IncidenceScraper
from ElasticSearchWrapper import ElasticSearchClient
from HdfsClient import HdfsClient
from Util import *
import logging


if __name__ == "__main__":

    logging.basicConfig(filename='RKiLoader.log', level=logging.DEBUG)
    logging.debug('Creating elasticsearch client')
    es_client = ElasticSearchClient()
    logging.debug('Creating HDFS client')
    hdfs_client = HdfsClient()

    vaccination_scraper = VaccinationScraper(
        es_client=es_client, hdfs_client=hdfs_client)
    testing_scraper = TestingScraper(
        es_client=es_client, hdfs_client=hdfs_client)
    incidence_scraper = IncidenceScraper(
        es_client=es_client, hdfs_client=hdfs_client)

    logging.debug('Starting to scrape vaccination data')
    vaccination_scraper.scrape_data()
    logging.info('Finished scraping vaccination data')
    logging.debug('Starting to scrape testing data')
    testing_scraper.scrape_data()
    logging.info('Finished scraping testing data')
    logging.debug('Starting to scrape incidence data')
    incidence_scraper.scrape_data()
    logging.info('Finished scraping incidence data')
