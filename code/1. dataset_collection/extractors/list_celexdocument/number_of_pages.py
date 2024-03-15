from extractors.libraries import *


def pages_extraction(provided_url):
    """
    Extracts the last page number from a given EUR-Lex URL.

    This function fetches the provided URL, parses the HTML content using BeautifulSoup, 
    and identifies the element containing the last page number within the pagination section.

    Args:
        provided_url (str): URL pointing to a specific domain or legal act category within EUR-Lex.
            Examples:
                - https://eur-lex.europa.eu/browse/directories/legislation.html (all legal acts)
                - https://eur-lex.europa.eu/search.html?type=named&name=browse-by:legislation-in-force&CC_1_CODED=12&displayProfile=allRelAllConsDocProfile (Energy legal acts)

    Returns:
        int: The last page number extracted from the pagination section, or 2 if no pagination is found.
    """
    input_url = urllib.request.urlopen(provided_url)
    input_soup = BeautifulSoup(input_url , 'lxml')
    page_number_indexes = input_soup.find_all('a', class_ = 'btn btn-primary btn-sm')
    if len(page_number_indexes) == 0:
        last_page_number = 2
    else:
        last_page_number_url = page_number_indexes[1].attrs['href']
        last_page_number = int((re.search('page=(\d+)', last_page_number_url , re.IGNORECASE)).group(1)) + 1
    return last_page_number