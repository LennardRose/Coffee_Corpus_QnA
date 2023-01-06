import json
import pandas as pd
import numpy as np
import os
from datasets import Dataset
from datasets import DatasetDict

basePath = "generated_training_data/"


def get_data_as_dataset():
    df_data = pd.DataFrame(read_data())
    df_data["id"] = df_data['id'].apply(str)
    dataset = Dataset.from_pandas(df_data)
    return dataset


def get_data_as_dataset_for_pipe():
    data = read_data()

    dataset = Dataset.from_pandas(pd.DataFrame(data)[["question", "context"]])
    return dataset


def read_data():
    json_files = [pos_json for pos_json in os.listdir(basePath) if pos_json.endswith('.json')]

    data = []

    for json_file in json_files:
        data.extend(json.load(open(basePath + "/" + json_file, encoding="utf8")))

    formattedData = format_data(data)

    for d in formattedData:
        d["answers"].pop("answer_end", None)

    return formattedData


def format_data(data):
    formattedData = []

    for idx, dic in enumerate(data):
        # make all keys lowercase for easier working
        dic = {k.lower(): v for k, v in dic.items()}

        if not "answer" in dic:
            continue

        if "answer" in dic:
            newDic = {}

            newDic["id"] = idx
            newDic["title"] = f"Test_{idx}"

            if not "text" in dic:
                dic["text"] = dic["context"]

            newDic["context"] = dic["text"]
            newDic["question"] = dic["question"]

            answers = []
            answersStart = []
            answersEnd = []

            # special case handling
            if type(dic["answer"]) == dict:

                text = dic["answer"]["text"]
                answer_start = dic["answer"]["answer_start"]
                if "end" in dic["answer"]:
                    answer_end = dic["answer"]["answer_end"]
                else:
                    # print(dic["answer"])
                    answer_end = [start + len(text) for start, text in
                                  zip(dic["answer"]["answer_start"], dic["answer"]["text"])]

                newDic["answers"] = {
                    "text": text,
                    "answer_start": answer_start,
                    "answer_end": answer_end
                }
                # print(newDic["answers"])

            else:

                for answer in dic["answer"]:
                    answers.append(answer["text"])
                    answersStart.append(int(answer["start"]))
                    answersEnd.append(int(answer["end"]))

                newDic["answers"] = {
                    "text": answers,
                    "answer_start": answersStart,
                    "answer_end": answersEnd
                }

            formattedData.append(newDic)

    return formattedData
