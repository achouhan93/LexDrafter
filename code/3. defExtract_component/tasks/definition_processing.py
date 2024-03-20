class DefinitionProcessor():
    """
    A class to process and manage terms within documents. It checks for term existence,
    updates terms, and maintains term identifiers.

    Attributes:
        term (dict): A dictionary of existing terms, mapping term text to term details.
        new_term (list): A list to collect new terms that are encountered.
        last_term_id (int): The last used term identifier, used to assign new IDs to new terms.
    """
    def __init__(self, terms, term_id):
        """
        Initializes the DefinitionProcessor with existing terms and the last term ID.

        Args:
            terms (dict): Existing terms, mapping term text to their details.
            term_id (int): The starting point for new term IDs.
        """
        self.term = terms
        self.new_term = []
        self.last_term_id = term_id

        
    def term_exist(self, token_text: str, doc_id: int):
        """
        Checks if a term exists within the processed terms. If the term is new, it is added;
        otherwise, it retrieves the existing term's information.

        Args:
            token_text (str): The text of the term to check or add.
            doc_id (int): The document ID where the term was found.

        Returns:
            tuple: A tuple containing the term's ID and a boolean indicating if the term was already present.
        """
        # Clean and check the token text against existing terms
        if token_text.strip() not in self.term:
            # Add new term
            self.new_term.append(token_text.strip())
            self.last_term_id = self.last_term_id + 1 # Increment the last term ID
            # Update the terms dictionary with the new term
            self.term.update({token_text.strip(): {"term_id": self.last_term_id, "doc_id": doc_id, "term": token_text.strip()}})
            return (self.last_term_id, False)
        else:
            # Term exists, retrieve its info
            term_info = self.term[token_text.strip()]

            # Check if the term is from the same document
            if term_info["doc_id"] == doc_id:
                return (term_info["term_id"], True)
            
            return (term_info["term_id"], False)


class DocProcessor():
    """
    A class to process and manage documents. It maintains a collection of documents and
    their identifiers, primarily focusing on handling new document entries.

    Attributes:
        celex (list): A list of existing documents, typically by their CELEX identifiers.
        new_celex (list): A list to collect new documents that are encountered.
        last_celex_doc_id (int): The last used document identifier, used to assign new IDs to new documents.
    """
    def __init__(self, documents, doc_id):
        """
        Initializes the DocProcessor with existing documents and the last document ID.

        Args:
            documents (list): Existing documents, typically identified by CELEX numbers.
            doc_id (int): The starting point for new document IDs.
        """
        self.celex = documents
        self.new_celex = []
        self.last_celex_doc_id = doc_id