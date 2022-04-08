import pandas as pd
import logging
import json
from Config import *
from ElasticSearchClient import ElasticSearchClient
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    logging.debug("Creating ElasticSearch Client")
    es_client = ElasticSearchClient()

    sources = pd.read_csv("urls.csv", sep=";")

    for index, row in sources.iterrows():
        data = {}
        data["state"] = row.State
        data["url"] = row.URL
        data["target"] = row.Target
        data["value"] = row.Value
        json_object = json.dumps(data)
        es_client.indexConfig(row.State, json_object)