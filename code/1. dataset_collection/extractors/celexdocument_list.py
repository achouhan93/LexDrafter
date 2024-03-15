from extractors.libraries import *
from extractors import pages_extraction, get_celex

def celex_main(provided_url):
    """
    Extracts a list of CELEX numbers from the provided EUR-Lex URL.

    This function retrieves the last page number from the provided URL 
    (representing a specific domain or legal act category) and then 
    iterates through all pages to extract CELEX numbers.

    Args:
        provided_url (str): URL pointing to a specific domain or legal act category 
                            within EUR-Lex. 
                            Examples:
                                - https://eur-lex.europa.eu/browse/directories/legislation.html (all legal acts)
                                - https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile (Energy legal acts)

    Returns:
        list: List of CELEX numbers extracted from all pages of the provided URL.
    """
    logging.info(f"Executing the extraction of the celex number")

    last_page_number = pages_extraction(provided_url)
    all_celex_number = get_celex(last_page_number, provided_url)
    
    logging.info(f"{len(all_celex_number)} documents are present")
    return all_celex_number