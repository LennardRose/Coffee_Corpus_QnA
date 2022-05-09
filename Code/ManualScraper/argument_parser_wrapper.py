#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
import client_factory
import argparse
import sys


class ArgumentParserWrapper: # clap the sillables like a 3 year old
    """
    wraps the argumentparser of argparse
    retrieves data to scrape based on args
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='scrapes sources by the configs given')

    def _parse_arguments(self):
        """
        parses the arguments
        """

        self.parser.add_argument("-c", "--articleclient", action="append", dest="articleclient_ids", default=[],
                            help="config stored in articleclient, add id of the config")

        self.parser.add_argument("-f", "--file", action="append", dest="filenames", default=[],
                            help="config stored in file, add filename")

        return self.parser.parse_args()

        

    def parse_data_from_arguments(self):
        """
        retrieves the article_configs mentioned in the arguments
        if no arguments are given, retrieves all article_configs 
        :return: list with all matching article_configs
        """

        args = self._parse_arguments()
        data = []

        if len(sys.argv) < 2: #programmname ist auch ein argument, deshalb 2 ---> scrape alle in articleclient wenn nichts weiter angegeben
            data = client_factory.get_article_client().get_all_article_configs()

        for filename in args.filenames:
            data.append(client_factory.get_file_client().read_file(filename))
                
        for id in args.articleclient_ids:
            data.append(client_factory.get_article_client().get_article_config(id))

        data = list(filter(None, data)) # filter the none values for missing values

        return data