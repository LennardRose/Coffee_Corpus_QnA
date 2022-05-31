#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
import os
import utils
from pywebhdfs.webhdfs import PyWebHdfsClient
from abstract_client import FileClient
import json
import logging


class HDFSClient(FileClient):
    """
    HDFS Helper class
    """

    def __init__(self):
        """
        init function that creates an insecure hdfs client
        """
        logging.info("Init HDFS client with url: %s : %s", utils.config["HDFS_URL"] , utils.config["HDFS_PORT"])
        self.hdfs_client = PyWebHdfsClient(host=utils.config["HDFS_URL"], port=utils.config["HDFS_PORT"], user_name=utils.config["HDFS_USER"], timeout=1)

    def read_file(self, file_path, filename):
        """
        reads a file from the given file_path filename combination and returns it as json
        :param file_path: the path the file, no filename here
        :param filename: the name of the file to read
        :return: json presentation of the files content
        """
        target_file = os.path.join(file_path, filename)
        return json.loads(self.hdfs_client.read_file(target_file))

    def save_as_file(self, file_path, filename, content):
        """
        combines the file_path and filename to the location to save the content
        raises error if save was not successfull
        careful it overwrites the file if already present
        :param file_path: the path the file will be saved to, no filename here
        :param filename: the name of the file that will be saved
        :param content: the content that will be saved in the file
        :return: nothing
        """
    
        target_file_path = os.path.join(file_path, filename)
        success = self.hdfs_client.create_file(target_file_path, content, overwrite=True)

        if not success:
            raise Exception("failed to save content as file to hdfs")



class MOCKHDFSClient(FileClient):
    """
    mock of hdfs, saves to local file system
    """

    def save_as_file(self, file_path, filename, content):
        """
        saves the content with a given filename as a file
        """
        file_path = "./manuals/" + file_path
        os.makedirs(file_path, exist_ok=True)
        target = os.path.join(file_path, filename)

        with open(target, "wb") as file:
                file.write(content)


    def read_file(self, filename, file_path=""):
        """
        opens the file by filename
        """
        try:
            
            target_file = os.path.join(file_path, filename)

            with open(target_file, "r") as file:
                return json.load(file)
        except:
            logging.error(target_file + " not found.")
