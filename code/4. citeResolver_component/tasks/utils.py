def get_split_text(text, spacy_obj):
    """
    Splits the input text into sentences, simulating paragraph-like divisions, using a spaCy language model.
    
    This function processes the given text to replace certain UTF-8 characters that may be misinterpreted by
    the spaCy sentence tokenizer. It then utilizes the provided spaCy object (language model) to tokenize the
    text into sentences, returning these sentences as a list.
    
    Args:
        text (str): The input text to be split into pseudo-paragraphs.
        spacy_obj (Language): An instance of a spaCy Language object (e.g., loaded spaCy language model) used for
                              processing the text and splitting into sentences.
    
    Returns:
        list: A list of strings, where each string is a sentence extracted from the input text.
    """
    # Replace non-breaking space characters with regular spaces and strip leading/trailing whitespace
    text = text.replace(u"\xa0", u" ").strip()

    # Process the cleaned text with the provided spaCy object to create a Doc object
    doc = spacy_obj(text)

    # Extract the text of each sentence from the Doc object and compile into a list
    split_text = [sent.text for sent in doc.sents]
    
    return split_text