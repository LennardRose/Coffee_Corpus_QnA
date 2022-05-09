#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
import json
import os
import utils
import logging

class meta_parser:
    """
    parses meta data from given soup based on the specifications in the manual_config

    """

    def __init__(self, URL, soup, article_config):
        """
        initializes values as class values to be able to accesss them from anywhere, readable
        """

        self.article_config = article_config
        self.soup = soup
        self.article_meta_data = { "title" : None, 
            "description" : None, 
            "url": URL,  #wird direkt übergeben um sie nicht nochmal auslesen zu müssen
            "source_url" : article_config["base_url"] + article_config["path_url"],  #wird gebraucht um später doppelte ergebnisse zu vermeiden und um bei mehreren scrapern pro website verwechslungen zu vermeiden
            "type" : None, 
            "date" : None, 
            "index_time" : utils.date_now(),  #wichtig mit millisekunden
            "region" : article_config["region"], 
            "site_name" : article_config["site_name"], 
            "author" : None, 
            "keywords" : None,
            "filename" : "placeholder_to_prevent_iteration",
            "filepath" : "placeholder_to_prevent_iteration"}



    def get_article_meta_data(self):
        """
        returns the manual_meta_data
        """
        return self.article_meta_data



    def parse_metadata(self):
        """
        chooses a parsing strategy for every meta attribute based on the given source set in the manual_config to set the value
        sets the filename
        """
        for key in self.article_meta_data.keys():

            if self.article_meta_data[key] == None:

                if self.article_config[key]["source"] == "NOEXIST":
                    self._set_noexist(key)

                elif self.article_config[key]["source"] == "DEFAULT":
                    self._set_default(key)

                elif self.article_config[key]["source"] == "TAG":
                    self._parse_from_tag(key)

                elif self.article_config[key]["source"] == "JSON_LD":
                    self._parse_from_json(key)

                else:
                    logging.error("No meta-config found for: " + (str(self.article_meta_data[key]) if self.article_meta_data[key] else " <not found>") + 
                    ", config was: " + (str(self.article_config[key]) if self.article_config[key] else " <not found>"))

        self._set_files_name_and_path()


    def _set_files_name_and_path(self):
        """
        sets the filename by appending the region, sites name, the title and .txt
        sets the files path by appending "datakraken", "articles", the region, sites name and the current date in the os manner
        """
        self.article_meta_data["filename"] = self.article_config["region"] + "_" + self.article_config["site_name"] + "_" + utils.slugify(self.article_meta_data["title"]) + ".txt"
        self.article_meta_data["filepath"] =os.path.join("datakraken", "articles", self.article_config["region"], self.article_config["site_name"], utils.date_today())

    def _set_noexist(self, key):
        if  key == "title" or key == "date":
            logging.error("Forbidden attribute value NOEXIST for "+ key +" meta data.")
        
        self.article_meta_data[key] = "-" #überlegen welches freizeichen 



    def _set_default(self, key):
        """
        set the keys default value
        error if the key is title, title must be unique for filename
        default date is the current date
        every other key is set from meta_configs default value
        """
        if self.article_config[key]["default"] == None or self.article_config[key]["default"] == "":
            logging.warning("No default-value set for %s", key)
            self.article_meta_data[key]["-"]

        if key == "title":
            logging.error("Forbidden attribute value DEFAULT for title meta data.")

        elif key == "date":
            self.article_meta_data[key] = utils.date_now()

        else:
            self.article_meta_data[key] = self.article_config[key]["default"]


    def _parse_from_tag(self, key):
        """
        parses meta value from any given tag/attribute/attribute_value combination
        takes care of right format
        """
        
        tag = self.soup.find(self.article_config[key]["tag"], { self.article_config[key]["attribute"] : self.article_config[key]["attribute_value"]})

        if tag:

            if key == "date":
                self.article_meta_data[key] = utils.parse_date(self._get_content(tag))

            else:
                self.article_meta_data[key] = self._get_content(tag)



    def _get_content(self, tag):
        """
        get content of given tag, if tag has some nested tags inside of which one is holding the content, it returns the first content
        example:
        right result will be returned: <div><span><a>right</a></span></div> 
        wrong result will be returned: <div><span>wrong<a>right</a></span></div>
        """
        if tag.is_empty_element and tag.get("content", None) != None and tag.get("content", None) != "":
            return tag.get("content", None)
        elif not tag.is_empty_element:
            return tag.text
        else:
            for child in tag.descendants:
                return self._get_content(child) # rekursiv 

        logging.error("No content in tag: " + tag.get("name", None) if tag else "<tag not found>" + " found.")

        

    def _parse_from_json(self, key):
        """
        uses the <script type=application/ld+json> to retrieve meta information
        even thoug script is the tag, type the attribute and application/... the attribute value, 
        we will use the tag property of the article_meta_config as the json-key, the attribute and attribute_value
        porperty to choose wich application/ld+json tag to use if there are multiple
        retrieves all ld+json scripts on the page and iterates through all for the needed value
        """
        if self.article_config[key]["attribute"] == None and self.article_config[key]["attribute_value"] == None:
            result_set = self.soup.find_all('script', {'type':'application/ld+json'}) 
        else:
            result_set = self.soup.find_all('script', {'type':'application/ld+json', self.article_config[key]["attribute"] : self.article_config[key]["attribute_value"]}) 

        if result_set: #result_json from soup.findall is a list
            result_jsons = []

            for element in result_set:

                element = element.text.strip()
                result_jsons.append(json.loads( element ))

            if result_jsons: # find_all returns a list

                for result_json in result_jsons: #json+ld script may consist of other scripts

                    if type(result_json) is list: #check ob json liste

                        for element in result_json:
                            self._get_json_value(element, key)

                    else: 
                        self._get_json_value(result_json, key)
        


    def _get_json_value(self, json, key):
        """
        set the meta_data of the given key if the json-key is in the given script
        if the value for the key is a list, appends all the "name" values in the list to resultstring
        """

        if self.article_config[key]["tag"] in json:

            content = json[self.article_config[key]["tag"]]
            result = ""

            if type(content) is list:
                for element in content:
                    if "name" in element:
                        result += (str(element["name"]) + " ")

            elif type(content) is dict:
                result = content["name"]

            else: 
                result = content

            if key == "date":
                self.article_meta_data[key] = utils.parse_date(result)

            else:
                self.article_meta_data[key] = result 





