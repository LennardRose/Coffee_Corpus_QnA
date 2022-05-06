import logging
from Config import *
from ElasticSearchClient import ElasticSearchClient, MOCKElasticSearchClient
from HDFSclient import HDFSClient, MOCKHDFSClient
from CoffeeManualScraper import CoffeeManualScraper
import pandas as pd
from bs4 import BeautifulSoup
import requests

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, filename=logFileName)
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    logger.debug("Creating ElasticSearch Client")
    es_client = MOCKElasticSearchClient()
    logger.debug("Creating HDFS Client")
    hdfs_client = MOCKHDFSClient()

    logger.debug("Starting CoffeeManualScraper")
    coffeeScraper = CoffeeManualScraper(es_client=es_client, hdfs_client=hdfs_client)

    # get all sources:
    logger.debug("Collecting all sources from local")
    sources = pd.read_excel("../../sources/sources.xlsx")
    sources.dropna(subset=['Manufacturer'], inplace=True)

    for index, row in sources.iterrows():
        page = requests.get(row["Link"])
        soup = BeautifulSoup(page.content, 'lxml')
        elements = soup.find_all("div", {"class":"dln-categoryBox"})
        filteredElem = []
        for elem in elements:
            filtered = elem.select_one("a:not([href*=milch])")
            if filtered:
                filteredElem.append(filtered['href'])
        print(elements)
    print(sources)