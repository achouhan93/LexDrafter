# identifying semantic relations using spaCy and semantic role labeling
# inspired by spacy documentation: https://spacy.io/usage/spacy-101
import os.path
import re
import unicodedata

import spacy
from myapp.definitions import get_dictionary
from collections import defaultdict
import csv

hyponymy = {}
meronymy = {}
synonymy = {}
all_relations = list()
dash = False


def noun_relations(definitions):
    global hyponymy
    hyponymy.clear()
    global all_relations
    all_relations = list()
    nlp = spacy.load("en_core_web_sm")
    for (key, value) in definitions:
        # case when definitions are already defined in the previous regulations
        if key in value and value.__contains__("as defined in point"):
            all_relations.append(key + " is a hyponym of " + key)
            hypernym = key
            if hypernym not in hyponymy and hypernym != "":
                hyponymy[hypernym] = set()
            if hypernym != "":
                hyponymy[hypernym].add(key)
            continue
        # case when definition is not previously defined
        sentence = prepare_sentence(value)
        doc = nlp(sentence)
        global dash
        dash = False
        meronymy = False
        previous_noun = ""
        for noun in doc.noun_chunks:
            if meronymy:
                save_to_meronymy(noun, key)
                break
            # in case of enumeration
            if noun.root.text == "following":
                continue
            if (noun.root.text == "type" or noun.root.text == "kind" or noun.root.text == "form") \
                    and doc[noun.end:][0].text == "of":
                continue
            if (noun.root.text == "part" or noun.root.text == "piece" or noun.root.text == "portion") \
                    and doc[noun.end:][0].text == "of":
                meronymy = True
                continue
            if single_relation(doc[noun.end:]) and not dash:
                save_to_hyponymy(noun, key)
                break
            # noun chucks do not support dashes (e.g non-compliance), so we have to cache it
            if dash:
                if previous_noun == "":
                    previous_noun = noun.text
                    continue
                elif noun.text == "-":
                    continue
                else:
                    hypernym = previous_noun + "-" + noun.text
                    all_relations.append(key + " is a hyponym of " + hypernym)
                    if hypernym not in hyponymy and hypernym != "":
                        hyponymy[hypernym] = set()
                    if hypernym != "":
                        hyponymy[hypernym].add(key)
                    dash = False
                    if single_relation(doc[noun.end:]):
                        break
                    else:
                        continue
            save_to_hyponymy(noun, key)
    find_synonyms()
    create_csv_file()
    return sorted(set(all_relations))


def find_synonyms():
    synonym_keys = defaultdict(list)
    for k, v in get_dictionary().items():
        synonym_keys[v].append(k)
    result_synonyms = [
        tuple(keys) for keys in synonym_keys.values() if len(keys) > 1
    ]
    global all_relations
    for synonyms in result_synonyms:
        s = ""
        if synonyms[0] not in synonymy or synonymy.values():
            synonymy[synonyms[0]] = set()
        for synonym in synonyms:
            if synonym != synonyms[0]:
                synonymy[synonyms[0]].add(synonym)
            s += synonym + ", "
        all_relations.append(s[:-2] + " are synonyms")


def save_to_hyponymy(noun, key):
    hyponym_noun = ""
    for noun_token in noun:
        if noun_token.pos_ != "PRON" and noun_token.pos_ != "DET":
            if noun_token.text == "‘":
                continue
            if (noun_token.nbor() is not None and noun_token.nbor().text
                    == "-") or noun_token.text == "-":
                hyponym_noun += noun_token.text
            else:
                hyponym_noun += noun_token.text + " "
    if hyponym_noun != "":
        all_relations.append(
            key + " is a hyponym of " +
            hyponym_noun.strip().replace(" , ", ", ").replace(" '", "'"))
    hypernym = hyponym_noun.strip()
    if hypernym not in hyponymy and hypernym != "":
        hyponymy[hypernym] = set()
    if hypernym != "":
        hyponymy[hypernym].add(key)


def save_to_meronymy(noun, key):
    meronym_noun = ""
    for noun_token in noun:
        if noun_token.pos_ != "PRON" and noun_token.pos_ != "DET":
            if noun_token.text == "‘":
                continue
            if (noun_token.nbor() is not None and noun_token.nbor().text
                    == "-") or noun_token.text == "-":
                meronym_noun += noun_token.text
            else:
                meronym_noun += noun_token.text + " "
    if meronym_noun != "":
        all_relations.append(key + " is a meronym of " + meronym_noun.strip())
    m = meronym_noun.strip()
    if m not in meronymy and m != "":
        meronymy[m] = set()
    if m != "":
        meronymy[m].add(key)


def single_relation(doc):
    # if abbreviations are used in the explanation
    if len(doc) > 1 and doc[0].text == ')':
        doc = doc[1:]
    # check for dash
    global dash
    if doc[0].text == '-' and not dash:
        dash = True
        return False
    # check for , or and
    if doc[0].text == ',':
        # cases like including, with, in ...
        if len(doc) > 1 and (doc[1].dep_ == "prep" or doc[1].dep_ == "mark"
                             or doc[1].pos_ == "VERB"):
            return True
        else:
            return False
    if doc[0].text == "or" or doc[0].text == "and":
        return False
    if doc[0].text == '(':
        return False
    else:
        return True


# to simplify the search for the relations, trying to detect a pattern "for purpose: explanation"
def prepare_sentence(value):
    sentence = unicodedata.normalize("NFKD", value)
    sentence = sentence.replace("- ", "-")
    sentence = sentence.replace(" -", "-")
    pattern = r'for[\s+\w+]+:'
    if re.search(pattern, sentence) and not sentence.__contains__("for which"):
        index = sentence.find("for")
        sentence = sentence[index:]
        index = sentence.find(":")
        sentence = sentence[index + 1:]
    if sentence.__contains__(": in the context of") or sentence.__contains__(": as regards") \
            or sentence.__contains__(": for"):
        sentence = sentence[sentence.find(",") + 1:]
    return sentence


def get_hyponymy():
    return hyponymy


def get_meronymy():
    return meronymy


def get_synonymy():
    return synonymy


def build_tree(node, depth=0):
    result = '| ' * depth + node + '\n'
    if node not in hyponymy:
        return result
    for child in hyponymy[node]:
        result += build_tree(child, depth + 1)
    return result


# for evaluation of definitions and relations
def create_csv_file():
    file_path = './myapp/results/relation.csv'
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Definition', 'Relation'])
        for relation in sorted(set(all_relations)):
            if relation.__contains__(" is a hyponym of "):
                definition = relation.split(" is a hyponym of ")[0]
            elif relation.__contains__(" is a meronym of "):
                definition = relation.split(" is a meronym of ")[0]
            else:
                definition = relation.split(",")[0]
            writer.writerow([definition, relation])
    return file_path
