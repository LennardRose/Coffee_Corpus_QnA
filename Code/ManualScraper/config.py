# -------------------------------COMMON------------------------------------------
MAX_TRY = 3
# dont change this config without checking if it is a elasticsearch readable date-format (if you use elasticsearch)
# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html#strict-date-time
STANDARD_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
STANDARD_DATE_FORMAT = "%Y-%m-%d"
STANDARD_LOG_FORMAT = "[%(levelname)s][%(asctime)s]: %(message)s"
STANDARD_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
STANDARD_LOG_FILENAME = "manualscraper.log"
WEBDRIVER_DIR = "drivers"
WEBDRIVER_FILE = "chromedriver.exe"
CLIENTS = {
    "META_CLIENT": "elastic",
    "MANUAL_CLIENT": "elastic",
    "FILE_CLIENT": "mock_hdfs"
}
# -------------------------------HDFS---------------------------------------------------
HDFS_URL = "192.168.0.115"
HDFS_PORT = "9870"
HDFS_USER = "hadoop"
# -------------------------------ElasticSearch------------------------------------------
ES_URL = '127.0.0.1'
ES_PORT = '9200'

sourceIndex = "manuals_config"
sourceMapping = {

}

metaIndex = "manuals_meta"
metaMapping = {
            "mappings": {
                "properties": {
                    "URL": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 512
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
                                "ignore_above": 512
                            }
                        }
                    },
                    "index_time": {
                        "type": "date",
                        "format": "yyyy-MM-dd'T'HH:mm:ssZ"
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

