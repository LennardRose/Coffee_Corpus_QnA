from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import json
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # TODO model from config!
nlp = pipeline("question-answering", model="deepset/roberta-base-squad2")


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
            result = nlp(question = question, context = paragraph)
            results.append( result)

        results = sorted( results , key=lambda k: k['score'], reverse=True)
        answers.append(results)

    return answers