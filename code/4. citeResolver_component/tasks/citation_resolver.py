from string import ascii_letters
import regex as re
import logging

# Map each ASCII letter to a numerical value
alph_to_num = dict(zip(ascii_letters,[ord(c)%32 for c in ascii_letters]))

# Compile regular expressions for identifying legal acts
legal_acts = re.compile(r'Directives?|Regulations?|Decisions?')
directive_regex = re.compile(r'Directives?\s(?:\((?:EU|EEC)\)\s)?(?P<year>\d+)\/(?P<number>\d+)')
regulation_regex = re.compile(r'(Regulations?\s(?:\(?(?:\w+(?:\,?\s?\w+){1,}?)\)?\s)?(?:\w+\s)(?P<number>\d+)\/?(?P<year>\d+)?)|(Regulations?\s(?:\(?(?:\w+(?:\,?\s?\w+){1,}?)\)?\s)?(?P<year>\d+)\/?(?P<number>\d+)?)')
decision_regex = re.compile(r'(Decisions?\sNo(?P<number>\d+)\/(?P<year>\d+))|(Decisions?\s(?P<year>\d+)\/(?P<number>\d+))')
article_regex = re.compile(r'Articles?\s(?P<article_number>\d+)\s?(?:\(?(?P<article_fragment_num>\d+)\)?)?(?:\(?(?P<article_fragment_char>\w+)\)?)?')

def process_explanation(explanation):
    """
    Process the explanation text to extract citation information.

    The function splits the explanation text into fragments, searches for legal act citations
    within each fragment, and extracts relevant details about each citation.

    Args:
        explanation (str): The explanation text to be processed.

    Returns:
        list: A list of dictionaries, where each dictionary contains information about a cited legal act.
    """
    intext_citation_list = [] # Initialize list to hold citation information
    definition_fragments = [explanation]
    # Iterate through each fragment to find citations
    for definition in definition_fragments:
        regulation_matches = []
        decision_matches = []
        directive_matches = []
        citation_information = {}

        try:
            # Find all matches for each type of legal act in the fragment
            regulation_matches = regulation_regex.findall(definition, timeout=10)
            decision_matches = decision_regex.findall(definition, timeout=10)
            directive_matches = directive_regex.findall(definition, timeout=10)
        except TimeoutError:
            # Skip the current iteration if a timeout occurs
            continue
        
        # Skip the fragment if no legal act citations are found
        if not (regulation_matches or decision_matches or directive_matches):
            citation_information['cited_celex_id'] = 'NA'
            citation_information['cited_article_number'] = -1
            citation_information['cited_article_fragment_number'] = -1
            citation_information['comment'] = 'citation with Regulation, Directive, or Decision not present'

            intext_citation_list.append(citation_information)
            continue
    
        intext_citation_information = intext_citation_relation(definition)
    
        # Iterate through extracted citation information to populate the list
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
    Identify and extract information about cited legal documents in a given text.

    This function searches the text for mentions of Directives, Regulations, or Decisions,
    extracts relevant information about these citations, and compiles details about any
    cited articles within these legal acts.

    Args:
        text (str): The text to search for legal document citations.

    Returns:
        list: A list of dictionaries, each containing details about a cited article within a legal document.
    """
    relation_list = []
    celex_info = None

    # Search for the first occurrence of each type of legal act in the
    directive_index = text.find("Directive")
    decision_index = text.find("Decision")
    regulation_index = text.find("Regulation")

    # Check if any legal act is found in the text
    if directive_index == -1 and decision_index == -1 and regulation_index == -1:
        pass
    else:
        # Determine which string occurred first
        indices = [(directive_index, "Directive"), (decision_index, "Decision"), (regulation_index, "Regulation")]
        indices = [(index, string) for index, string in indices if index != -1]  # Remove strings that were not found
        indices.sort()  # Sort by index
        first_string = indices[0][1]
    
    # Based on the first found legal act type, search for detailed citation using respective regex
    if "Regulation" in first_string:
      celex_info = re.search(regulation_regex, text)
      regulation = "R"
    elif "Directive" in first_string:
      celex_info = re.search(directive_regex, text)
      regulation = "L"
    elif "Decision" in first_string:
      celex_info = re.search(decision_regex, text)
      regulation = "D"

# If detailed citation information was found, extract and compile article information
    if celex_info is not None:
        if celex_info.group('number') is not None and celex_info.group('year') is not None :
            year = celex_info.group('year') if len(celex_info.group('year')) > 2 else "19" + celex_info.group('year')
            number = '{:04}'.format(int(celex_info.group('number')))
            celex_number = f"3{year}{regulation}{number}"

            # Find all article citations within the text
            article_info = re.findall(article_regex, text)

            if len(article_info) == 0:
                relation_information = {}
                relation_information['celex_number'] = celex_number
                relation_information['article_number'] = -1
                relation_information['article_fragment_number'] = -1
                relation_list.append(relation_information)
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