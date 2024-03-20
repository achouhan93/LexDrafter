
def get_split_text(text, spacy_obj):
    """
    Utility function to generate pseudo-paragraph splitting
    """
    # Replace misplaced utf8 chars
    text = text.replace(u"\xa0", u" ").strip()
    doc = spacy_obj(text)
    split_text = [sent.text for sent in doc.sents]
    return split_text