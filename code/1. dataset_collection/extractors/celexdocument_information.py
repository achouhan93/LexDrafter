from extractors.libraries import *
from extractors import get_metadata, get_file_by_id, opensearch_en_insert


def process_celex_id(celex_id, langs):
    """
    Extracts and stores metadata and document content for a given CELEX ID in specified languages.

    This function takes a CELEX ID and a list of languages as input. It iterates through
    the languages and performs the following:

    1. Calls `get_metadata` to retrieve the document's metadata for the specific language.
    2. Calls `get_file_by_id` to extract the document content for the specific language.
    3. Stores the retrieved metadata and document information in a dictionary structure.
    4. Logs a message indicating successful extraction for the CELEX ID and language.

    Args:
        celex_id (str): The CELEX identifier of the document.
        langs (list): A list of language codes (e.g., ['EN', 'DE']).

    Returns:
        dict: A dictionary containing the extracted information for the CELEX ID in each language.
              The structure is:
              ```
              {
                  'EN': {
                      'metadata': {...},  # Extracted metadata for the English document
                      'documentInformation': {...}  # Extracted document content for the English document
                  },
                  # ... (similar structure for other languages)
              }
              ```
    """
    celex_document_information = {}
    celex_document_information['_id'] = celex_id

    for lang in langs:
        language_document_information = {}

        # Calling the function to extract the metadata for the celex document
        document_metadata = get_metadata(lang, celex_id)

        # Calling the function to extract the document content for the celex document
        document_information = get_file_by_id(lang, celex_id)

        language_document_information['metadata'] = document_metadata
        language_document_information['documentInformation'] = document_information
        celex_document_information[lang] = language_document_information

        logging.info(f'Completed Extracting Information of {celex_id} for {lang}')
        sleep(1)

    return celex_document_information


def get_document_information(os, index_name, celex_list):
    """
    Extracts and stores document information for a list of CELEX IDs in specified languages.

    This function orchestrates the information gathering process for multiple CELEX IDs.
    It utilizes a multiprocessing pool to improve efficiency.

    Args:
        os (object): An OpenSearch connection object.
        index_name (str): The name of the OpenSearch index where the extracted information will be stored.
        celex_list (list): A list of CELEX identifiers for the documents.

    Returns:
        bool: True if document information is successfully extracted and inserted into OpenSearch, 
              False otherwise.
    """
    langs = ['EN'] # Currently supports English only
    
    logging.info(f"Document information gathering started for {len(celex_list)} in {len(langs)} languages")
    with mp.Pool() as pool:
        results = [pool.apply_async(process_celex_id, args=(celex_id, langs)) for celex_id in celex_list]
        output = [p.get() for p in results]

        # English extraction
        status = opensearch_en_insert(os, index_name, output)
        if status:
            logging.info(f"Document information gathering completed for {len(celex_list)} in {len(langs)} languages")
            return status   
        else:
            logging.info(f"Document information gathering failed for {len(celex_list)} in {len(langs)} languages, refer logs")   
            return status