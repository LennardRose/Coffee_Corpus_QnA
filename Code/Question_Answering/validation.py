from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from evaluate import load, evaluator
import torch
import pandas as pd
from utils import read_data, get_data_as_dataset
from tqdm import tqdm
import time

def test_models(models):
    results = []

    # Read data
    df_data = pd.DataFrame(read_data())
    dataset = get_data_as_dataset()
    # build references
    references = []
    for index, row in df_data.iterrows():
        dict = {"id": str(row["id"]), "answers": row["answers"]}
        # remove answer_end from dict as metric does not expect it
        dict["answers"].pop("answer_end", None)
        references.append(dict)

    metric = load("squad")

    for model_checkpoint in tqdm(models, desc="Models"):
        print(f"\n-----Testing model {model_checkpoint}----")
        # predsViaTokenizer = get_predictions_via_tokenizer(model_checkpoint, dataset)
        # history = metric.compute(predictions=predsViaTokenizer, references=references)
        # print("tokenizer:", history)
        # predsViaPipeline = get_predictions_via_pipeline(model_checkpoint, dataset)
        # history = metric.compute(predictions=predsViaPipeline, references=references)
        # print("pipeline:", history)

        history = evaluate_by_evaluator(model_checkpoint, dataset, metric)
        print("evaluator:", history)
        results.append([model_checkpoint, history["exact_match"], history["f1"]])

    results = pd.DataFrame(results, columns=["model", "exact_match", "f1"])
    results.to_csv("model_testing"+time.strftime("%Y%m%d-%H%M%S")+".csv", index=False, sep=";")

    return results


def get_prediction_via_tokenizer(model, tokenizer, question, context):
    # Tokenize data
    inputs = tokenizer(question, context, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    # Get start and end logits
    output = model(**inputs)
    answer_start_scores, answer_end_scores = output.start_logits, output.end_logits

    # Get the most likely beginning of answer with the argmax of the score
    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1

    # Get answer
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer


def get_predictions_via_tokenizer(model_checkpoint, dataset):
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)

    return [{"id": str(data["id"]),
             "prediction_text": get_prediction_via_tokenizer(model, tokenizer, data["question"], data["context"])} for
            data in dataset]


def get_predictions_via_pipeline(model_checkpoint, dataset):
    qa_model = pipeline("question-answering", model=model_checkpoint, tokenizer=model_checkpoint)
    results = qa_model(dataset.remove_columns(["id", "title", "answers"]))

    return [{"id": id, "prediction_text": result["answer"]} for id, result in zip(dataset["id"], results)]


def evaluate_by_evaluator(qa_model, dataset, metric):
    task_evaluator = evaluator("question-answering")
    history = task_evaluator.compute(model_or_pipeline=qa_model, data=dataset, metric=metric, squad_v2_format=False)
    return history


if __name__ == "__main__":
    models = ["deepset/roberta-base-squad2", "distilbert-base-uncased-distilled-squad",
              "deepset/bert-base-cased-squad2"]
    results = test_models(models)
    print(results)
