from extractors.libraries import *


def get_celex_per_page(i, provided_url, list_celex):
    """
    Extracts CELEX numbers from a specific page of the provided URL.

    This function constructs a URL for the given page number and fetches the 
    content using `urllib.request`. Then, it parses the HTML content using 
    BeautifulSoup to find elements containing "CELEX number". 

    Args:
        page_number (int): The page number to extract CELEX numbers from.
        provided_url (str): Base URL of the legal act domain.
        celex_list (list): List to store extracted CELEX numbers.
    """
    # URL is create for each page of the legal act domain
    url = urllib.request.urlopen(provided_url + '&page=' +str(i)).read()

    # Scrapping the Page using the BeautifulSoup Library
    soup = BeautifulSoup(url , 'lxml')

    # Fetching celex numbers by parsing html tags heirarchy and checking for text 'CELEX number' 
    try:
        div_tags = soup.find_all("div", attrs={"class": "col-sm-6"})
        for tag in div_tags:
            titles = tag.find_all("dt")
            values = tag.find_all("dd")
            for t ,v in zip(titles, values):
                if t.text == 'CELEX number: ':
                    list_celex.append(v.text)
    except:
        pass


def get_celex(pages, provided_url):
    """
    Extracts all CELEX numbers from the provided URL using parallel processing.

    This function utilizes a multiprocessing pool to efficiently extract CELEX 
    numbers from all pages within the specified URL. 

    Args:
        total_pages (int): Total number of pages to process.
        provided_url (str): Base URL of the legal act domain.

    Returns:
        list: List of all extracted CELEX numbers.
    """   
    with mp.Manager() as manager:
        list_celex = manager.list()
    
        # Looping over all the pages present for the legal act
        with mp.Pool(processes=pages) as pool:
            pool.starmap(get_celex_per_page, [(i, provided_url, list_celex) for i in range(1,pages)])

        celex_ids = [id for id in list_celex]
        return celex_ids