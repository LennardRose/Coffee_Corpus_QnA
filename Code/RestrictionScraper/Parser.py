from bs4 import BeautifulSoup
from bs4.element import Comment
from Config import *
from Util import *
import requests
import time
import pdfminer.high_level
import io
import os
import urllib
import pytesseract

try:
    from PIL import Image
except ImportError:
    import Image
from Config import *
import logging
logger = logging.getLogger(loggerName)

class Parser:
    """
    Parses the relevant data from the given url with specified key/value pair
    """

    def __init__(self, hdfs_client, directory, url, target, value):
        """
        Constructor which creates an instance with an instance of the hdfs client, the directory to save it to, the url to scrape from and the target/value

        Args:
            hdfs_client (object): instance of the hdfs client
            directory (string): the current directory to save data to
            url (string): the url from where to scrape
            target (string): e.q. a CSSselector/class etc.
            value (string): the value for the target
        """
        self.hdfs_client = hdfs_client
        self.directory = directory
        self.baseUrl = url
        self.target = target
        self.val = value
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    def findElements(self):
        """
        Parses the website to BeautifulSoup and tries to find elements specified by Target/Value

        Args:
            elements (list): found elements - can be empty
        """

        page = requests.get(self.baseUrl)
        soup = BeautifulSoup(page.content, 'lxml')

        elements = ""

        if self.target == 'Text':
            #deprecated?
            texts = soup.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            elements = elements.join(t.strip() for t in visible_texts).strip()

        elif self.target == 'CSSselector':
            elements = soup.select(self.val)

        else:
            kwargs = {
                    self.target: self.val
                }
            elements = soup.find_all(**kwargs)

        return self.filterElements(elements)

    def tag_visible(self, element):
        """
        Filtering method - returns True/False if element is relevant text from webpage or not necessary html stuff

        (Grabs the text of the webpage in case a complete site needs to be downloaded: https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text)
        Args:
            result (boolean): True if element is relevant text
        """

        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def filterElements(self, elements):
        """
        Filtering the elements, if its an <img>-element it gets the img-URL and if its <a>-Tag it gets the refering URL (mostly image or pdf files)
        if the element is a div which indicates we are only interested in the plain text it does nothing

        Args:
            elements (list): list of the found elements from the page
            resultSet (list of tuple(fileType, url|element)): condensed list of the elements, reduced to their urls
        """

        resultSet = []
        for (index, element) in enumerate(elements, 0):
            if element.name == "img":
                val = "src"

            elif element.name == "a":
                val = "href"

            elif element.name == 'div':
                resultSet.extend([("Text",element)])
                continue
            else:
                logger.error("Unknown element found: %s", element)
                continue

            url = element[val]
            url = fixURL(self.baseUrl, url)
            if url:
                logger.info("Filtering found Element %s", url)
                resultSet.extend([("File", url)])

        return resultSet

    def parse(self):
        """
        Parses the site, tries to find the specified elements from it and parses their urls/texts to a text string and saves the files to hdfs

        Args:
            dataStr (string): condensed data from the page as a string for later analyzses
        """

        elements = self.findElements()
        if elements:
            dataStr = ""

            for type, element in elements:
                  dataStr += self.downloadAndConvertFiles(type, element)

            return dataStr

    def downloadAndConvertFiles(self, type, elem):
        """
        Downloads the files from the page and feeds tesseract/pdfminer with the files to convert it into text.
        if type is "Text" the whole page is downloaded and saved as html-file
        if type is "img" the images are downloaded, converted into Black&White to have better accuracy from tesseract at extracting the text from them
        if type is "pdf" the pdf file is downloaded and feed to pdfminer to extract the text from it

        Args:
            type (string): specifing the kind of element e.q. Text/File ->(img, pdf)
            elem (string): the actual element, if its Text its a div, else its a url to a file like pdf or image
            data (string): the data string of the current element
        """

        data = ""
        if type == "Text":
            data = '\n' + elem.text.strip()

            logger.info("downloading File %s", self.baseUrl)
            response = urllib.request.urlopen(self.baseUrl)
            webContent = response.read()

            self.hdfs_client.save_as_file(self.directory, str(time.time())+_+DEFAULT_HTML_FILENAME, webContent)
        else:
            url = elem

            # clean url from parameters and stuff
            if not url.find('?') < 1:
                cleanedUrl = url[:url.find('?')]
            else:
                cleanedUrl = url

            path, dataType = os.path.splitext(cleanedUrl)
            if not dataType:
                dataType = dataType[:-1] + ".pdf"
                url = url + dataType

            fileName = url[url.rindex("/") + 1:url.rindex(".")] + dataType
            fullFilePath = self.directory + fileName

            if dataType == ".pdf":
                logger.info("downloading File %s", url)

                fileBytes = requests.get(url).content

                logger.info("extracting text from pdf..")
                data = '\n' + pdfminer.high_level.extract_text(io.BytesIO(fileBytes), codec="utf-8")

                self.hdfs_client.save_as_file(self.directory, fileName, fileBytes)

            else:


                #fileNameBG = fileName[:fileName.rindex(".")] + "BG" + dataType
                fileNameBW = fileName[:fileName.rindex(".")] + "BW" + dataType

                logger.info("downloading File %s", cleanedUrl)
                imgBytes = requests.get(cleanedUrl).content
                image = Image.open(io.BytesIO(imgBytes))

                logger.info("converting %s into B&G", fileName)
                imgBW = image.convert("1", dither=Image.NONE)

                # converting the generated B&W image to bytes to save it
                buf = io.BytesIO()
                if dataType == ".png":
                    imgBW.save(buf, format="png")
                else:
                    imgBW.save(buf, format="jpeg")
                imgBWbytes = buf.getvalue()

                self.hdfs_client.save_as_file(self.directory, fileNameBW, imgBWbytes)
                self.hdfs_client.save_as_file(self.directory, fileName, imgBytes)

                logger.info("extracting text from image..")
                data = '\n' + pytesseract.image_to_string(imgBW, lang='deu')

        return data