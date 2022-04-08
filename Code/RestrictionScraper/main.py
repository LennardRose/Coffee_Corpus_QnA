import logging
import json
import pandas as pd
from Config import *
from ElasticSearchClient import ElasticSearchClient
from HDFSclient import *
from RestrictionScraper import RestrictionScraper

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, filename=logFileName)
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    logger.debug("Creating ElasticSearch Client")
    es_client = ElasticSearchClient()
    logger.debug("Creating HDFS Client")
    hdfs_client = MOCKHDFSClient()

    logger.debug("Starting RestrictionScraper")
    restrictionScraper = RestrictionScraper(es_client=es_client, hdfs_client=hdfs_client)

    # get all sources:
    logger.debug("Collecting all sources from ElasticSearch")
    sources = es_client.getAllSources()

    for source in sources:
        restrictionScraper.scrape(source)

    logger.info("Finished scraping RestrictionData")
