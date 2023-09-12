import regex as re
from tqdm import tqdm
from tasks.utils import get_split_text
import spacy
from string import ascii_letters
import pandas as pd
import json
import logging
import multiprocessing as mp

alph_to_num = dict(zip(ascii_letters,[ord(c)%32 for c in ascii_letters]))
spacy_model = spacy.load('en_core_web_trf')

legal_acts = re.compile(r'Directives?|Regulations?|Decisions?')
directive_regex = re.compile(r'Directives?\s(?:\((?:EU|EEC)\)\s)?(?P<year>\d+)\/(?P<number>\d+)')
regulation_regex = re.compile(r'(Regulations?\s(?:\(?(?:\w+(?:\,?\s?\w+){1,}?)\)?\s)?(?:\w+\s)(?P<number>\d+)\/?(?P<year>\d+)?)|(Regulations?\s(?:\(?(?:\w+(?:\,?\s?\w+){1,}?)\)?\s)?(?P<year>\d+)\/?(?P<number>\d+)?)')
decision_regex = re.compile(r'(Decisions?\sNo(?P<number>\d+)\/(?P<year>\d+))|(Decisions?\s(?P<year>\d+)\/(?P<number>\d+))')
article_regex = re.compile(r'Articles?\s(?P<article_number>\d+)\s?(?:\(?(?P<article_fragment_num>\d+)\)?)?(?:\(?(?P<article_fragment_char>\w+)\)?)?')


def intext_citation_recognition_relation(article_records):
    """
    Function to recognise if the text comprises of an intext citation
    and to store the information of the cited document

    Args:
        article_records (_type_): _description_

    Returns:
        _type_: _description_
    """        
    intext_citation_list = []
    records_list = []
    
    for record in tqdm(article_records, 
                    desc=f"Processing records to extract the ground truth statements (size={len(article_records)})"):

        article_text = record['article_text']

        celex_id = record['celex_id']

        chapter_number = record['chapter_number']
        section_number = record['section_number']
        article_number = record['article_number']
        article_fragment_number = record['article_fragment_number']

        citing_document_information = {}
        citing_document_information['citing_celex_id'] = celex_id
        citing_document_information['citing_chapter'] = chapter_number
        citing_document_information['citing_section'] = section_number
        citing_document_information['citing_article'] = article_number
        citing_document_information['citing_article_fragment'] = article_fragment_number
        citing_document_information['citing_article_subfragment'] = 0

        records_list.append(citing_document_information)

        logging.info(f"Extracting the citation information for {celex_id} document, from chapter {chapter_number} -> section {section_number} -> article {article_number} -> article_fragment {article_fragment_number}")

        citation_information = {}
        article_fragments = get_split_text(article_text, spacy_model)

        spacy_objects = list(spacy_model.pipe(article_fragments))
        for spacy_object in spacy_objects:
            
            law_words = [ent.text for ent in spacy_object.ents if ent.label_ == 'LAW']

            law_result = []
            current = ""

            for s in law_words:
                if "Article" in s:
                    law_result.append(current.strip())
                    current = s
                else:
                    current += " " + s

            law_result.append(current.strip())

            for record in law_result:
                regulation_matches = []
                decision_matches = []
                directive_matches = []

                try:
                    regulation_matches = regulation_regex.findall(record, timeout=10)
                    decision_matches = decision_regex.findall(record, timeout=10)
                    directive_matches = directive_regex.findall(record, timeout=10)
                except TimeoutError:
                    continue


                if not (regulation_matches or decision_matches or directive_matches):
                    continue

                citing_document_information['citing_text'] = article_text
                
                intext_citation_information = intext_citation_relation(record)

                for i in range(len(intext_citation_information)):
                    cited_document_information = {}
                    citation_information['citing_information'] = citing_document_information

                    cited_document_information['cited_celex_id'] = intext_citation_information[i]['celex_number']
                    cited_document_information['cited_article_number'] = intext_citation_information[i]['article_number']
                    cited_document_information['cited_article_fragment_number'] = intext_citation_information[i]['article_fragment_number']
                    cited_document_information['cited_article_subfragment_number'] = 0
                    cited_document_information['cited_article_text'] = " "

                    citation_information['cited_information'] = cited_document_information

                    citation_information['record_identifier'] = f'{celex_id}-{chapter_number}-{section_number}-{article_number}-{article_fragment_number}'

                    intext_citation_list.append(citation_information)
        
        logging.info(f"Completed the citation information for {celex_id} document, from chapter {chapter_number} -> section {section_number} -> article {article_number} -> article_fragment {article_fragment_number}")
        logging.info("\n")

    df_intext_citation = pd.DataFrame.from_records(intext_citation_list, columns=["citing_information", "cited_information", "record_identifier"])
    df_intext_citation['citing_information'] = df_intext_citation['citing_information'].apply(json.dumps)
    df_intext_citation['cited_information'] = df_intext_citation['cited_information'].apply(json.dumps)

    return df_intext_citation, records_list


def intext_citation_relation(text):
    """
    Function objective is to identify the cited document present in the 
    statement
    """
    relation_list = []
    celex_info = None

    directive_index = text.find("Directive")
    decision_index = text.find("Decision")
    regulation_index = text.find("Regulation")

    if directive_index == -1 and decision_index == -1 and regulation_index == -1:
        pass
    else:
        # Determine which string occurred first
        indices = [(directive_index, "Directive"), (decision_index, "Decision"), (regulation_index, "Regulation")]
        indices = [(index, string) for index, string in indices if index != -1]  # Remove strings that were not found
        indices.sort()  # Sort by index
        first_string = indices[0][1]
    
    if "Regulation" in first_string:
      celex_info = re.search(regulation_regex, text)
      regulation = "R"
    elif "Directive" in first_string:
      celex_info = re.search(directive_regex, text)
      regulation = "L"
    elif "Decision" in first_string:
      celex_info = re.search(decision_regex, text)
      regulation = "D"

    if celex_info is not None:
        if celex_info.group('number') is not None and celex_info.group('year') is not None :
            year = celex_info.group('year') if len(celex_info.group('year')) > 2 else "19" + celex_info.group('year')
            number = '{:04}'.format(int(celex_info.group('number')))
            celex_number = f"3{year}{regulation}{number}"

            article_info = re.findall(article_regex, text)
        else:
            article_info = []
    else:
        article_info = []
    
    for index in range(len(article_info)):
        relation_information = {}
        relation_information['celex_number'] = celex_number
        article_number = -1
        article_fragment = -1

        (article_number, article_fragment_number, article_fragment_character) = article_info[index]
        relation_information['article_number'] = article_number

        if article_fragment_number != "":
            article_fragment = article_fragment_number
        elif article_fragment_character != "" and (len(article_fragment_character) < 2) :    
            article_fragment = alph_to_num[article_fragment_character]
        
        relation_information['article_fragment_number'] = article_fragment

        relation_list.append(relation_information)
    
    return relation_list


def intext_citation_resolution():
    """
    Function objective is to identify the contextually relevant candidate
    statement from the cited document
    """    
    pass