# This is the code from the github repository: https://github.com/AnastasiyaDmrsk/Legal-Definitions-and-their-Relations/tree/main

import re
import os
import utils
import logging
import argparse
import unicodedata
import requests

from time import time
from tqdm import tqdm
from collections import Counter, defaultdict

from bs4 import BeautifulSoup
from sqlalchemy import Table, MetaData

from definitions import (
    find_definitions,
    get_annotations,
    check_more_definitions_in_text,
    any_definition_in_text,
    get_dictionary,
)
from relations import *
from tasks import *

log_buffer = []


class Processor:
    def __init__(self, opensearch_connection, postgres_connection, index):
        self.os_connection = opensearch_connection
        self.pg_connection = postgres_connection
        self.index_name = index
        self.scroll_size = 100
        self.batch_size = 50
        self.url = " "
        self.celex = ""
        self.reg_title = ""
        self.definitions = list(tuple())
        self.relations = ""
        self.annotations = {}
        self.regulation_with_annotations = ""
        self.done_date = ""
        self.regulation_body = ""
        self.frequency_articles = {}
        self.sentences_set = {}
        self.articles_set = {}
        self.articles_set_and_frequency = {}
        self.all_relations = list()

        self.doc_info = []
        self.term_info = []
        self.key_sentences_dict = {}
        self.explanation_info = []
        self.relation_info = []

    def load_document(self):
        # https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679&from=EN
        self.url = (
            "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:"
            + self.celex
            + "&from=EN"
        )

    def check(self):
        if self.celex[0] != "3":
            logging.info(
                f"{self.celex[0]} type of sector is not supported for document number {self.celex}"
            )
            log_buffer.append(
                f"{self.celex[0]} type of sector is not supported for document number {self.celex}"
            )
            return False

        if not ((self.celex[1] != "1") or (self.celex[1] != "2")):
            logging.info(
                f"Year of a regulation is invalid for document number {self.celex}"
            )
            log_buffer.append(
                f"Year of a regulation is invalid for document number {self.celex}"
            )
            return False

        # check whether the regulation exists or not
        new_url = (
            "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:"
            + self.celex
            + "&from=EN"
        )
        soup = BeautifulSoup(requests.get(new_url).text, "html.parser")
        try:
            if (
                soup.find("title")
                .getText()
                .__contains__("The requested document does not exist")
            ):
                logging.info(
                    f"The celex document {self.celex} does not exist in HTML format"
                )
                log_buffer.append(
                    f"The celex document {self.celex} does not exist in HTML format"
                )
                return False
        except:
            logging.info(
                f"The celex document {self.celex} does not contain title in the HTML document"
            )
            log_buffer.append(
                f"The celex document {self.celex} does not contain title in the HTML document"
            )
            return False

        # check whether a regulation contains a chapter definitions or not
        if soup.find("p", string="Definitions") is None:
            logging.info(
                f"The celex document {self.celex} does not contain legal definitions and cannot be processed."
            )
            log_buffer.append(
                f"The celex document {self.celex} does not contain legal definitions and cannot be processed."
            )
            return False

        return True

    def extract_text(self):
        if self.check():
            logging.info(
                f"Extraction of the definitions initiated for the celex document {self.celex}"
            )
            self.response = requests.get(self.url)
            soup = BeautifulSoup(self.response.text, "html.parser")
            self.reg_title = self.find_title(soup)
            self.definitions = find_definitions(soup)
            self.done_date = soup.find(string=re.compile("Done at"))
            self.annotations = get_annotations()
            self.add_annotations_to_the_regulation(soup)
            self.regulation_body = soup.body

            # adding styles to the annotations
            self.regulation_with_annotations = (
                '<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <title>Annotations'
                "</title><style>[data-tooltip] {position: relative;}"
                "[data-tooltip]::after {content:"
                "attr(data-tooltip);position: absolute; width: 400px; left: 0; top: 0; background: "
                "#3989c9; color: #fff; padding: 0.5em; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); "
                "pointer-events: none; opacity: 0; transition: 1s; } [data-tooltip]:hover::after "
                "{opacity: 1; top: 2em; z-index: 99999; right: max(20px, calc(100% - 220px));} "
                '</style></head>"' + str(self.regulation_body) + "</html>"
            )

            self.all_relations = noun_relations(self.definitions)
            self.relations = "\n".join(self.all_relations)
            return True
        else:
            return False

    def add_annotations_to_the_regulation(self, soup):
        self.sentences_set.clear()
        self.articles_set.clear()
        self.articles_set_and_frequency.clear()
        self.key_sentences_dict.clear()
        article = ""

        # case if a regulation has div for each article
        if soup.find("div", id="001") is not None:
            for div in soup.find_all("div"):
                div.unwrap()
        for sentence in soup.find_all("p"):
            if self.check_if_article(sentence.text):
                article = sentence.text.strip()
                self.create_an_article(article)
            for key, value in self.definitions:
                abrv_match = re.search(r"(.*?)\[ABRV\](.*?)\[ABRV\](.*?)", key)

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

                capitalized = key[0].islower() and sentence.text.__contains__(
                    key.capitalize()
                )
                if sentence.text.__contains__(key) or capitalized:
                    text = sentence.text.strip()
                    sentence.clear()
                    if not check_more_definitions_in_text(key, text, capitalized):
                        defs = sorted(any_definition_in_text(text), key=lambda x: x[2])
                        start_index = 0
                        for k, v, start, end in defs:
                            sentence.append(text[start_index:start].strip())
                            tag = self.create_new_tag(soup, text, k, v, start, end)
                            sentence.append(tag)
                            start_index = end
                            sent = text.replace("\n\n", "\n").strip()
                            sent = unicodedata.normalize("NFKD", sent)

                            if k not in get_dictionary().keys():
                                k = k[0].lower() + k[1:]

                            if k not in self.key_sentences_dict:
                                self.key_sentences_dict[k] = {}

                            if len(article) == 0:
                                new_article = "Not Article"
                            else:
                                new_article = article

                            if new_article not in self.key_sentences_dict[k]:
                                self.key_sentences_dict[k][new_article] = []
                                self.key_sentences_dict[k][new_article].append(sent)
                            else:
                                self.key_sentences_dict[k][new_article].append(sent)

                            self.key_sentences_dict[k][new_article] = list(
                                set(self.key_sentences_dict[k][new_article])
                            )

                            if k not in self.sentences_set:
                                self.sentences_set[k] = set()
                            self.sentences_set[k].add(sent)

                            if k not in self.articles_set:
                                self.articles_set[k] = set()
                            self.articles_set[k].add(new_article)

                            if k not in self.articles_set_and_frequency:
                                self.articles_set_and_frequency[k] = list()

                            if len(article) != 0:
                                self.articles_set_and_frequency[k].append(new_article)

                            if len(article) != 0:
                                self.frequency_articles[new_article].add((key, sent))

                        sentence.append(text[start_index:])

    def check_if_article(self, text):
        if len(text) > 11 or not text.__contains__("Article"):
            return False
        new_text = text.replace("Article", "").strip()
        if new_text.isdigit():
            return True
        return False

    def create_an_article(self, article):
        self.frequency_articles[article] = set()  # set of tuples (definition, sentence)

    def find_title(self, s):
        start_class = s.find("p", string=re.compile("REGULATION"))
        if start_class is None:
            return ""
        end_class = s.find(
            "p", string=re.compile("THE EUROPEAN PARLIAMENT AND THE COUNCIL")
        )
        title = str(start_class.text).strip()
        for element in start_class.next_siblings:
            if element == end_class:
                break
            title = title + " " + element.text.strip()
        return title

    def create_new_tag(self, soup, text, key, value, start, end):
        new_tag = soup.new_tag("span")
        new_tag["style"] = "background-color: yellow;"
        new_tag["data-tooltip"] = key + " " + value
        new_tag.string = text[start:end]
        return new_tag

    def most_frequent_definitions(self):
        def_list = dict()
        sorted_def = sorted(
            self.sentences_set.items(), key=lambda x: len(x[1]), reverse=True
        )
        top_five_definitions = [definition[0] for definition in sorted_def[:5]]
        for d in top_five_definitions:
            def_list[d] = len(self.sentences_set[d])
        return def_list

    def calculate_the_frequency(self, key):
        counter = Counter(self.articles_set_and_frequency[key])
        repeated_elements = [(element, count) for element, count in counter.items()]
        articles = "Definition " + key + " can be found in: Article "
        for element, count in repeated_elements:
            num = re.findall(r"\d+", element)
            articles = articles + "".join(num) + "; "
        return articles.replace(" ; ", " ")

    def document_processing(self, definition_class, document_class):
        document_id = document_class.last_celex_doc_id + 1

        # Document Information
        doc = [
            {
                "id": document_id,
                "celex_id": self.celex,
                "celex_url": self.url,
                "original_text": self.response.text,
                "annotated_text": self.regulation_with_annotations,
            }
        ]
        self.doc_info.extend(doc)

        # Term and Explanation Information
        for key, value in self.definitions:

            def_id, term_flag = definition_class.term_exist(key, document_id)

            if not term_flag:
                existing_term = next(
                    (
                        entry
                        for entry in self.term_info
                        if entry["term_id"] == def_id and entry["doc_id"] == document_id
                    ),
                    False,
                )
                if not existing_term:
                    # Term Information
                    term_information = []
                    term_information = [
                        {
                            "term_id": def_id,
                            "doc_id": document_id,
                            "term": key.strip(),
                            "sentences": (
                                self.key_sentences_dict[key]
                                if key in self.key_sentences_dict
                                else {"not used": "not used"}
                            ),
                        }
                    ]
                    self.term_info.extend(term_information)

                existing_entry = next(
                    (
                        entry
                        for entry in self.explanation_info
                        if entry["term_id"] == def_id and entry["doc_id"] == document_id
                    ),
                    False,
                )
                key_present = any(key in terms for terms in self.annotations.keys())

                # Definition Information
                if (not existing_entry) and key_present:
                    for terms, definition in self.annotations.items():
                        explanantion_information = []
                        if key in terms:
                            value = definition
                            break
                    explanantion_information = [
                        {
                            "term_id": def_id,
                            "doc_id": document_id,
                            "explanation": (
                                value.strip() if len(value.split(" ")) > 3 else ""
                            ),
                            "definition_type": (
                                "dynamic"
                                if "as defined in" in value.strip()
                                else "static"
                            ),
                            "reference_list": [],
                        }
                    ]
                    self.explanation_info.extend(explanantion_information)

        # Relation Information
        for relation in sorted(set(self.all_relations)):
            if relation.__contains__(" is a hyponym of "):
                relationship = relation.split(" is a hyponym of ")
                relation_term = relationship[1].strip()
                term_id = [
                    term[1]["term_id"]
                    for term in definition_class.term.items()
                    if term[1]["term"] == relationship[0].strip()
                ][0]
                relationship_id = 1
                relation_information = [
                    {
                        "doc_id": document_id,
                        "term_id1": term_id,
                        "term": relation_term,
                        "relationship_id": relationship_id,
                    }
                ]
                self.relation_info.extend(relation_information)

            elif relation.__contains__(" is a meronym of "):
                relationship = relation.split(" is a meronym of ")
                relation_term = relationship[1].strip()
                term_id = [
                    term[1]["term_id"]
                    for term in definition_class.term.items()
                    if term[1]["term"] == relationship[0].strip()
                ][0]
                relationship_id = 2
                relation_information = [
                    {
                        "doc_id": document_id,
                        "term_id1": term_id,
                        "term": relation_term,
                        "relationship_id": relationship_id,
                    }
                ]
                self.relation_info.extend(relation_information)
            else:
                relation = relation.replace(" are synonyms", "")
                relationship = relation.split(",")
                relationship_id = 3

                for i in range(len(relationship)):
                    for j in range(i + 1, len(relationship)):
                        term_id = [
                            term[1]["term_id"]
                            for term in definition_class.term.items()
                            if term[1]["term"] == relationship[i].strip()
                        ][0]
                        relation_term = [
                            term[1]["term_id"]
                            for term in definition_class.term.items()
                            if term[1]["term"] == relationship[j].strip()
                        ][0]
                        relation_information = [
                            {
                                "doc_id": document_id,
                                "term_id1": term_id,
                                "term": relation_term,
                                "relationship_id": relationship_id,
                            }
                        ]
                        self.relation_info.extend(relation_information)

        document_class.last_celex_doc_id = document_id

        return True


def secondsToText(secs):
    days = secs // 86400
    hours = (secs - days * 86400) // 3600
    minutes = (secs - days * 86400 - hours * 3600) // 60
    seconds = secs - days * 86400 - hours * 3600 - minutes * 60
    result = (
        ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "")
        + ("{0} hour{1}, ".format(hours, "s" if hours != 1 else "") if hours else "")
        + (
            "{0} minute{1}, ".format(minutes, "s" if minutes != 1 else "")
            if minutes
            else ""
        )
        + (
            "{0} second{1}, ".format(round(seconds, 2), "s" if seconds != 1 else "")
            if seconds
            else ""
        )
    )
    return result


def main(argv=None):
    try:
        CONFIG = utils.loadConfigFromEnv()

        if not os.path.exists(CONFIG["LOG_PATH"]):
            os.makedirs(CONFIG["LOG_PATH"])
            print(f'created: {CONFIG["LOG_PATH"]} directory.')

        logging.basicConfig(
            filename=CONFIG["LOG_EXE_PATH"],
            filemode="a",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%y %H:%M:%S",
            level=logging.INFO,
        )

        pg_connection = postgres_connection()

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-d",
            "--definitionextraction",
            help="extracting the logical structure of the document",
            action="store_true",
        )

        args = parser.parse_args()

        pg_connection = postgres_connection()

        os_connection = opensearch_connection()
        database = CONFIG["DB_LEXDRAFTER_INDEX"]
        scroll_size = 50
        batch_size = 50

        if args.definitionextraction:
            # ---------------- Reading the existing Information ----------------- #
            reading_vocab_start_time = time()
            logging.info(f"started reading vocab")
            pg_read = PostgresReader(pg_connection)
            last_doc_id, docs = pg_read.get_document()
            celex_docs = DocProcessor(docs, last_doc_id)

            last_term_id, terms = pg_read.get_terms()
            definition = DefinitionProcessor(terms, last_term_id)

            logging.info(
                f"finished reading vocab and took: {secondsToText(time()- reading_vocab_start_time)}!\n"
            )

            document_processor = Processor(os_connection, pg_connection, database)

            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(
                f"Process to extracting the defnition of terms present in the celex documents started"
            )
            pg_insert = PostgresInsert(pg_connection)

            search_params = opensearch_query()  # extract all the celex ids

            # Execute the initial search request
            response = os_connection.search(
                index=database, scroll="50m", size=scroll_size, body=search_params
            )

            # Get the scroll ID and hits from the initial search request
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            total_docs = response["hits"]["total"][
                "value"
            ]  # Get the total number of documents

            # Loop to extract the celex id from opensearch
            with tqdm(total=total_docs) as pbar:
                while hits:
                    logging.info(f"Considered {len(hits)} documents for processing")
                    document_count = len(hits)

                    hits = check_for_processed_records(pg_connection, hits)
                    logging.info(
                        f"{document_count - len(hits)} documents already processed. \n {len(hits)} documents are considered for processing"
                    )

                    batch_progress = []
                    hits = check_for_existing_records(pg_connection, hits)

                    logging.info(
                        f"{document_count - len(hits)} documents already exist. \n {len(hits)} new documents are considered for processing"
                    )

                    non_existing_count = len(hits)

                    logging.info(
                        f"{non_existing_count} documents are considered for processing"
                    )

                    if len(hits) == 0:
                        progress_status = True
                    else:
                        progress_status = False

                    if not progress_status:
                        document_processor.doc_info.clear()
                        document_processor.term_info.clear()
                        document_processor.explanation_info.clear()
                        document_processor.relation_info.clear()

                        for idBatch in tqdm(
                            [
                                hits[i : i + batch_size]
                                for i in range(0, len(hits), batch_size)
                            ],
                            desc=f"Inserting definition information of batch (size={len(hits) if len(hits) < batch_size else batch_size})",
                        ):
                            for information in tqdm(idBatch):
                                record_progress = []
                                document_processor.celex = information["_id"]
                                logging.info(
                                    f"\n Started the extraction of the definitions present in the celex document {document_processor.celex}"
                                )
                                document_processor.load_document()
                                status = document_processor.extract_text()

                                if status:
                                    document_processor.document_processing(
                                        definition, celex_docs
                                    )
                                    record_progress = [
                                        {
                                            "celex_id": document_processor.celex,
                                            "status": "definition processed",
                                        }
                                    ]
                                    batch_progress.extend(record_progress)
                                    logging.info(
                                        f"Completed the extraction of the definitions present in the celex document {document_processor.celex} \n"
                                    )
                                else:
                                    record_progress = [
                                        {
                                            "celex_id": document_processor.celex,
                                            "status": log_buffer[-1],
                                        }
                                    ]
                                    batch_progress.extend(record_progress)
                                    logging.info(
                                        f"Error while extracting the definitions present in the celex document {document_processor.celex}. See logs for more information \n"
                                    )

                        logging.info(
                            f"\n Starting the insertion of the information into database for the batch"
                        )

                        try:
                            if batch_progress:
                                logging.info(
                                    f"\n Starting the insertion of batch progress"
                                )
                                pg_insert.insert_information(batch_progress, "progress")
                                logging.info(
                                    "Completed the insertion of batch information"
                                )

                            if document_processor.doc_info:
                                logging.info(
                                    f"\n Starting the insertion of document information"
                                )
                                pg_insert.insert_information(
                                    document_processor.doc_info, "document"
                                )
                                logging.info(
                                    f"Completed the insertion of document information"
                                )

                            if document_processor.term_info:
                                logging.info(
                                    f"\n Starting the insertion of term information"
                                )
                                pg_insert.insert_information(
                                    document_processor.term_info, "term"
                                )
                                logging.info(
                                    f"Completed the insertion of term information"
                                )

                            if document_processor.explanation_info:
                                logging.info(
                                    f"\n Starting the insertion of explanation information"
                                )
                                pg_insert.insert_information(
                                    document_processor.explanation_info, "explanation"
                                )
                                logging.info(
                                    f"Completed the insertion of explanation information"
                                )

                            if document_processor.relation_info:
                                logging.info(
                                    f"\n Starting the insertion of relation information"
                                )
                                pg_insert.insert_information(
                                    document_processor.relation_info, "relation"
                                )
                                logging.info(
                                    f"Completed the insertion of relation information"
                                )

                            if document_processor.doc_info:
                                logging.info(
                                    f"\n Starting the updation of the documentProcessedFlag in Opensearch"
                                )
                                update_opensearch_batch(
                                    os_connection, document_processor.doc_info, database
                                )
                                logging.info(
                                    f"Completed the updation of documentProcessedFlag"
                                )
                        except Exception as e:
                            logging.info(
                                f"\n Error during insertion of the information in database. Error: {e}"
                            )
                            raise e

                    pbar.update(document_count)

                    # Paginate through the search results using the scroll parameter
                    response = os_connection.scroll(scroll_id=scroll_id, scroll="50m")
                    hits = response["hits"]["hits"]
                    scroll_id = response["_scroll_id"]

    finally:
        pg_connection.dispose()


if __name__ == "__main__":
    main()
