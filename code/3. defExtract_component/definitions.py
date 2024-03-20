import re
import unicodedata

import nltk
from nltk.corpus import wordnet as wn
import spacy

# Dictionaries to store processed data
annotations = {}  # Annotations for 1:1 relationships, ideal for straightforward printing
counter_set = {}  # Counts the frequency of each definition
sentences_set = {}
articles_set = {}
sub_definitions = {}  # Stores definitions that are part of other definitions
definitions = {}  # Definitions with n:m relationships
definitions_dict = {}  # Definitions with 1:n relationships, used for annotation
articles_set_and_frequency = {}
definitions_list = list(tuple())  # List of tuples, each containing a definition and its explanation
nltk.download('wordnet') # Ensures the WordNet data is available for synonym checks


def find_definitions(soup):
    """
    Extracts and processes definitions from the provided BeautifulSoup object,
    specifically from sections marked as "Definitions" until the next article.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML of a legal document.

    Returns:
        list: A list of tuples, each containing a definition and its explanation.
    """
    global annotations
    annotations = {}
    global definitions_list
    definitions_list = list(tuple())
    global definitions_dict
    definitions_dict = {}

    # Identify the start and end points for definitions within the document
    start_class = soup.find("p", string="Definitions")
    end_class = soup.find("p", string=re.compile("Article"))

    # Iterate through sibling elements to extract definitions and their explanations
    for element in start_class.next_siblings:
        element_text = element.text.replace('\xa0', ' ').strip()
        if element == end_class:
            break
        if re.match(r"^Article \d+$", element_text):
            break
        process_definitions(element_text)
    save_to_sub_definitions()
    return definitions_list


def check_definition_part_of_another_definition(definition):
    """
    Determines if a given definition is part of another definition within the processed list.

    Args:
        definition (str): The definition to check.

    Returns:
        set: A set of definitions that contain the given definition as part of them.
    """
    part_def = set()
    for (key, value) in definitions_list:
        if key.__contains__(definition) and key != definition:
            part_def.add(key)
    return part_def


def save_to_sub_definitions():
    """
    Saves processed definitions to a global dictionary, identifying those that are part of other definitions.
    """
    global sub_definitions
    for (key, value) in definitions_list:
        abrv_match = re.search(r'(.*?)\[ABRV\](.*?)\[ABRV\](.*?)', key)

        if abrv_match:
            extracted_text = abrv_match.group(2).strip()
            # Check the number of words in the extracted text
            words = extracted_text.split()
            if len(words) > 1:
                key = extracted_text
            else:
                if abrv_match.group(1):
                    key = abrv_match.group(1).strip()
                elif abrv_match.group(3):
                    key = abrv_match.group(3).strip()
        sub_definitions[key] = check_definition_part_of_another_definition(key)


def fill_sets():
    """
    Initializes global sets and counters for new processing.
    """
    global articles_set
    global articles_set_and_frequency
    global sentences_set
    global counter_set
    for (key, value) in definitions_list:
        articles_set[key] = set()
        articles_set_and_frequency[key] = list()
        sentences_set[key] = ""
        counter_set[key] = 1


def get_article_number(article):
    """
    Extracts the article number from a string.

    Args:
        article (str): The string containing an article number.

    Returns:
        int: The extracted article number.
    """
    return int(article.split()[1])


def get_annotations():
    """
    Retrieves the global annotations dictionary.

    Returns:
        dict: The annotations dictionary.
    """
    return annotations


def get_sentences():
    """
    Retrieves the global sentences set.

    Returns:
        set: The sentences set.
    """
    return sentences_set


def get_counter():
    """
    Retrieves the global counter set.

    Returns:
        set: The counter set.
    """
    return counter_set


def get_articles(key):
    """
    Retrieves a comma-separated string of articles related to a given key.

    Args:
        key (str): The key for which to retrieve related articles.

    Returns:
        str: A comma-separated string of article numbers.
    """
    articles = ", ".join(sorted(articles_set[key], key=get_article_number))
    return articles


def check_two_definitions_in_text(definition1, definition2, text):
    """
    Checks if the longer definition (definition2) appears in the text without the shorter one (definition1).

    Args:
        definition1 (str): The shorter definition.
        definition2 (str): The longer definition.
        text (str): The text to check.

    Returns:
        bool: True if only definition2 occurs in the text; False otherwise.
    """
    if not text.__contains__(definition2):
        return False
    strings = text.split(definition2)
    new_string = "".join(strings)
    if new_string.__contains__(definition1):
        return False
    return True


def check_more_definitions_in_text(definition1, text, cap):
    """
    Verifies if longer definitions occur in the text while the shorter does not, taking into account capitalization.

    Args:
        definition1 (str): The shorter definition to check against.
        text (str): The text in which to search for definitions.
        cap (bool): Indicates if the first letter should be treated as capitalized in the check.

    Returns:
        bool: True if only longer definitions occur in the text; False otherwise.
    """
    if cap:
        definition1 = definition1[0].lower() + definition1[1:]
    definition_set = sub_definitions[definition1]
    for s in definition_set:
        if check_two_definitions_in_text(definition1, s, text):
            return True
    return False


def is_synonym(verb):
    """
    Checks if the given verb is a synonym of "mean", "include", or "be", based on WordNet.

    Args:
        verb (str): The verb to check.

    Returns:
        bool: True if the verb is a synonym; False otherwise.
    """
    if verb == "mean" or verb == "include" or verb == "be":
        return True
    # since most of the regulations have mean as a verb or include, we compare the verb to the synonyms of them
    mean_synsets = wn.synsets('mean', pos='v')
    mean_synonyms = set(lemma.name() for synset in mean_synsets
                        for lemma in synset.lemmas())
    include_synsets = wn.synsets('include', pos='v')
    include_synonyms = set(lemma.name() for synset in include_synsets
                           for lemma in synset.lemmas())
    be_synsets = wn.synsets('be', pos='v')
    be_synonyms = set(lemma.name() for synset in be_synsets
                      for lemma in synset.lemmas())
    if verb in mean_synonyms or verb in include_synonyms or verb in be_synonyms:
        return True
    return False


def remove_text_within_brackets(text):
    """
    Removes any text within parentheses from the given text, along with the parentheses themselves.

    Args:
        text (str): The text from which to remove parenthesized content.

    Returns:
        str: The modified text with parenthesized content removed.
    """
    # Use regular expressions to find and remove text within brackets
    if re.search(r'\(.*\)', text):
        text = re.sub(r'[()]', '[ABRV]', text)  # Remove both brackets

    # Check if only one bracket is present
    elif re.search(r'\(.*', text):
        text = re.sub(r'\(.*', '', text)  # Remove text after the opening bracket

    return text


def process_definitions(text):
    """
    Extracts definitions and their explanations from a given text block, focusing on the part before the first semicolon.
    It leverages SpaCy for natural language processing to identify key verbs associated with definitions.
    Additionally, it handles cases where definitions are split across multiple lines or contain special notations like abbreviations.

    Args:
        text (str): The text block from which to extract definitions and explanations.

    Global Variables:
        definitions (dict): Stores unique definitions and their corresponding explanations.
        annotations (dict): Annotations for processed definitions.
    """
    text = unicodedata.normalize("NFKD", text) # Normalize unicode characters
    if text.__contains__("’"):
        nlp = spacy.load("en_core_web_sm") # Load SpaCy language model
        doc = nlp(
            text.split(";")[0]
        )  # this way only the most important part of the definition will be examined
        definition_set = set()
        explanation_set = set()
        # Search for the first verb that implies a definition
        first_verb = None
        for token in doc:
            if (token.text.__contains__("mean") and token.pos_ == "VERB"):
                first_verb = token
                break
            if token.dep_ == "ROOT" and (token.pos_ == "VERB"
                                         or token.pos_ == "AUX"):
                first_verb = token
                break
        if first_verb is not None and is_synonym(first_verb.lemma_):
            definition = text[:first_verb.idx].strip()
            explanation = text[first_verb.idx:].strip()

            # Process and clean individual lines within both definition and explanation parts
            d = [s.strip() for s in definition.split("\n") if s != ""]
            e = [s.strip() for s in explanation.split("\n") if ((s != "") and (len(s) > 3))]

            # Save processed data for further use
            save_in_annotations("".join(d), "".join(e))
            for element in d:
                if element.__contains__("‘"):
                    if element.__contains__(" and ‘") or element.__contains__(
                            " or ‘") or element.__contains__(", ‘"):
                        definition_set = split_multiples(element)
                    else:
                        if '(' in element:
                            element = remove_text_within_brackets(element)
                        definition_set.add(element.strip())
            for element_e in e:
                if element_e != "" and element_e[0] != "(":
                    # Handle cases with multiple explanations
                    if len(e) > 1 and element_e.__contains__(":"):
                        base = element_e.strip()
                        while len(e) > e.index(element_e.strip()) + 1:
                            next_element = e[e.index(element_e.strip()) + 1]
                            if next_element[0] == "(" and len(
                                    e) > e.index(element_e.strip()) + 2:
                                new_element = base + " " + e[e.index(element_e.strip())
                                                             + 2]
                                element_e = e[e.index(element_e.strip()) + 2]
                            else:
                                new_element = base + " " + next_element.strip()
                                element_e = e[e.index(element_e) + 1]
                            explanation_set.add(new_element.strip())
                        break
                    # single explanation
                    else:
                        explanation_set.add(element_e.strip())
            global definitions
            save_in_list(definition_set, explanation_set)
            d_set = tuple(definition_set)
            definitions[d_set] = explanation_set


def split_multiples(text):
    """
    Splits text containing multiple definitions or explanations separated by commas, 'and', or 'or' into individual components.

    Args:
        text (str): The text containing potentially multiple definitions or explanations.

    Returns:
        set: A set of individual definitions or explanations extracted from the text.
    """
    result = set()
    
    # Example split logic based on common separators
    if text.__contains__(",") and text.__contains__(" and "):
        elements = text.split(", ")
        for e in elements:
            if not e.__contains__(" and "):
                if '(' in e:
                    e = remove_text_within_brackets(e)
                if len(e.strip()) > 0:
                    result.add(e.strip())
            else:
                el = e.split(" and ")
                for e1 in el:
                    if '(' in e1:
                        e1 = remove_text_within_brackets(e1)
                    if len(e1.strip()) > 0:
                        result.add(e1.strip())
    elif text.__contains__(",") and text.__contains__(" or "):
        elements = text.split(",")
        for e in elements:
            if e.__contains__(" or "):
                el = e.split(" or ")
                for e1 in el:
                    if '(' in e1:
                        e1 = remove_text_within_brackets(e1)
                    if len(e1.strip()) > 0:
                        result.add(e1.strip())
            else:
                if '(' in e:
                    e = remove_text_within_brackets(e)
                if len(e.strip()) > 0:
                    result.add(e.strip())
    elif text.__contains__(" or "):
        result = text.split(" or ")
    elif text.__contains__(" and "):
        result = text.split(" and ")
    return result


def save_in_list(set1, set2):
    """
    Saves processed sets of definitions and explanations into a global list and dictionary for annotation purposes.

    Args:
        set1 (set): A set containing processed definitions.
        set2 (set): A set containing processed explanations corresponding to the definitions.
    """
    for s in set1:
        for s2 in set2:
            global definitions_list
            start = s.find("‘")
            end = s.rfind("’")
            definition = s[start + 1:end].strip()
            if '(' in definition:
                definition = remove_text_within_brackets(definition)
                definition.strip()
            definition = definition.replace('’', '').strip()
            definitions_list.append((definition, s2.strip()))
            # save in the dictionary for the annotations later
            global definitions_dict
            if definition in definitions_dict:
                definitions_dict[definition] += '\n' + s2.strip()
            else:
                definitions_dict[definition] = s2.strip()


def save_in_annotations(definition, explanation):
    """
    Saves a definition and its explanation into the global annotations dictionary.

    Args:
        definition (str): The definition to save.
        explanation (str): The explanation for the definition.
    """
    global annotations
    annotations[definition] = explanation


def get_dictionary():
    """
    Retrieves the global dictionary containing all processed definitions and their annotations.

    Returns:
        dict: The dictionary with definitions as keys and their corresponding annotations as values.
    """
    return definitions_dict


def any_definition_in_text(text):
    """
    Searches for any definitions within a given text, considering variations and abbreviations.
    Definitions are identified based on keys in the global definitions dictionary, accounting for
    both exact matches and capitalized versions of each definition.

    Args:
        text (str): The text to search for definitions.

    Returns:
        set: A set of tuples containing the definition, its explanation, and the start and end positions
             within the text where the definition was found.
    """
    definitions_in_text = set(tuple())
    starts_and_ends = set(tuple()) # Tracks start and end positions of definitions found in the text

    for key, value in definitions_dict.items():
        # Search for abbreviations and select the most relevant part of the definition
        abrv_match = re.search(r'(.*?)\[ABRV\](.*?)\[ABRV\](.*?)', key)

        if abrv_match:
            extracted_text = abrv_match.group(2).strip()
            # Check the number of words in the extracted text
            words = extracted_text.split()
            if len(words) > 1:
                key = extracted_text
            else:
                if abrv_match.group(1):
                    key = abrv_match.group(1).strip()
                elif abrv_match.group(3):
                    key = abrv_match.group(3).strip()
                
        capitalized = key[0].islower() and text.__contains__(key.capitalize())
        if text.__contains__(key) or capitalized:
            d = sub_definitions[key]
            if len(d) != 0:
                for k in d:
                    cap = text.__contains__(k.capitalize()) and k[0].islower()
                    if text.__contains__(k) or cap:
                        if cap:
                            k = k[0].upper() + k[1:]
                        match = re.search(k, text)
                        if match is not None:
                            s, e = match.start(), match.end()
                            if not check_definition_inside(
                                    starts_and_ends, s, e):
                                if k in definitions_dict:
                                    definitions_in_text.add(
                                        (k, definitions_dict[k], s, e))
                                elif cap:
                                    definitions_in_text.add(
                                        (k, definitions_dict[k.lower()], s, e))
                                starts_and_ends.add((s, e))
            if capitalized:
                key = key[0].upper() + key[1:]
            match = re.search(key, text)
            if match is not None:
                start, end = match.start(), match.end()
                if not check_definition_inside(starts_and_ends, start, end):
                    definitions_in_text.add((key, value, start, end))
                    starts_and_ends.add((start, end))
    return definitions_in_text


def check_definition_inside(start_and_end, start, end):
    """
    Determines if a given definition's position overlaps with any previously found definitions in the text.

    Args:
        starts_and_ends (set of tuple): A set containing start and end positions of definitions already found.
        start (int): The start position of the current definition.
        end (int): The end position of the current definition.

    Returns:
        bool: True if the current definition's position overlaps with any existing ones; False otherwise.
    """
    for (s, e) in start_and_end:
        if s == start or e == end:
            return True
        elif start > s and end < e:
            return True
    return False