import collections
import pandas as pd

from Code.Clients import client_factory
import Code.Question_Answering.Question_Answering as QA


class QuestionAnswerer:

    def __init__(self, language, questions, manufacturer=None, product_name=None, max_answers=3):
        self.language = language
        self.product_name = product_name
        self.manufacturer = manufacturer
        self.questions = questions
        self.max_answers = max_answers
        self.answers = None
        self.errors = None


    def is_valid(self):
        try:
            if self.language and self.questions and isinstance(self.questions, collections.Iterable):
                return True
            else:
                self.errors = "question not valid"
                return False
        except Exception:
            self.errors = Exception
            return False


    def ask(self):
        # hier valider request an ES um den context aus den angegebenen manufacturer/model zu bekommen
        # und dann weitergeben an das modul dass die frage beantwortet
        # anschließend antwort (und frage gebündelt (?)) speichern
        context = self._get_context()
        self.answers = self._get_answers(context)


    def _get_context(self):
        docs = self._get_metadata()

        df = pd.DataFrame(docs)
        texts = df["headerParagraphText"].unique().tolist()
        texts.extend(df["subHeaderParagraphText"].unique().tolist())
        texts = list(filter(None, texts))

        # location_in_filesystem = self._get_corpus_location()
        # corpusfiles = []
        # for location in location_in_filesystem:
        #     corpusfiles.append(self._get_corpus(location))
        return texts


    # def _get_corpus_location(self):
    #     """

    #     returns: a list of all filetpaths
    #     """
    #     meta_data = self._get_metadata() # TODO checken was ich hier zurück krieg
    #     if isinstance(meta_data, collections.Iterable):
    #         filepaths = []
    #         for m in meta_data:
    #             filepaths.append(m["filepath"])
    #         return filepaths
    #     else:
    #         return [meta_data["filepath"]]

    def _get_metadata(self):
        # TODO: Similarity Search
        return client_factory.get_meta_client().get_corpusfile_metadata(self.manufacturer,
                                                                        self.product_name,
                                                                        self.language)


    # def _get_corpus(self, location):
    #     return client_factory.get_file_client().read_file(location)

    def _get_answers(self, context):
        answers = QA.answer_questions(context, self.questions)[0:self.max_answers]
        answers = [answer["answer"] for answer in answers]
        return answers
