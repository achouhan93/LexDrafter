from extractors.libraries import *
from extractors import pages_extraction, get_celex

def celex_main(provided_url):
    """
    Orchestrator function to extract the list of Celex Numbers from the provided URL

    Args:
        provided_url (string): URL of the Domain specific Legal Acts, for example: Energy, Agriculture, Taxation, and other
                                Legal Acts: https://eur-lex.europa.eu/browse/directories/legislation.html
                                Energy Legal Acts: https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile

    Returns:
        list: List of Celex numbers extracted from the provided URL
    """
    logging.info(f"Executing the extraction of the celex number")

    last_page_number = pages_extraction(provided_url)
    all_celex_number = get_celex(last_page_number, provided_url)
    
    logging.info(f"{len(all_celex_number)} documents are present")
    return all_celex_number