#####################################################################
#                                                                   #
#                     Lennard Rose 5122737                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2022                                  #
#                                                                   #
#####################################################################
import os
from argument_parser_wrapper import ArgumentParserWrapper
from manual_scraper import ManualScraper
import logging
import utils

if __name__ == '__main__':

    config_path = os.path.join("..", "config", "config.json")

    utils.init_global_config(config_path)
    logging.basicConfig(filename=utils.config["STANDARD_LOG_FILENAME"],
                        format=utils.config["STANDARD_LOG_FORMAT"],
                        datefmt=utils.config["STANDARD_LOG_DATE_FORMAT"],
                        level=logging.INFO)

    logging.info("Start ManualScraper")

    scraper = ManualScraper()
    parser = ArgumentParserWrapper()

    for source in parser.parse_data_from_arguments():
        scraper.scrape(source)

    logging.info("Close ManualScraper")
