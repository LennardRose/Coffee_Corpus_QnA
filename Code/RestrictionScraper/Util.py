import re
import locale
from Config import *
from datetime import datetime
import logging
logger = logging.getLogger(loggerName)

def extractDate(data):
    match = re.search(OTHER_DATE_REGEX, data, re.IGNORECASE)
    if not match:
        match = re.search(DATE_REGEX, data, re.IGNORECASE)
    if match:
        beginDateStr = match.group()
        beginDateStr = beginDateStr.rstrip()

        # date has chars infront
        if re.search(r"\d", beginDateStr).start() > 0:
            index = re.search(r"\d", beginDateStr).start()
            beginDateStr = beginDateStr[index:]

        # date has chars behind
        if 0 < re.search(FIND_ANY_NON_LETTER_DIGIT, beginDateStr).start() < len(beginDateStr):
            index = re.search(FIND_ANY_NON_LETTER_DIGIT, beginDateStr).start()
            beginDateStr = beginDateStr[:index]

        if any(c.isalpha() for c in beginDateStr) and not beginDateStr[-1].isnumeric():
            now = datetime.now()
            beginDateStr += " " + str(now.year)
        locale.setlocale(locale.LC_ALL, "german")
        try:
            return datetime.strptime(beginDateStr, '%d. %B %Y')
        except:
            try:
                return datetime.strptime(beginDateStr, '%d.%m.%Y')
            except:
                logger.error("date conversion failed")

    logger.error("No ValidFrom Date found...")

def fixURL(baseURL, fileURL):
    url = fileURL
    index = re.search(FIND_DOMAIN, baseURL).start() + 1
    if not fileURL.startswith(baseURL[:index]):
        url = baseURL[:index] + fileURL
    return url

def extractIncidences(data):

    incidenceRanges = []

    matches = re.finditer(OTHER_INCIDENCE_REGEX, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if not match.group(3) in incidenceRanges:
            incidenceRanges.append(match.group(3))

    incidenceRanges.sort()

    return incidenceRanges