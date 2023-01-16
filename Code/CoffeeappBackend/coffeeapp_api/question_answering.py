import collections

import pandas as pd
from django.conf import settings

from Code.Clients import client_factory


class QuestionAnswerer:

    def __init__(self, language, question, manufacturer=None, product=None, model=None, max_answers=3):
        self.language = language
        self.product = product
        self.manufacturer = manufacturer
        self.question = question
        self.model = model
        self.max_answers = max_answers
        self.answers = None
        self.errors = None


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
        context = self._get_context()
        print("Received Context and Question!")
        self.answers = self._get_answers(context)
        print("Answered Question!")


    def _get_context(self):
        """
        Method that reads the context given from ES and extracts only the paragraph texts.

        Returns
        -------
        list
            List of paragraphs from one specific manufacturer and product
        """
        docs = self._get_metadata()

        df = pd.DataFrame(docs)
        texts = df["headerParagraphText"].unique().tolist()
        texts.extend(df["subHeaderParagraphText"].unique().tolist())
        texts = list(filter(None, texts))
        
        return texts


    def _get_metadata(self):
        """
        Method that reads the metadata from ES and returns it.

        Returns
        -------
        list
            List of metadata from one specific manufacturer and product
        """
        # TODO: Similarity Search
        return client_factory.get_meta_client().get_corpusfile_metadata(self.manufacturer,
                                                                        self.product,
                                                                        self.language)


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
            
            result = self.model(question=self.question, context=paragraph)
            results.append(result)

        results = sorted(results, key=lambda k: k['score'], reverse=True)[0:self.max_answers]
        answers = [answer["answer"] for answer in results]

        return answers

############################### UNUSED #########################################

    # def _get_corpus_location(self):
    #     """
    #     returns: a list of all filetpaths
    #     """
    #     meta_data = self._get_metadata() 
    #     if isinstance(meta_data, collections.Iterable):
    #         filepaths = []
    #         for m in meta_data:
    #             filepaths.append(m["filepath"])
    #         return filepaths
    #     else:
    #         return [meta_data["filepath"]]
    

    # def _get_corpus(self, location):
    #     return client_factory.get_file_client().read_file(location)