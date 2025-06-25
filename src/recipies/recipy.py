from src.constants import KEYWORDS_SECTION
from src.exceptions.KeywordsNotFound import KeywordsNotFoundError

class Recipy:
    
    def __init__(self):
        self.filepath = ""
        self.content = ""
        self.keywords = []
        self.keywords_raw = ""

    def load(self, filepath):
        self.filepath = filepath
        with open(self.filepath, 'r', encoding='utf-8') as file:
            self.content = file.read()

    def get_keywords_raw(self):
        if not KEYWORDS_SECTION in self.content:
            raise KeywordsNotFoundError(f"File {self.filepath} has no keywords!")
        return self.content.split(KEYWORDS_SECTION, 1)[1]

    def get_keywords(self): 
        if not KEYWORDS_SECTION in self.content:
            raise KeywordsNotFoundError(f"File {self.filepath} has no keywords!")
        _, keywords_section = self.content.split(KEYWORDS_SECTION, 1)
        self.keywords = [kw.strip().lower() for kw in keywords_section.strip().split(',') if kw.strip()]
        return self.keywords