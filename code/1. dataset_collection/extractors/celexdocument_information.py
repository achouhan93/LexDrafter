from extractors.libraries import *
from extractors import get_metadata, get_file_by_id, opensearch_en_insert

def process_celex_id(celex_id, langs):
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
    Orchestrator function to extract the summary and document content for the provided Celex Number

    Args:
        celex_list (list): List of Celex number for which the summary and contents needs to be extracted

    Returns:
        list: Comprising of dictionary of information about the summary and document 
                content for the provided Celex Numbers in the different languages
    """
    langs = ['EN']
    
    logging.info(f"Document information gathering started for {len(celex_list)} in {len(langs)} languages")
    with mp.Pool() as pool:
        results = [pool.apply_async(process_celex_id, args=(celex_id, langs)) for celex_id in celex_list]
        output = [p.get() for p in results]

        # German and English extraction
        status = opensearch_en_insert(os, index_name, output)
        if status:
            logging.info(f"Document information gathering completed for {len(celex_list)} in {len(langs)} languages")
            return status   
        else:
            logging.info(f"Document information gathering failed for {len(celex_list)} in {len(langs)} languages, refer logs")   
            return status