from datetime import datetime
import ssl
import logging
import json
from Config import *
from Util import *
from Parser import Parser

logger = logging.getLogger(loggerName)

class RestrictionScraper:
    """
    Class to scrape Restriction data
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
        starts to scrape relevant data with given key/value pair from the url
        tries to extract metadata from the condensed data returned from Parser as string and index that

        Args:
            source (dict): scraping config like the current state, from which url,
                            the target (e.q. CSSselector/class etc.) and the value for the target
        """
        state = source["state"]
        url = source["url"]
        target = source["target"]
        value = source["value"]
        directory = HDFS_MEASURES_BASE_PATH + state + "/" + datetime.now().strftime("%d-%m-%Y_%H-%M/")

        logger.info("Starting scraping for %s with URL %s", state, url)

        parser = Parser(self.hdfs_client, directory, url, target, value)
        data = parser.parse()
        if data:
            metadata = self.getMetadata(state, data)
            self.hdfs_client.save_as_json(directory, "metadata.json", metadata)
            self.saveMetadata(metadata)
        else:
            logger.error("nothing found for URL %s", url)

        logger.info("Finished scraping for State %s done", state)

    def getMetadata(self, state, data):
        """
        analyzes the data string for a starting date of the measurement and if its incidence based or not

        Args:
            state (string): the current federal state
            data (string): the extracted data from the website represented as a text string
            metadata (dict): the analyzed metadata as a dict
        """

        logger.info("analyzing Metadata...")

        metadata = dict.fromkeys(METADATA_ATTRIBUTES)
        metadata['creationDate'] = datetime.now().strftime("%d-%m-%Y")
        metadata['incidenceBased'] = False
        metadata['federateState'] = state

        metadata['validFrom'] = extractDate(data).strftime("%d-%m-%Y")
        incidenceRanges = extractIncidences(data)

        if incidenceRanges:
            metadata["incidenceRanges"] = incidenceRanges
            metadata["incidenceBased"] = True

        metadata["tags"] = self.checkForTags(data)

        return metadata

    def checkForTags(self, data):
        """
        iterates through the TAGS from the config to narrow down
        the affected categories of the measurement

        Args:
            data (string): the extracted data from the website represented as a text string
            foundTags (list): the analyzed tags from the data
        """
        foundTags = []
        for tag, keys in TAGS.items():
            for key in keys:
                if re.search(key, data, re.IGNORECASE):
                    #if any string from the list of keys is in data
                    if foundTags is None:
                        foundTags = [tag]
                    else:
                        if tag not in foundTags:
                            foundTags.append(tag)
                else:
                    continue

        return foundTags

    def saveMetadata(self, metadata):
        """
        saves the metadata to ElasticSearch

        Args:
            metadata (dict): the analyzed metadata as a dict
        """
        logger.info("writing Metadata-JSON to Elasticsearch")
        json_object = json.dumps(metadata)

        uid = metadata["federateState"] + metadata['validFrom']

        if not self.es_client.checkExistance(uid):
            self.es_client.indexDoc(uid, json_object)