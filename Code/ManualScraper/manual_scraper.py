#####################################################################
#                                                                   #
#                     Lennard Rose 5122737                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2022                                  #
#                                                                   #
#####################################################################
from typing import List



import utils
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
import re
import html5lib
import client_factory
import logging
import ssl
import os
from tqdm import tqdm


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

        if manual_config["base_url"] is None:
            logging.error("Missing url information to scrape from manual_config")

        else:
            logging.info("Start scraping from manuals source URL: %s", manual_config["base_url"])

            links = []
            links.append(manual_config["paths"])

            # add a queue for every layer as well as one for the end
            for _ in range(0, len(manual_config["layers"])):
                links.append([])

            # for each i, try the current layer to get new links, try these again with the current layer, if they stop
            # yielding results, put them to the next i
            # do not iterate over the last i
            for i in tqdm(range(0, len(links) - 1), desc="query linktree for pdfs"):
                while links[i]:
                    old_link = links[i].pop(0)
                    new_links = []
                    new_links.extend(self._get_layer_links(old_link, manual_config["layers"][i]))
                    # if the old link yielded new results append them and remove the old link (popped above)
                    if new_links:
                        links[i].extend(new_links)
                    # if the link does not yielded results, try in the next iteration with the next layer
                    else:
                        # to the next layer, ultimatively the last one gets filled only with "product pages" or
                        # the destination link on which the manuals are
                        links[i + 1].append(old_link)

            self._save_manuals(links[-1])

        # clear manual config for next one
        self.manual_config = None


    def _save_manuals(self, URLs):
        """
        retrieves manuals from the product pages
        parses meta information
        saves all data
        :param URLs: An iterable with all the product pages URLs
        """
        for URL in tqdm(URLs, desc="pdfs saved"):
            try:
                # all the different manuals
                manual_links = self._get_layer_links(URL, self.manual_config["pdf"])
                for i, manual_link in enumerate(manual_links):
                    most_recent_saved_articles_url = client_factory.get_meta_client().get_latest_entry_URL(manual_link,
                                                                                                           self.manual_config[
                                                                                                               "manufacturer_name"])

                    if not self._was_already_saved(most_recent_saved_articles_url, URL):
                        # save element
                        logging.info("Save content of: " + manual_link)

                        meta_data = self._get_meta_data(URL, manual_link, i)
                        fileBytes = self._get_pdf_bytes(manual_link)

                        self._save(meta_data, fileBytes)

            except Exception as e:
                logging.error("Something went wrong while trying to save: " + URL)
                logging.error(e)


    def _get_meta_data(self, URL, manual_link, number):
        """ TODO
            initializes meta_parser with necessary information, parses metadata and returns it
            :param URL: the url to get the metadata of
            :param soup: the soup of the url
            :return: the meta_data of the urls article
        """
        meta_data = {}
        soup = self._get_soup(URL)

        meta_data["manufacturer_name"] = self.manual_config["manufacturer_name"]
        meta_data["product_name"] = utils.slugify(soup.select(self.manual_config["meta"]["product_name"])[0].text)
        meta_data["manual_name"] = utils.slugify(soup.select(self.manual_config["meta"]["manual_name"])[number].text) #TODO gucken obs hier bricht
        meta_data["filepath"] = str(meta_data["manufacturer_name"] + "/" + meta_data["product_name"] + "/")
        meta_data["filename"] = str(meta_data["product_name"] + "_" + meta_data["manual_name"] + ".pdf")
        meta_data["language"] = None #TODO
        meta_data["URL"] = manual_link
        meta_data["index_time"] = utils.date_now()

        return meta_data


    def _save(self, manual_meta_data, content):
        """
        saves the source pdf of the given URL
        also saves the meta data of the product
        only saved the content if meta_data was successfully indexed, if content saving raises an exception, deletes created meta_data
        :param manual_meta_data: the meta data to save
        :param content: the pdf to save
        """
        current_id = None
        try:
            current_id = client_factory.get_meta_client().index_meta_data(manual_meta_data)
            logging.info("Success -- Saved Metadata")

        except Exception as e:
            logging.error("failed to save Metadata with meta_client")
            logging.error(e)

        if current_id:
            try:
                client_factory.get_file_client().save_as_file(manual_meta_data["filepath"],
                                                              manual_meta_data["filename"],
                                                              content)
                logging.info("Success -- Saved content")

            except Exception as e:
                logging.error("failed to save Content with file_client")
                logging.error(e)
                client_factory.get_meta_client().delete_meta_data(current_id)


    def _get_layer_links(self, path, layer):
        """
        creates a list with the links on the path with respect to the constraints of the given layer
        also completes every relative URL with the base_url if necessary
        checks every link if it matches the given conditions in the filter
        :param path: the path of the source, may be just the URL path or a complete URL
        :return: a list with all valid links on the page
        """

        links = []

        # has to be here for the first paths, may come up with a clever soulution ... or not
        if self._is_relative_URL(path):
            source_URL = self.manual_config["base_url"] + path
        else:
            source_URL = path

        for link in self._get_link_list(URL=source_URL,
                                        html_tag=layer["html_tag"],
                                        html_class=layer["html_class"],
                                        css_selector=layer["css_selector"]):

            if self._is_valid(link, layer["filter"]):

                if self._is_relative_URL(link):
                    link = self.manual_config["base_url"] + link

                links.append(link)

        links.reverse()  # important to have the newest link at the last index of the list, so it has the newest indexing time, making it easier (if not possible) to search for without having to write an overcomplicated algorithm

        return links


    def _get_link_list(self, URL, html_tag=None, html_class=None, css_selector=None):
        """
        collects all links from the specified URL that fits the html_tag html_class combination or the css_selector
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
        collects all tags that match html_tag and html_class or css_selector
        tries to do so by treating the page as static, if fails as dynamic page
        """

        tag_list = []

        # first try static page
        soup = self._get_soup_of_static_page(URL)

        if soup:
            if html_tag:
                tag_list = soup.body.find_all(html_tag, html_class)
            elif css_selector:
                tag_list = soup.body.select(css_selector)

        # if static doesnt work try dynamic
        if not tag_list:
            soup = self._get_soup_of_dynamic_page(URL)
            if soup:
                if html_tag:
                    tag_list = soup.body.find_all(html_tag, html_class)
                elif css_selector:
                    tag_list = soup.body.select(css_selector)

        # if still no result something must be wrong with the html_tag and html_class
        if not tag_list:
            logging.error("No results found for html_class: " + html_class
                          + ", html_tag: " + html_tag
                          + ", css_selector: " + css_selector)

        return tag_list


    def _get_pdf_bytes(self, URL):
        return requests.get(URL).content


    def _get_soup(self, URL):
        """
        return soup by trying first to get it as a static page, after failure tries as a dynamic page
        :params URL: the url
        """
        soup = self._get_soup_of_static_page(URL)

        if soup is None:
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
        if page:
            return BeautifulSoup(page.content, 'html5lib')
        else:
            return None


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
        if page:
            return BeautifulSoup(self.driver.page_source, 'html5lib')
        else:
            return None


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
        :param URL: the url to check
        :param conditions: list with the condition_string and include_condition combination to match in the url
        :return: true if url includes condition NXOR include_condition set true, else false 
        """
        valid = True

        if conditions is not None and conditions != []:

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
