from extractors.libraries import *

def get_document_summary(lang, celex_id):
    """
    Extracts the summary of a CELEX document in the specified language.

    This function retrieves the summary of a document identified by its CELEX number 
    from the EUR-Lex website. The language parameter determines the language of 
    the retrieved summary.

    Args:
        lang (str): The language code for the desired summary (e.g., "en" for English).
        celex_id (str): The CELEX number of the document to extract the summary for.

    Returns:
        dict: A dictionary containing the extracted summary information.
            - 'summaryContent' (str): The extracted summary text (may be None if not available).
            - 'rawSummary' (str): The raw HTML content of the summary page (may be None if not available).
    """
    summary_dict = {}
    
    # Preparing URL for the summary of the Celex number
    document_url = f'https://eur-lex.europa.eu/legal-content/{lang}/LSU/?uri=CELEX:{celex_id}'
    document_request = requests.get(document_url)

    if 'No legislative summaries' in document_request.text:
        summary_dict['summaryContent'] = None
        summary_dict['rawSummary'] = None
    else:
        # HTML for that information
        document_page = BeautifulSoup(document_request.text, "html.parser")
    
        language_id = f'format_language_table_HTML_{lang}'
        list_of_documents = document_page.find( 'a', attrs={'id':language_id, 'class': 'piwik_download'}, href = True)
    
        if list_of_documents is None:
            summary_dict['summaryContent'] = None
            summary_dict['rawSummary'] = None
        else:
            summary_url = 'https://eur-lex.europa.eu/'+ list_of_documents['href'][list_of_documents['href'].find("legal-content"):]
            summary_html = requests.get(summary_url).text
            summary_dict['rawSummary'] = summary_html
            summary_dict['summaryContent']= BeautifulSoup(summary_html, "html.parser").text

    return summary_dict