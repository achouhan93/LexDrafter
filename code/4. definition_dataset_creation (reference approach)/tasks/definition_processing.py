class DefinitionProcessor():

    def __init__(self, terms, term_id):
        self.term = terms
        self.new_term = []
        self.last_term_id = term_id

        
    def term_exist(self, token_text: str, doc_id: int):
        if token_text.strip() not in self.term:
            self.new_term.append(token_text.strip())
            self.last_term_id = self.last_term_id + 1
            self.term.update({token_text.strip(): {"term_id": self.last_term_id, "doc_id": doc_id, "term": token_text.strip()}})
            return (self.last_term_id, False)
        else:
            term_info = self.term[token_text.strip()]

            if term_info["doc_id"] == doc_id:
                return (term_info["term_id"], True)
            
            return (term_info["term_id"], False)


class DocProcessor():

    def __init__(self, documents, doc_id):
        self.celex = documents
        self.new_celex = []
        self.last_celex_doc_id = doc_id
