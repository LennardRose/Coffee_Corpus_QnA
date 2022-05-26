ELASTICSEARCH_URL = "localhost",
ELASTICSEARCH_PORT = "9200",
HDFS_URL = "192.168.0.115",
HDFS_PORT = "9870",
HDFS_USER = "hadoop",
RECENT_MANUAL_COUNT = "100",
MAX_TRY = "3",
STANDARD_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ",
STANDARD_DATE_FORMAT = "%Y-%m-%d",
STANDARD_LOG_FORMAT = "[%(levelname)s][%(asctime)s]: %(message)s",
STANDARD_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S",
STANDARD_LOG_FILENAME = "manualscraper.log",
WEBDRIVER_DIR = "drivers",
WEBDRIVER_FILE = "chromedriver.exe",
CLIENTS = {
    "META_CLIENT": "mock_elastic",
    "MANUAL_CLIENT": "mock_elastic",
    "FILE_CLIENT": "mock_hdfs"
}
