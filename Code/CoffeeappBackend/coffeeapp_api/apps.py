import sys
sys.path.append("C:/Users/jochen/MAI_NLP_PROJECT")
import logging
from django.apps import AppConfig

from transformers import pipeline
from sentence_transformers import SentenceTransformer
from Code.config import config


class CoffeeappApiConfig(AppConfig):
    # Model here, so it is only loaded once
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coffeeapp_api'
    qa_model = pipeline("question-answering", model=config.QA_MODEL, tokenizer=config.QA_MODEL)
    embedder_model = SentenceTransformer(config.EMBEDDER)
    logging.info("Loaded QA Model and Embedder Model!")