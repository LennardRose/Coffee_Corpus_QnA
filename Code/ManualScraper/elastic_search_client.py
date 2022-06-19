#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
from abstract_client import ManualClient, MetaClient
import logging
from elasticsearch import Elasticsearch
import utils


class ElasticSearchClient(MetaClient, ManualClient):
    """
    Wrapper Class for the elasticsearch client
    offers all functionality concerning communication with the elasticsearch server
    """


    def __init__(self):
        """
        constructor which crates ElasticSearchClient with the elasticsearch
        url from the config file
        """

        logging.info("Init Elasticsearch client with url: %s : %s", utils.config["ELASTICSEARCH_URL"],
                     utils.config["ELASTICSEARCH_PORT"])
        self.es_client = Elasticsearch([utils.config["ELASTICSEARCH_URL"] + ":" + utils.config["ELASTICSEARCH_PORT"]])

        self._initialize_indizes_if_not_there()


    def _initialize_indizes_if_not_there(self):
        """
        initializes needed indizes if not already there
        """
        if not self.es_client.indices.exists(index="manual_config"):
            logging.info("Index manual_config not found, initialize index.")
            self.es_client.indices.create(index="manual_config")

        if not self.es_client.indices.exists(index="manual_meta_data"):
            logging.info("Index manual_meta_data not found, initialize index.")
            self.es_client.indices.create(index="manual_meta_data", body=self._get_manual_meta_data_mapping())


    def delete_meta_data(self, id):
        """
        deletes meta_data doc in manual_meta_data index
        """
        self.es_client.delete(index="manual_meta_data", id=id)


    def get_manual_config(self, id):
        """
        search elasticsearch for article configs by id
        :param id: the id you want to search for
        :return: _source element of the found _doc or nothing
        """

        query = {"query": {"match": {"_id": {"query": id}}}}
        docs = self.es_client.search(index="manual_config", body=query)
        if docs["hits"]["hits"]:
            return docs["hits"]["hits"][0]["_source"]
        else:
            logging.error("id: " + id + " not found.")


    def get_all_manual_configs(self):
        """
        search elasticsearch for all article configs
        :return: result field - list format - with all _source elements of the index - can be empty
        """

        query = {"size": 1000, "query": {"match_all": {}}}
        docs = self.es_client.search(index="manual_config", body=query)
        result = []
        for doc in docs["hits"]["hits"]:
            result.append(doc["_source"])
        return result


    def index_meta_data(self, metadata_json):
        """
        index meta data to elasticsearch
        :return: the id of the new indexed meta data
        """

        result = self.es_client.index(index="manual_meta_data", body=metadata_json,
                                      doc_type="_doc")

        if result["result"] == "created" and result["_id"]:
            return result["_id"]

        else:
            raise Exception("meta_data not created")


    def get_latest_entry_URL(self, source_URL, manufacturer_name):
        """
        searches for the latest entries url of the given website, number of returned entries defined in config
        latest means  index time 
        :param source_URL: the URL of the site we are looking for the latest entry
        :returns: the url of the latest entries in the manual_meta_data index with the matching source_URL
        """
        try:
            result = []
            query = {
                "_source":
                    {"includes": ["URL"]
                     },
                "query":
                    {"bool":
                        {"must": [
                            {"match_phrase": {"manufacturer_name": {"query": manufacturer_name}}},
                            {"match_phrase": {"source_url": {"query": source_URL}}}
                        ]}
                    },
                "sort": [{"index_time": {"order": "desc"}}],
                "size": utils.config["RECENT_MANUAL_COUNT"]
            }
            docs = self.es_client.search(index="manual_meta_data", body=query)

            for doc in docs["hits"]["hits"]:
                result.append(doc["_source"]["URL"])

            return result
        except:
            return None


    def _get_manual_meta_data_mapping(self):
        """
        :return: the manual_meta_data index mapping
        """
        return {
            "mappings": {
                "properties": {
                    "URL": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "filename": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "filepath": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "index_time": {
                        "type": "date"
                    },
                    "language": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "manual_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "manufacturer_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "product_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "source_URL": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            }
        }


class MockElasticSearchClient(MetaClient, ManualClient):

    def index_meta_data(self, metadata_json):
        return True


    def get_latest_entry_URL(self, source_URL, region):
        return False


    def delete_meta_data(self, id):
        return True


    def get_manual_config(self, id):
        return True


    def get_all_manual_configs(self):
        return True


    def __init__(self):
        pass
