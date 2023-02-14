from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import json
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
"""
Using a pretrained model from Huggingface
get_qa_model will load the model using load_model function
you need to specify in the config the type of model you want

"""


def get_qa_model(config):
    """
    Supplies trained qa model.
    Calls load model 
    reference
    https://huggingface.co/tasks/question-answering

    Args:
        config: hyperparameters of the type of model you want
    """
    ### Not quite sure of the qa model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    nlp  = pipeline("question-answering", model)


def load_model():
    """
    Loads trained model artifact from
    model store / artifactory

    https://huggingface.co/tasks/question-answering
    """

    pass
