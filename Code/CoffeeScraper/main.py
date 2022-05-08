import logging
from Config import *
from ElasticSearchClient import ElasticSearchClient, MOCKElasticSearchClient
from HDFSclient import HDFSClient, MOCKHDFSClient
from CoffeeManualScraper import CoffeeManualScraper
import pandas as pd
from bs4 import BeautifulSoup
import requests
from queue import Queue
from urllib.parse import urlparse


def get_subpage_links(link, selector):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'lxml')
    #element = soup.find_next("div", {"class": "dln-category-browser__category"})
    # doesnt work anymore??
    element = soup.find("div", {"class": "dln-category-browser__category"})
    if element:
        return [element.select_one("a:not([href*=milch])")["href"]]
    raise ValueError("No Elements found")
    #return [elem['href'] for elem in element.select("a:not([href*=milch])")]


def getDetailPageInfo(link, selector):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'lxml')
    elements = soup.select(".dln-instruction-manuals__list > li > a")
    names = soup.select(".dln-instruction-manuals__list > li span:first-of-type")
    productName = soup.select_one(".dln-instruction-manuals__mainSubtitle").text.strip().replace(" ", "_")
    return [elem["href"] for elem in elements], [elem.text.strip() for elem in names], productName

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
    baseURL = "/manuals/"
    for index, row in sources.iterrows():
        if index >= 1:
            break
        pdfLinks = []
        mainLink = "https://" + urlparse(row["Link"]).netloc
        links = Queue()
        links.put(row["Link"])
        selector = "dln-category-browser__category"
        while True:
            link = links.get()
            try:
                [links.put(mainLink+sublink) for sublink in get_subpage_links(link, selector)]
            except ValueError:
                pdfURLs, names, productName = getDetailPageInfo(link, None)
                pdfURLs = [mainLink+link for link in pdfURLs]

                dataPath = baseURL + row["Manufacturer"] + "/" + productName
                for url, name in zip(pdfURLs, names):
                    if "Intro" in name:
                        continue
                    pdfLinks.append((name, url))

                break
            except Exception as e:
                print(e)
                break

    print("storing "+str(len(pdfLinks))+" pdfs at"+dataPath)
