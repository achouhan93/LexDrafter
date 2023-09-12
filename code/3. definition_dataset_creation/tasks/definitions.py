import regex as re
from tqdm import tqdm
from tasks.utils import get_split_text
import pandas as pd
import json
import logging

definition_regex = re.compile(r'\‘(?P<term>[^\’]+)\’\:(?P<definition>[^\.]+)')


def definition_extraction(article_records):
    """
    Function to recognise the terms and their definitions present in the text

    Args:
        article_records (dictionary): article records from the postgresql from respective article_title

    Returns:
        _type_: _description_
    """        
    records_list = []
    
    for record in tqdm(article_records, 
                    desc=f"Processing records to extract the definitions (size={len(article_records)})"):

        article_text = record['article_text']

        celex_id = record['celex_id']
        chapter_number = record['chapter_number']
        section_number = record['section_number']
        article_number = record['article_number']
        article_fragment_number = record['article_fragment_number']
        article_subfragment_number = record['article_subfragment_number']
        article_title = record['article_title']

        document_information = {}
        document_information['celex_id'] = celex_id
        document_information['chapter'] = chapter_number
        document_information['section'] = section_number
        document_information['article'] = article_number
        document_information['article_fragment'] = article_fragment_number
        document_information['article_subfragment'] = article_subfragment_number
        document_information['article_title'] = article_title

        logging.info(f"Extracting the definition information for {celex_id} document, from chapter {chapter_number} -> section {section_number} -> article {article_number} -> article_fragment {article_fragment_number} is started")

        definition_info = re.search(definition_regex, article_text)
        document_information['article_text'] = article_text
        document_information['term'] = definition_info.group('term')
        document_information['relationship'] = 'hasDefinition'
        document_information['definition_text'] = definition_info.group('definition')

        if (document_information['term'] is None or document_information['definition_text'] is None):
            document_information['processed_flag'] = 'N'
        else:
            document_information['processed_flag'] = 'Y'
        
        document_information['regex'] = '\‘(?P<term>[^\’]+)\’\:(?P<definition>[^\.]+)'
        
        records_list.append(document_information)
        logging.info(f"Extracting the definition information for {celex_id} document, from chapter {chapter_number} -> section {section_number} -> article {article_number} -> article_fragment {article_fragment_number} is complete")
        logging.info("\n")

    df_definition = pd.DataFrame.from_records(records_list, columns=["celex_id", "chapter", "section", "article", "article_fragment", "article_subfragment", "article_title", "article_text", "term", "relationship", "definition_text", "processed_flag", "regex"])
    return df_definition