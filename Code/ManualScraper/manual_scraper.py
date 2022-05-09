#####################################################################
#                                                                   #
#                     Lennard Rose 5122737                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2022                                  #
#                                                                   #
#####################################################################
import utils
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
import re
import html5lib
from meta_parser import meta_parser
import client_factory
import logging
import ssl
import os
from queue import Queue


class ManualScraper:

    def __init__(self):
        self.manual_config = None
        ssl._create_default_https_context = ssl._create_unverified_context
        self.driver = self._get_webdriver()


    def _get_webdriver(self):
        """
        returns a webdriver for selenium
        expects you to have the file in a directory named after your os (linux / windows / if you use mac, go buy linux)
        https://www.makeuseof.com/how-to-install-selenium-webdriver-on-any-computer-with-python/
        """
        try:
            path = None
            driver_options = Options()
            driver_options.headless = True

            if os.name == 'posix':
                path = os.path.join(utils.config["WEBDRIVER_DIR"], "linux", utils.config["WEBDRIVER_FILE"])
                return webdriver.Chrome(path, options=driver_options)
            else:
                path = os.path.join(utils.config["WEBDRIVER_DIR"], "windows", utils.config["WEBDRIVER_FILE"])
                return webdriver.Chrome(executable_path=path, options=driver_options)

        except Exception as e:
            logging.error("failed to initialize webdriver for selenium, /"
                          "make sure you downloaded a driver and wrote the correct path to config, current path: " + path)
            logging.error(e)


    def scrape(self, manual_config):
        """
        makes sure necessary properties are set in the manual_config
        """
        self.manual_config = manual_config

        if manual_config["base_url"] == None:
            logging.error("Missing url information to scrape from manual_config")

        else:
            logging.info("Start scraping from manuals source URL: %s", manual_config["base_url"])

            links = Queue()
            map(links.put, manual_config["paths"])

            # TODO Hier muss noch iteriervorgang hin
            map(links.put, self._get_layer_links(links.get(block=False)))

            self._save_manuals(links)

        self.manual_config = None


    def _save_manuals(self, URLs):
        """
        retrieves content of the article page
        parses meta information
        saves all data
        """
        for URL in URLs:
            try:
                logging.info("Save content of: " + URL)

                for element in self._get_link_list(URL,
                                                   html_tag=self.manual_config["pdf"]["html_tag"],
                                                   html_class=self.manual_config["pdf"]["html_class"],
                                                   css_selector=self.manual_config["pdf"]["css_selector"]):
                    # save element
                    continue

                names = ""
                productName = ""

            except Exception as e:
                logging.error("Something went wrong while trying to save: " + URL)
                logging.error(e)


    def _get_meta_data(self, URL, soup):
        """
            initializes meta_parser with necessary information, parses metadata and returns it
            :param URL: the url to get the metadata of
            :param soup: the soup of the url
            :return: the meta_data of the urls article
            """
        parser = meta_parser(URL, soup)
        parser.parse_metadata()  # das URL ist von der individuellen seite, nicht aus Base + Path
        return parser.get_article_meta_data()


    def _save(self, manual_meta_data, content):
        """
        saves the html source of the given URL 
        also saves the meta data of the page
        only saved the content if meta_data was successfully indexed, if content saving raises an exception, deletes created meta_data
        :param manual_meta_data: the meta data to save
        :param content: the page content to save
        """
        id = None
        try:
            id = client_factory.get_meta_client().index_meta_data(manual_meta_data)
            logging.info("Success -- Saved Metadata")

        except Exception as e:
            logging.error("failed to save Metadata with meta_client")
            logging.error(e)

        if id:
            try:
                client_factory.get_file_client().save_as_file(manual_meta_data["filepath"],
                                                              manual_meta_data["filename"], content)
                logging.info("Success -- Saved content")

            except Exception as e:
                logging.error("failed to save Content with file_client")
                logging.error(e)
                client_factory.get_meta_client().delete_meta_data(id)


    def _get_layer_links(self, path):
        """
        creates a list with the links to all articles from the given manual_config
        also completes every relative URL with the base_url if necessary
        checks every link if it matches the given conditions in the manual_config
        checks if there is not already an entry in the manual_meta_data index
        :param manual_config: the manual_config of the sources page to get die article links of
        :return: a list with all valid links of the page
        """

        links = []

        if self._is_relative_URL(path):
            source_URL = self.manual_config["base_url"] + path
        else:
            source_URL = path

        most_recent_saved_articles_url = client_factory.get_meta_client().get_latest_entry_URL(source_URL,
                                                                                               self.manual_config[
                                                                                                   "manufacturer_name"])

        for link in self._get_link_list(source_URL, layer["html_tag"], layer["html_class"]):

            if self._is_valid(link, self.manual_config["url_conditions"]):

                if self._is_relative_URL(link):
                    link = self.manual_config["base_url"] + link

                if not self._was_already_saved(most_recent_saved_articles_url, link):
                    links.append(link)

        links.reverse()  # important to have the newest article at the last index of the list, so it has the newest indexing time, making it easier (if not possible) to search for without having to write an overcomplicated algorithm

        return links


    def _get_link_list(self, URL, html_tag=None, html_class=None, css_selector=None):
        """
        collects all links from the specified URL that fits the html_tag html_class combination
        If no href is found, the children will be searched for a href
        """

        link_list = []

        for link in self._get_tag_list(URL, html_tag, html_class, css_selector):

            if link.has_attr('href'):
                link_list.append(link['href'])

            else:
                link = self._search_direct_children_for_href(link)

                if link != None:
                    link_list.append(link)

        return link_list


    def _get_tag_list(self, URL, html_tag=None, html_class=None, css_selector=None):
        """
        collects all tags that match html_tag and html_class
        """

        tag_list = []

        # first try static page
        soup = self._get_soup_of_static_page(URL)

        if soup:
            if html_tag:
                tag_list = soup.body.find_all(html_tag, html_class)
            elif css_selector:
                tag_list = soup.bofy.select(css_selector)

        # if static doesnt work try dynamic
        if tag_list == []:
            soup = self._get_soup_of_dynamic_page(URL)
            if soup:
                if html_tag:
                    tag_list = soup.body.find_all(html_tag, html_class)
                elif css_selector:
                    tag_list = soup.bofy.select(css_selector)

        # if still no result something must be wrong with the html_tag and html_class
        if tag_list == []:
            logging.error("No results found for: " + html_class + " and " + html_tag)

        return tag_list


    def _get_soup(self, URL):
        """
        return soup by trying first to get it as a static page, after failure tries as a dynamic page
        :params URL: the url
        """
        soup = self._get_soup_of_static_page(URL)

        if soup == None:
            soup = self._get_soup_of_dynamic_page(URL)

        return soup


    def _get_soup_of_static_page(self, URL):
        """
        extract content of static loaded page
        does some retries
        :param URL: the url to get the soup (Beatifulsoup) of
        :return: the soup, parsed with 'html5lib' parser
        """
        page = None
        retry_count = 0
        while page == None and retry_count < int(utils.config["MAX_TRY"]):
            try:
                retry_count += 1
                page = requests.get(URL, timeout=5)
            except Exception as e:
                logging.warning("request unable to get: %s - retries left: %d", URL,
                                int(utils.config["MAX_TRY"]) - retry_count)
                logging.warning(e)
        return BeautifulSoup(page.content, 'html5lib')


    def _get_soup_of_dynamic_page(self, URL):
        """
        extract content of dynamic loaded page
        does some retries
        :param URL: the url to get the soup (Beatifulsoup) of
        :return: the soup, parsed with 'html5lib' parser
        """
        page = None
        retry_count = 0
        while page == None and retry_count < int(utils.config["MAX_TRY"]):
            try:
                retry_count += 1
                self.driver.get(URL)
                time.sleep(1)  # load page
            except Exception as e:
                logging.warning("selenium unable to get: %s - retries left: %d", URL,
                                int(utils.config["MAX_TRY"]) - retry_count)
                logging.warning(e)
        return BeautifulSoup(self.driver.page_source, 'html5lib')


    def _search_direct_children_for_href(self, tag):
        """
        searches all children of a tag for a href, returns the first
        """
        for child in tag.findAll(recursive=True):
            if child.has_attr('href'):
                return child['href']
        else:
            return None


    def _was_already_saved(self, most_recent_saved_articles_URLs, current_URL):
        """
        the first link in the list returned by the page is not always the most recent
        :param most_recent_saved_articles_url: the URLs of the most recent saved articles (in an earlier call)
        :param URL: the url of the current link
        :return: true if the URL matches one url in the most recent urls
        """
        if most_recent_saved_articles_URLs:
            return current_URL in most_recent_saved_articles_URLs
        else:
            return False


    def _is_relative_URL(self, URL):
        """
        checks if the given URL starts with http, to determine if it is a relative URL
        lots of webpages return only the path url on their own website
        :param URL: the URL to check
        :return: false if URL starts with http, otherwise true
        """
        return not bool(re.search("^http", URL))


    def _is_valid(self, URL, conditions):
        """
        checks if the given URL matches the given conditions, returns wether the url should be included in the list based on the include_condition value
        necessary because a lot of websites got fake articles with ads or have their interesting articles under a similar url path, 
        :param URL: the url to check
        :param conditions: list with the strings to match in the url
        :param include_condition: true if matches of the url should be included, false if matches should be excluded
        :return: true if url includes condition NXOR include_condition set true, else false 
        """
        valid = True

        if conditions != None and conditions != []:

            for condition in conditions:

                is_included = bool(
                    re.search(condition["condition_string"], URL))  # if the condition_string is part of the URL

                if condition["include_condition"]:  # if the condition_string should be included in the URL
                    if is_included:
                        valid = valid
                    else:
                        valid = False

                else:  # if the condition_string should not be included in the URL
                    if is_included:
                        valid = False
                    else:
                        valid = valid

        return valid
