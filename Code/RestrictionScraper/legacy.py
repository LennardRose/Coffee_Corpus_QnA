import requests
import re
import urllib
import ssl
import datefinder
import locale
import json
import os.path
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from elasticsearch import Elasticsearch
import pandas as pd
import pdfminer
import pdfminer.high_level
from Util import *

try:
    from PIL import Image
except ImportError:
    import Image

pytesseract.pytesseract.tesseract_cmd = 'E:/Programme/Tesseract/tesseract'
# plan for the scraper:
# future config will tell what exactly to scrape and what type
# scrape from every landesregierungs website
# if picture -> put into tesseract
# if pdf -> put into ocrmypdf // klappt wohl nicht -> https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/
# search text from picture or pdf
# put into json locally first

#logging.basicConfig(filename='RestrictionScraper.log', level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
ssl._create_default_https_context = ssl._create_unverified_context
#URL = "https://www.stmgp.bayern.de/coronavirus/"

attributes = ["validFrom", "incidenceBased", "federateState", "creationDate", "incidenceRanges", "tags"]
#tags = ["Maskenpflicht", "Kontaktbeschrankung", "Veranstaltungen", "Kultur", "Gastronomie", "Schule", "Sport"]


def getImgURLfromElem(elem):
    if "Regeln" in elem['alt'] or "Regelung" in elem['alt'] or not elem['alt'] or "Änderung" in elem['alt']:
        imgURL = elem['src']

        imgURL = fixURL(row.URL, imgURL)

        logging.info("Filtering found Img-Element %s", imgURL)
        return imgURL

    return None

def getPDFURLfromElem(elem):

    pdfURL = elem["href"]

    pdfURL = fixURL(row.URL, pdfURL)

    logging.info("Filtering found PDF %s", pdfURL)
    return pdfURL

def savePage(URL, directory):

    if not os.path.isdir(directory):
        os.makedirs(directory)

    response = urllib.request.urlopen(URL)
    webContent = response.read()
    fileName = directory + "page.html"

    #kwargs = {'bypass_robots': True, 'project_name': 'recognisable-name'}
    #save_webpage(URL, directory, **kwargs)

    open(fileName, 'wb').write(webContent)


def saveImagesFromPage(imgURLs, directory):

    #fileNames = [""] * len(imgURLs)
    txtData = ""

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for index, imgURL in enumerate(imgURLs, start=0):

        #clean url
        if not imgURL.find('?') < 1:
            imgURL = imgURL[:imgURL.find('?')]

        t, dataType = os.path.splitext(imgURL)

        image = 'image' + str(index+1)
        fileName = directory+image+dataType
        fileNameBG = directory + image + "BG" + dataType
        fileNameBW = directory + image + "BW" + dataType

        #TODO: save raw data to hadoop

        logging.info("downloading File %s", fileName)
        urllib.request.urlretrieve(imgURL, fileName)

        logging.info("converting %s into B&G",fileName)
        imgBG = Image.open(fileName).convert("L")
        imgBW = Image.open(fileName).convert("1", dither=Image.NONE)

        imgBG.save(fileNameBG)
        imgBW.save(fileNameBW)

        logging.info("extracting text from image")
        #data = pytesseract.image_to_string(Image.open(fileNames[index]), lang='deu')
        data = pytesseract.image_to_string(imgBW, lang='deu')

        #with open(fileNames[index] + ".txt", "w") as text_file:
        #   text_file.write(data)

        txtData += '\n' + data

    return txtData

def savePDFfromPage(pdfURLs, directory):

    fileNames = [""] * len(pdfURLs)
    txtData = ""

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for index, pdfURL in enumerate(pdfURLs, start=0):

        fileName = directory + pdfURL[pdfURL.rindex("/")+1:pdfURL.rindex(".")] + ".pdf"
        logging.info("downloading File %s", fileName)
        urllib.request.urlretrieve(pdfURL, fileName)

        with open(fileName, 'rb') as fin:
            data = pdfminer.high_level.extract_text(fin, codec='utf-8')
            #data = data.encode('utf-8').decode("utf-8")

        with open(fileName + ".txt", "w", encoding='utf-8') as text_file:
            text_file.write(data)

        txtData += '\n' + data

    return txtData

def checkForTags(restrictionData, data):
    for tag, keys in TAGS.items():
        for key in keys:
            if re.search(key, data, re.IGNORECASE):
            #if any(key in data for key in keys): #if any string from the list of keys is in data
                if restrictionData['tags'] is None:
                    restrictionData['tags'] = [tag]
                else:
                    if tag not in restrictionData['tags']:
                        restrictionData['tags'].append(tag)
            else:
                continue

def getInformationFromPDF(txtData):
    if txtData:
        for index, pdfFile in enumerate(pdfFiles, start=0):
            logging.info("analyzing Metadata for file %s", pdfFile)



            if index == 0:
                restrictionData['validFrom'] = extractDate(data).strftime("%d-%m-%Y")

            # get incidence ranges
            matches = re.finditer(INCIDENCE_REGEX, data, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                if match.group().startswith("unter"):
                    incidenceStep = "<"+match.group()[-2:]
                elif match.group()[0].isnumeric():
                    incidenceStep = match.group()[:2] + "-" + match.group()[-2:]
                elif "ber" in match.group():
                    incidenceStep = ">"+match.group()[-2:]


                if restrictionData["incidenceSteps"] is None:
                    restrictionData["incidenceSteps"] = [incidenceStep]
                else:
                    if incidenceStep not in restrictionData["incidenceSteps"]:
                        restrictionData["incidenceSteps"].append(incidenceStep)


            checkForTags(restrictionData, data, tags)


def getInformationFromData(txtData, restrictionData):

    if txtData:
        #for index, imgFile in enumerate(imgFiles, start=0):

        logging.info("analyzing Metadata...")

        restrictionData['validFrom'] = extractDate(txtData).strftime("%d-%m-%Y")

        incidenceRanges = extractIncidences(txtData)

        if incidenceRanges:
            restrictionData["incidenceRanges"] = incidenceRanges
            restrictionData["incidenceBased"] = True

        checkForTags(restrictionData, txtData)

def saveMetadata(es, restrictionData):
    # send metadata to elastic search
    fileName = directory+"data.json"
    with open(fileName, 'w') as outfile:
        logging.info("writing Metadata-JSON to File %s", fileName)
        json.dump(restrictionData, outfile)

    logging.info("writing Metadata-JSON to Elasticsearch")
    json_object = json.dumps(restrictionData)

    uid = restrictionData["federateState"] + restrictionData['validFrom']

    if not es.exists(index="restrictions", id=uid):
        es.index(index="restrictions", id=uid, body=json_object)


def findElements(URL,target,value):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'lxml')

    element = ""

    if target == 'Text':
        texts  = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts )
        element = element.join(t.strip() for t in visible_texts).strip()
        print(element)

    elif target == 'CSSselector':
        element = soup.select(value)

    else:
        kwargs = ""
        if "[" in value: # a list
            kwargs = ""
        else:
            kwargs = {
                target: value
            }
        element = soup.find_all(**kwargs)

    return element

if __name__ == '__main__':

    sources = pd.read_csv("urls.csv", sep=";")
    es = Elasticsearch()
    es.indices.create(index="restrictions", ignore=400)

    for index, row in sources.iterrows():

        logging.info("Starting scraping for %s with URL %s",row.State, row.URL)

        element = findElements(row.URL, row.Target, row.Value)

        if element:
            restrictionData = dict.fromkeys(attributes)
            restrictionData['federateState'] = str(row.State)
            restrictionData['creationDate'] = datetime.now().strftime("%d-%m-%Y")
            restrictionData['incidenceBased'] = False

            directory = "measures/" + restrictionData["federateState"] + "/" + datetime.now().strftime("%d-%m-%Y_%H-%M/")

            if element[0].name == "img": #-> multiple images
                imgURLs = [getImgURLfromElem(elem) for elem in element]
                imgURLs = [elem for elem in imgURLs if elem is not None] # Filters empty urls - guess not necessary anymore
                if imgURLs:
                    txtData = saveImagesFromPage(imgURLs, directory)
                    getInformationFromData(txtData, restrictionData)
                else:
                    logging.error("Couldn't find any images for URL %s", row.URL)

            elif element[0].name == "a": #-> PDF
                pdfURLs = [getPDFURLfromElem(elem) for elem in element]
                if pdfURLs:
                    txtData = savePDFfromPage(pdfURLs, directory)
                    getInformationFromData(txtData, restrictionData)
                else:
                    logging.error("Couldn't find any PDFs for URL %s", row.URL)

            elif element[0].name == 'div': #-> Text
                txtData = "".join(div.text.strip() for div in element)
                savePage(row.URL, directory)
                getInformationFromData(txtData, restrictionData)

            saveMetadata(es, restrictionData)
            logging.info("Scraping for Federate State %s done", restrictionData["federateState"])
        else:
            logging.error("nothing found for URL %s", row.URL)

    logging.info("Scraper finished")