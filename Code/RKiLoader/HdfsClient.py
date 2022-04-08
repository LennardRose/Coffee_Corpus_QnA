import logging
from pywebhdfs.webhdfs import PyWebHdfsClient
import re
import json
import time
from Config import *
from ElasticSearchWrapper import ElasticSearchClient


class HdfsClient():
    """HDFS Helper class
    """

    def __init__(self) -> None:
        """init function that creates an insecure hdfs client
        """
        self.hdfs_client = PyWebHdfsClient(
            host=hdfs_base_url, port=hdfs_port, user_name='hadoop')
        #self.test_hdfs_connection()

    def test_hdfs_connection(self):
        """Testing the hdfs connection by trying to list items in the root directory

        Raises:
            IOError: Raises an Error when connection is offline
        """
        logging.info('Testing HDFS connection')
        try:
            self.hdfs_client.list_dir('/')
        except Exception:
            logging.error('No HDFS connection')
            raise IOError

    def read_json_from_hdfs(self, file_path):
        """reads a json file from the given path and converts it into an dictionary using json python lib

        Args:
            file_path (string): the hdfs path to the json file you want to read

        Returns:
            json: the json document as a dict/ json object
        """
        return json.loads(self.hdfs_client.read_file(file_path))

    def get_json_files_from_directory(self, directory):
        """get all meta jsons in a hdfs directory matching the internal regex pattern
        which filters all files that don't end with meta.json

        Args:
            directory (string): the hdfs directory you want to check

        Returns:
            list: list of all meta jsons in specified hdfs directory
        """
        file_names = self.hdfs_client.list_dir(
            directory)['FileStatuses']['FileStatus']
        file_list = []
        for file_name in file_names:
            file_list.append(file_name['pathSuffix'])
        file_list = list(
            filter(lambda x: x.endswith(".json"), file_list))
        return file_list

    def save_json_to_hdfs(self, json_doc, target_path):
        """takes a meta json and a target path
        uploads the file with utf-8 encoding to hdfs
        careful it overwrites the file if already present

        Args:
            meta_json (dict): meta json as a dictionary / json object
            target_path (dict): hdfs file path of target location
        """
        self.hdfs_client.create_file(
            target_path, json.dumps(json_doc), overwrite=True)

    def append_dict_to_json(self, file_path, additional_dictionary, override_existing):
        """Append a dictionary to a json in hdfs

        Args:
            file_path (string): hdfs path to the json
            additional_dictionary (dict): dictionary you want to add to your current json
            override_existing (boolean): override existing items in
        """
        meta_json = self.read_json_from_hdfs(file_path)
        meta_json = self.append_dict_to_dict(
            meta_json, additional_dictionary, override_existing)
        self.save_json_to_hdfs(meta_json, file_path)

    def append_dict_to_dict(self, dict_base, dict_addition, override_existing):
        """append a dictionary to another dictionary item by item, overrides existing when specified

        Args:
            dict_base (dict): base dictionary
            dict_addition (dict): dictionary to be added
            override_existing (bool): whether to override items in the base dict or not

        Returns:
            dict: the combined dictionary
        """
        result_dict = dict_base
        for item, value in dict_addition.items():
            if item not in dict_base.keys() or override_existing:
                result_dict[item] = value
        return result_dict

    def save_file_to_hdfs(self, file, file_name, path):
        with open('requirements.txt', 'r') as file:
            self.hdfs_client.create_file(
                file_data=file, path=file+'/'+file_name)
