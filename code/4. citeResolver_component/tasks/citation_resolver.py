from .utils import get_split_text
from string import ascii_letters
import regex as re
import logging
import spacy

spacy_model = spacy.load('en_core_web_sm')

alph_to_num = dict(zip(ascii_letters,[ord(c)%32 for c in ascii_letters]))

legal_acts = re.compile(r'Directives?|Regulations?|Decisions?')
directive_regex = re.compile(r'Directives?\s(?:\((?:EU|EEC)\)\s)?(?P<year>\d+)\/(?P<number>\d+)')
regulation_regex = re.compile(r'(Regulations?\s(?:\(?(?:\w+(?:\,?\s?\w+){1,}?)\)?\s)?(?:\w+\s)(?P<number>\d+)\/?(?P<year>\d+)?)|(Regulations?\s(?:\(?(?:\w+(?:\,?\s?\w+){1,}?)\)?\s)?(?P<year>\d+)\/?(?P<number>\d+)?)')
decision_regex = re.compile(r'(Decisions?\sNo(?P<number>\d+)\/(?P<year>\d+))|(Decisions?\s(?P<year>\d+)\/(?P<number>\d+))')
article_regex = re.compile(r'Articles?\s(?P<article_number>\d+)\s?(?:\(?(?P<article_fragment_num>\d+)\)?)?(?:\(?(?P<article_fragment_char>\w+)\)?)?')

def process_explanation(explanation):
    """
    Process the explanation and return the information as a dictionary.
    Placeholder function - implement according to your specific logic.
    """
    # Example processing logic
    definition_fragments = get_split_text(explanation, spacy_model)
    intext_citation_list = []

    for definition in definition_fragments:
        regulation_matches = []
        decision_matches = []
        directive_matches = []
        citation_information = {}

        try:
            regulation_matches = regulation_regex.findall(definition, timeout=10)
            decision_matches = decision_regex.findall(definition, timeout=10)
            directive_matches = directive_regex.findall(definition, timeout=10)
        except TimeoutError:
            continue
        
        if not (regulation_matches or decision_matches or directive_matches):
            citation_information['cited_celex_id'] = 'NA'
            citation_information['cited_article_number'] = -1
            citation_information['cited_article_fragment_number'] = -1
            citation_information['comment'] = 'citation with Regulation, Directive, or Decision not present'

            intext_citation_list.append(citation_information)
            continue
    
        intext_citation_information = intext_citation_relation(definition)
    
        for i in range(len(intext_citation_information)):
            citation_information['cited_celex_id'] = intext_citation_information[i]['celex_number']
            citation_information['cited_article_number'] = intext_citation_information[i]['article_number']
            citation_information['cited_article_fragment_number'] = intext_citation_information[i]['article_fragment_number']
            citation_information['comment'] = 'citation successfully extracted'
            intext_citation_list.append(citation_information)
        
    logging.info(f"Completed the citation information extraction")
    logging.info("\n")

    return intext_citation_list


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