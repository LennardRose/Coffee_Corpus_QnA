# class to build a valid elasticsearch request

class QuestionSerializer:

    def __init__(self, question):
        self.question = question
        self.answer = None
        self.errors = None



    def is_valid(self):
        try:
            if "manufacturer" in self.question and self.question["manufacturer"] \
                    and "model" in self.question and self.question["model"] \
                    and "question" in self.question and self.question["question"]:
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
        self.answer = ""
