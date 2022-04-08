# -------------------------------hdfs---------------------------------------------------
HDFS_BASE_URL = '127.0.0.1'
HDFS_PORT = '50070'
HDFS_USER = 'hadoop'
HDFS_MEASURES_BASE_PATH = '/datakraken/measures/'
# -------------------------------TESSERACT------------------------------------------
TESSERACT_PATH = "E:/Programme/Tesseract/tesseract"
# -------------------------------misc------------------------------------------
DEFAULT_HTML_FILENAME = "page.html"
TAGS = {
    "Maskenpflicht" : ["Maskenpflicht", "Maske"],
    "Kontaktbeschränkung" : ["Kontaktbeschränkung", "Kontaktbeschrankung"],
    "Veranstaltungen" : ["Events", "Veranstaltungen"],
    "Kultur" : ["Kultur"],
    "Gastronomie" : ["Gastronomie"],
    "Schule" : ["Schule", "Kindergarten"],
    "Sport" : ["Sport", "Fitnessstudios"]
}
# regex to find Any character that is NOT a letter or number from behind - example: 21.04.2021) <-
FIND_ANY_NON_LETTER_DIGIT = r"[^a-zA-Z0-9]*$"
# finding first / in an url for the domain
FIND_DOMAIN = r"(?<=[a-zA-Z])/{1}"
# https://regex101.com/r/2BXdcV/1
DATE_REGEX = r"([1-3]?[0-9][.]([ ](Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([ ]202[0-9])?|[0-1]?[0-9][.]?(202[0-9])?))\D"
# https://regex101.com/r/TyQzsm/1
OTHER_DATE_REGEX = r"(ab |vom |, |Stand(:)? |am |seit(:)? ){1}[1-3]?[0-9][.]([ ](Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([ ]202[0-9])?|(0|1)?[0-9][.]?(202[0-9])?)(\n| )"
# https://regex101.com/r/4J8BJ9/1
INCIDENCE_REGEX = r"(?<=Inzidenzstufe \d \n[(]).*(?=\))"
# https://regex101.com/r/FojuZ9/1
OTHER_INCIDENCE_REGEX = r"(((?<=Inzidenzstufe)|(?<=Inzidenzwert)|(?<=Inzidenz)|(?<=Schwellenwert))).{0,20}(\d{2,3})"
# -------------------------------logging------------------------------------------
loggerName = "restrictionLogger"
logFileName = 'RestrictionScraper.log'
# -------------------------------ElasticSearch------------------------------------------
es_url = '127.0.0.1'
es_port = '9200'
indexName = "restrictions",
indexMapping = \
{
    "mappings" : {
      "properties" : {
        "creationDate" : {
          "type" : "date",
          "format": "dd-MM-yyyy"
        },
        "validFrom" : {
          "type" : "date",
          "format": "dd-MM-yyyy"
        },
        "incidenceBased" : {
          "type" : "boolean"
        },
        "incidenceRanges" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "federateState" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "tags" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 512
            }
          }
        },
      }
    }
}
metaIndexName = "metarestrictions"
METADATA_ATTRIBUTES = ["validFrom", "incidenceBased", "federateState", "creationDate", "incidenceRanges", "tags"]
metaIndexMapping = \
{
  "mappings" : {
    "properties" : {
      "state" : {
        "type" : "text"
      },
      "url" : {
        "type" : "text"
      },
      "target" : {
        "type" : "text"
      },
      "value" : {
        "type" : "text"
      }
    }
  }
}

