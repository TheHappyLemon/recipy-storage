from src.system.BaseIndex import BaseIndex

class InvertedIndex(BaseIndex):

    def __init__(self, separator : str) -> None:
        super().__init__(separator)
        self.index = {}
    
    def get_index(self):
        return self.index

    def get_terms(self):
        return self.index.keys()

    def update_index(self, vocabulary, document_index):
        for term in vocabulary:
            if not term in self.index:
                self.index[term] = {
                    document_index : 1
                }
            else:
                postings = self.index.get(term)
                if not document_index in postings:
                    postings[document_index] = 0
                postings[document_index] = postings[document_index] + 1

    def sort_index(self) -> None:
        for term in self.index:
            postings = self.index[term]
            self.index[term] = {key: postings[key] for key in sorted(postings)}

    def tf(self, doc_id : int, term : str) -> float:
        term_count_in_doc = self.documents[doc_id].count(term)
        terms_in_doc = 0
        for term in self.index:
            terms_in_doc = terms_in_doc + int(doc_id in self.index[term])
        return term_count_in_doc / terms_in_doc
    
    def idf(self, term : str) -> float:
        docs_total = len(self.documents)
        docs_with_term = len(self.get_postings(term))
        return docs_total / docs_with_term

    def tf_idf(self, doc_id : int, terms : list) -> float:
        tf_idf_total = 0
        for term in terms:
            # TF(t)  = (termina t skaits dokumentā) / (kopējais terminu skaits dokumentā)
            # IDF(t) = (kopējais dokumentu skaits) / (dokumentu skaits, kas satur terminu t)
            tf_score     = self.tf(doc_id=doc_id, term=term)
            idf_score    = self.idf(term=term)
            tf_idf_total = tf_idf_total + (tf_score * idf_score)
        return tf_idf_total

    def sort_by_tf_idf(self, doc_ids : set, terms : list) -> list:
        sorted_docs = {doc_id: 0 for doc_id in doc_ids}
        for doc_id in doc_ids:
            tf_idf = self.tf_idf(doc_id, terms)
            sorted_docs[doc_id] = tf_idf
        sorted_docs = dict(sorted(sorted_docs.items(), key=lambda item: item[1]))
        return sorted_docs

    def QuerryAnd(self, terms : list) -> list:
        query_result = set()
        for term in terms:
            doc_ids = set(self.get_postings(term))
            # if any terms is not found at all, we can leave already
            if len(doc_ids) == 0:
                return []
            if len(query_result) == 0:
                query_result = doc_ids
            else:
                query_result = query_result.intersection(doc_ids)
        query_result = sorted(query_result)
        return list(query_result)

    def get_postings(self, term = None):
        if term is None:
            # Take all unique documents from index (e.g. - all filenames)
            postings = set()
            for term in self.index:
                for posting in self.index[term]:
                    postings.add(posting)
            return list(postings)
        else:
            # Take all dcouments to whom specicific term points
            if not term in self.index:
                return []
            return list(self.index[term].keys())

                