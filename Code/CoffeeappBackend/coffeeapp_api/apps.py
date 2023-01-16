import sys

from django.apps import AppConfig

sys.path.append("D:\Programming\master\MAI_NLP_PROJECT")
from transformers import pipeline


class CoffeeappApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coffeeapp_api'
    model = pipeline("question-answering", model="deepset/roberta-base-squad2")
    print("Model Loaded!")