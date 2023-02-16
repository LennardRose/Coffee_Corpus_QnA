import collections
import logging
import sys
#sys.path.append("D:\Programming\master\MAI_NLP_PROJECT")
# import Code.SimilaritySearch.embedders as embedders
import pandas as pd
from django.conf import settings

from Code.Clients import client_factory
from Code.CoffeeappBackend.coffeeapp_api.apps import CoffeeappApiConfig
from Code.config import config

class QuestionAnswerer:

    def __init__(self, language, question, manufacturer=None, product=None, model=None, max_answers=3):
        self.language = language
        self.product = product
        self.manufacturer = manufacturer
        self.question = question
        self.max_answers = max_answers
        self.answers = None
        self.errors = None
        self.qa_model = CoffeeappApiConfig.qa_model
        self.embedder_model = CoffeeappApiConfig.embedder_model
        self.n_returns = config.SIM_SEARCH_RETURNS

    def is_valid(self):
        """Checks if the QuestionAnswerer is valid.

        Returns
        -------
        bool
            True if the QuestionAnswerer is valid, False otherwise
        """
        try:
            if self.language and self.question:
                return True
            else:
                self.errors = "question not valid"
                return False
        except Exception:
            self.errors = Exception
            return False

    def ask(self):
        """Entry method for the QuestionAnswerer"""
        try:
            context = self._get_context()
            logging.debug("Received Context and Question!")
            self.answers = self._get_answers(context)
            logging.debug("Answered Question!")
        except Exception:
            self.errors = Exception
            return False

    def _get_context(self):
        """
        Method that reads the context given from ES and extracts only the paragraph texts.

        Returns
        -------
        list
            List of paragraphs from one specific manufacturer and product
        """
        embedded_question = self.embedder_model.encode(self.question)
        logging.debug("Embedded Question!")

        contexts = client_factory.get_context_client().search_similar_context(manufacturer=self.manufacturer,
                                                                              product_name=self.product,
                                                                              language=self.language,
                                                                              question_embedded=embedded_question,
                                                                              n_returns=self.n_returns)

        if contexts:
            df = pd.DataFrame(contexts)
            df["headerParagraphText"].fillna("", inplace=True)
            df["subHeaderParagraphText"].fillna("", inplace=True)  # fill None paragraphs with empty string
            df["total"] = df["headerParagraphText"].astype(str) + df["subHeaderParagraphText"].astype(str)
            texts = df["total"].unique().tolist()
            texts = list(filter(None, texts))

            return texts

        else:
            logging.error("no context retrievable")
            return None

    def _get_answers(self, context):
        """Method that returns the answers to the question.

        Parameters
        ----------
        context : list
            List of paragraphs from one specific manufacturer and product

        Returns
        -------
        list
            List of answers to the question
        """

        results = []

        for paragraph in context:
            result = self.qa_model(question=self.question, context=paragraph)

            # filter mechanic: to filter answers like "12" or "yes"
            if len(result["answer"]) <= 5:
                continue
            results.append(result)

        results = sorted(results, key=lambda k: k['score'], reverse=True)[0:self.max_answers]
        answers = [answer["answer"] for answer in results]

        return answers
