# from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import json
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def answer_question(context, question):
    return answer_questions(context, [question])


def answer_questions(context, questions):
    embeddings = []
    for header in context:
        embedding_dict = {}

        embedding_dict['id'] = header['headerId']
        embedding_dict['embedding'] = model.encode(header['paragraphText'], convert_to_tensor=True)

        embeddings.append(embedding_dict)

    n = 3
    n_highest = []
    for question in questions:
        relevances = []
        for paragraph in embeddings:
            relevances.append(
                util.pytorch_cos_sim(model.encode(question, convert_to_tensor=True), paragraph['embedding']))
        n_highest.append(np.argsort(relevances)[::-1][:n])

    paragraph_for_question = []
    for set in n_highest:
        likely_paragraphs = []
        for i in set:
            likely_paragraphs.append(context[i]['paragraphText'])
        paragraph_for_question.append(likely_paragraphs)

    answers = []
    for i, question in enumerate(questions):
        results = []

        for paragraph in paragraph_for_question[i]:
            result = nlp(question=question, context=paragraph)
            results.append(result)

        results = sorted(results, key=lambda k: k['score'], reverse=True)
        answers.append(results)

    return answers


from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
from evaluate import load

nlp = pipeline("question-answering", model="deepset/roberta-base-squad2")
qa_model = pipeline(
    "question-answering")  # , model="distilbert-base-cased") #default: distilbert-base-cased-distilled-squad
question = "Where do I live?"
context = "My name is Merve and I live in İstanbul."
answer = 'İstanbul'
result = qa_model(question=question, context=context)
print(result)


# Question answering pipeline, specifying the checkpoint identifier
#oracle = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", tokenizer="bert-base-cased")
#result = oracle(question=question, context=context)
#print(result)
predictions = [result["answer"]]
references = [answer]
# Returns the rate at which the input predicted strings exactly match their references, ignoring any strings input as part of the regexes_to_ignore list.
exact_match_metric = load("exact_match")
f1_metric = load("squad") #{'predictions': {'id': Value(dtype='string', id=None), 'prediction_text': Value(dtype='string', id=None)}, 'references': {'id': Value(dtype='string', id=None), 'answers': Sequence(feature={'text': Value(dtype='string', id=None), 'answer_start': Value(dtype='int32', id=None)}, length=-1, id=None)}}
results = exact_match_metric.compute(predictions=predictions, references=references)
print(results)
results = f1_metric.compute(predictions=predictions, references=references)
print(results)
