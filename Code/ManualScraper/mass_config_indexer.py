import pandas as pd
import json
import config
from elastic_search_client import ElasticSearchClient
from os import listdir
from os.path import isfile, join

if __name__ == "__main__":
    path = "./manual_sources"

    es_client = ElasticSearchClient()

    for f in listdir(path):
        if isfile(join(path, f)):
            with open(join(path, f), "r", encoding='utf-8') as file:
                source = json.load(file)

                es_client.index_config(source["manufacturer_name"], source)