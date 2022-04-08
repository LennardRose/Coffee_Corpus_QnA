# import glob and os
#####################################################################
#                                                                   #
#                     Lennard Rose 5118054                          #
#       University of Applied Sciences Wuerzburg Schweinfurt        #
#                           SS2021                                  #
#                                                                   #
#####################################################################
import os, glob
from elasticsearch import Elasticsearch
import json

client = Elasticsearch("localhost:9200")


# posix uses "/", and Windows uses ""
if os.name == 'posix':
    slash = "/" # for Linux and macOS
else:
    slash = chr(92) # '\' for Windows

def _current_path():
    return os.path.dirname(os.path.realpath( __file__ ))

# default path is the script's current dir
def _get_files_in_dir():

    self = os.path.join(_current_path(), "article_sources")

    file_list = []

    # put a slash in dir name if needed
    if self[-1] != slash:
        self = self + slash

    # iterate the files in dir using glob
    for filename in glob.glob(self + '*.*'):

        if ".json" in filename:
            file_list += [filename]

    return file_list

def _get_data_from_json_file(file):
    data = None

    with open(file) as file:
        data = json.load(file)

    return data

# pass a directory (relative path) to function call
all_files = _get_files_in_dir()

print ("Files to index:", len( all_files ))

if not client.indices.exists(index="article_config"):
    print("Index article_config not found, initialize index.")
    client.indices.create(index="article_config")

python_path = os.path.join(_current_path(), "venv", "Scripts", "python.exe")
main_path = os.path.join(_current_path(), "main.py")


index_count = 0
# iterate over the list of files
for file in enumerate(all_files):

    # get the data inside the file
    data = _get_data_from_json_file( file[1] )

    query = {
        "query" :  
            { "bool" : 
                { "must" : [ 
                    {"match_phrase": { "region": { "query" : data["region"] } } },
                    {"match_phrase": { "base_url": { "query" : data["base_url"] } } }
                ]} 
            }
    }

    already_indexed_document = client.search(index="article_config", body = query)

    if already_indexed_document["hits"]["total"]["value"] == 0:
        response = client.index(index="article_config", body=data, doc_type="_doc")
        if response["result"] == "created":
            index_count += 1
            print("@hourly " + python_path + " " + main_path + " --elasticsearch " + response["_id"])
    else:
        print("file was already indexed, skip")

print("indexed: " + str(index_count) + " files")

