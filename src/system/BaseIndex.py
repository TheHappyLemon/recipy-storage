from pathlib import Path
import json
from re import sub

class BaseIndex:

    def __init__(self, separator : str) -> None:
        self.separator = separator
        self.documents = {}

    def tokenize(self, document : str) -> list:
        if document.strip() == "":
            raise ValueError("Can not tokenize an empty document")
        return [token.strip() for token in document.strip().split(sep=self.separator)]

    # Mostly for debugging
    def get_document(self, doc_idx : int) -> list:
        return self.documents.get(doc_idx, "DOCUMENT_NOT_FOUND")

    def print(self, file_name : str, index : dict) -> None:
        file_name = self.sanitize_filename(file_name)
        with open(file_name, 'w', encoding='utf-8') as output_f:
            json_str = json.dumps(index, indent=4, ensure_ascii=False)
            output_f.write(json_str)
    
    def levenshtein_distance(self, word_1 : str, word_2 : str):
        
        m = len(word_1)
        n = len(word_2)
        # Initialize 2D matrix
        matrix = []
        for i in range(m + 1):
            row = []
            for j in range(n + 1):
                row.append(0)
            matrix.append(row)
        for i in range(m + 1):
            matrix[i][0] = i
        for j in range(n + 1):
            matrix[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                matrix[i][j] = min(
                    matrix[i-1][j-1] + (0 if word_1[i-1] == word_2[j-1] else 1),
                    matrix[i-1][j] + 1,
                    matrix[i][j-1] + 1,
                )
        #print("2D matrix:")
        #for row in matrix:
           # print(row)
        return matrix[m][n]

    def sanitize_filename(self, filename):
        #Remove invalid characters from a filename and return a valid one.
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized_filename = sub(invalid_chars, '_', filename)
        return sanitized_filename

    def get_index(self):
        raise NotImplementedError("Abstract method!")