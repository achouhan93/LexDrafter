from tasks import *

def layout_extraction(html_document):
    document = []
    
    # Title extraction
    title_information = title_extraction(html_document)
    document.append(title_information)

    # Document layout extraction except Title
    document = document_information(html_document, document)

    return document


