import re
import unicodedata

import nltk
from nltk.corpus import wordnet as wn
import spacy

annotations = {}  # only 1:1 relations --> better for pure printing
counter_set = {}  # counts the frequency of each definition
sentences_set = {}
articles_set = {}
sub_definitions = {}  # here we save all the definitions which are the part of another definitions
definitions = {}  # definitions n:m
definitions_dict = {}  # definitions 1:n for annotations
articles_set_and_frequency = {}
definitions_list = list(tuple())  # each element is a tuple (definition, explanation)
nltk.download('wordnet')


def find_definitions(soup):
    global annotations
    annotations = {}
    global definitions_list
    definitions_list = list(tuple())
    global definitions_dict
    definitions_dict = {}
    # extract only the article which contains definitions
    start_class = soup.find("p", string="Definitions")
    end_class = soup.find("p", string=re.compile("Article"))
    # extract the definitions and their explanations
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
    part_def = set()
    for (key, value) in definitions_list:
        if key.__contains__(definition) and key != definition:
            part_def.add(key)
    return part_def


def save_to_sub_definitions():
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
    return int(article.split()[1])


def get_annotations():
    return annotations


def get_sentences():
    return sentences_set


def get_counter():
    return counter_set


def get_articles(key):
    articles = ", ".join(sorted(articles_set[key], key=get_article_number))
    return articles


# return True if only the longest definition (definition2) occurs, but the shortest does not
def check_two_definitions_in_text(definition1, definition2, text):
    if not text.__contains__(definition2):
        return False
    strings = text.split(definition2)
    new_string = "".join(strings)
    if new_string.__contains__(definition1):
        return False
    return True


# return True if only the longest definitions occur in the text, but the shortest does not
def check_more_definitions_in_text(definition1, text, cap):
    if cap:
        definition1 = definition1[0].lower() + definition1[1:]
    definition_set = sub_definitions[definition1]
    for s in definition_set:
        if check_two_definitions_in_text(definition1, s, text):
            return True
    return False


def is_synonym(verb):
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
    # Check if both opening and closing brackets are present
    if re.search(r'\(.*\)', text):
        text = re.sub(r'[()]', '[ABRV]', text)  # Remove both brackets

    # Check if only one bracket is present
    elif re.search(r'\(.*', text):
        text = re.sub(r'\(.*', '', text)  # Remove text after the opening bracket

    return text


def process_definitions(text):
    text = unicodedata.normalize("NFKD", text)
    if text.__contains__("’"):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(
            text.split(";")[0]
        )  # this way only the most important part of the definition will be examined
        definition_set = set()
        explanation_set = set()
        # search for the first verb after the definition
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
            d = [s.strip() for s in definition.split("\n") if s != ""]
            e = [s.strip() for s in explanation.split("\n") if ((s != "") and (len(s) > 3))]
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
                    # multiple explanations
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
    result = set()
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
    global annotations
    annotations[definition] = explanation


def get_dictionary():
    return definitions_dict


def any_definition_in_text(text):
    definitions_in_text = set(tuple())
    starts_and_ends = set(tuple())
    for key, value in definitions_dict.items():
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
    for (s, e) in start_and_end:
        if s == start or e == end:
            return True
        elif start > s and end < e:
            return True
    return False