from tasks import *


def layout_extraction(html_document):
    """
    Extracts the layout information from an HTML document.

    This function orchestrates the extraction of various components of a document,
    starting with the title and then extracting other parts of the document's layout.
    The extraction process relies on specific functions designed for each part,
    such as `title_extraction` for the title and `document_information` for the rest of the document.

    Args:
        html_document (BeautifulSoup): A BeautifulSoup object representing the HTML document from which
                                       to extract layout information.

    Returns:
        list: A list of dictionaries, where each dictionary contains information about a different part of the document's layout.
             The first item in the list always represents the title information.
    """
    document = []

    # Extract the title information and append it to the document list
    title_information = title_extraction(html_document)
    document.append(title_information)

    # Extract the rest of the document layout information and update the document list
    document = document_information(html_document, document)

    return document
