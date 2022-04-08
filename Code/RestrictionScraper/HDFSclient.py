from pywebhdfs.webhdfs import PyWebHdfsClient
import os
import json
import logging
from Config import *

logger = logging.getLogger(loggerName)


class HDFSClient:
    """
    HDFS Helper class
    """

    def __init__(self):
        """
        init function that creates an insecure hdfs client
        """
        self.hdfs_client = PyWebHdfsClient(
            host=HDFS_BASE_URL, port=HDFS_PORT, user_name=HDFS_USER)
        self.test_hdfs_connection()

    def test_hdfs_connection(self):
        """Testing the hdfs connection by trying to list items in the root directory

        Raises:
            IOError: Raises an Error when connection is offline
        """
        logger.info('Testing HDFS connection')
        try:
           self.hdfs_client.list_dir('/')
        except Exception:
            logger.error('No HDFS connection')
            raise IOError

    def save_as_file(self, path, filename, content):
        """
        saves the content with a given filename as a file
        """
        logger.info("saving %s to hdfs filesystem", path+filename)
        self.hdfs_client.create_file(file_data=content, path=path+filename)


    def open_file(self, path, filename):
        """
        opens the file by filename
        """
        try:
            logger.info("reading %s from hdfs filesystem", path + filename)
            with open(path+filename, "r") as file:
                return file
        except:
           logger.error(path+filename + " not found.")

    def save_as_json(self, path, filename, json_doc):
        """takes a meta json and a target path
        uploads the file with utf-8 encoding to hdfs
        careful it overwrites the file if already present

        Args:
            meta_json (dict): meta json as a dictionary / json object
            target_path (dict): hdfs file path of target location
        """
        logger.info("saving %s to hdfs filesystem", path + filename)
        self.hdfs_client.create_file(
            path + filename, json.dumps(json_doc), overwrite=True)


class MOCKHDFSClient:

    def save_as_file(self, file_path, filename, content):
        """
        saves the content with a given filename as a file
        """
        file_path = file_path[1:]
        if not os.path.isdir(file_path):
            os.makedirs(file_path)
        logger.info("saving %s to local filesystem", file_path + filename)
        with open(file_path+filename, "wb") as file:
            file.write(content)

    def read_file(self, file_path, filename):
        """
        opens the file by filename
        """
        try:
            logger.info("reading %s from local filesystem", file_path + filename)
            target_file = os.path.join(file_path, filename)

            with open(target_file, "r") as file:
                return file
        except:
            logger.error(target_file + " not found.")

    def save_as_json(self, path, filename, json_doc):
        """takes a meta json and a target path
        uploads the file with utf-8 encoding to hdfs
        careful it overwrites the file if already present

        Args:
            meta_json (dict): meta json as a dictionary / json object
            target_path (dict): hdfs file path of target location
        """
        path = path[1:]
        logger.info("saving %s to local filesystem", path + filename)

        with open(path + filename, 'w') as file:
            json.dump(json_doc, file)

