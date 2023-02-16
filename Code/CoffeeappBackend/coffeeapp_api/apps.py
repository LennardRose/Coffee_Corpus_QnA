import sys
import logging
from django.apps import AppConfig

sys.path.append("D:\Programming\master\MAI_NLP_PROJECT")
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from Code.config import config


class CoffeeappApiConfig(AppConfig):
    # Model here, so it is only loaded once
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coffeeapp_api'
    qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2")
    embedder_model = SentenceTransformer(config.EMBEDDER)
    logging.info("Loaded QA Model and Embedder Model!")