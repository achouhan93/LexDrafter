import matplotlib.pyplot as plt
import regex
from typing import List
from collections import Counter
from database_connection import postgres_connection, opensearch_connection
import utils
from tqdm import tqdm
from sqlalchemy import Table, MetaData, select, or_, and_
import json
import numpy as np


def identify_publishing_year(celex_id) -> int:
    """
    Identifies the publishing year of a CELEX document based on its ID.

    Args:
        celex_id (str): The CELEX ID of the document.

    Returns:
        int: The year of publication extracted from the CELEX ID.

    Raises:
        ValueError: If the CELEX ID does not contain a valid year.
    """
    # Take the last four digits of the sections just before the first letter
    relevant_segment = regex.search(r"(.*?)[A-Z]", celex_id)
    if relevant_segment:
        year_candidate = int(relevant_segment[1][-4:])
    else:
        raise ValueError(f"{celex_id} gives problems!")

    if not 1940 < year_candidate <= 2023:
        raise ValueError(f"{celex_id} gave year {year_candidate} as candidate.")

    return year_candidate


def identify_publishing_document(celex_id) -> int:
    """
    Identifies the document type of a CELEX document based on its ID.

    Args:
        celex_id (str): The CELEX ID of the document.

    Returns:
        str: The document type identifier extracted from the CELEX ID.
    """
    # Take the last four digits of the sections just before the first letter
    relevant_segment = regex.search(r"(.*?)[A-Z]", celex_id)
    if relevant_segment:
        document_candidate = relevant_segment[0][-1:]
    else:
        raise ValueError(f"{celex_id} gives problems!")

    return document_candidate


def plot_temporal_distribution(celex_ids: List[str], definition_celex: List[str]):
    """
    Plots the temporal distribution of legislative documents and those containing definitions.

    Args:
        celex_ids (List[str]): A list of CELEX IDs for legislative documents.
        definition_celex (List[str]): A list of CELEX IDs for legislative documents containing definitions.
    """
    # Use the celex IDs to determine the years that are available.
    celex_id_distribution = Counter(
        [identify_publishing_year(celex_id) for celex_id in celex_ids]
    )
    definition_distribution = Counter(
        [identify_publishing_year(celex_id) for celex_id in definition_celex]
    )

    x_labels = [
        year
        for year in range(
            min(list(celex_id_distribution.keys())),
            max(list(celex_id_distribution.keys())) + 1,
        )
    ]
    celex_bars = [celex_id_distribution.get(year, 0) for year in x_labels]
    definition_bars = [definition_distribution.get(year, 0) for year in x_labels]

    fig, ax = plt.subplots()
    ax.bar(
        x_labels, celex_bars, label="legislative documents", color="#1b9e77", width=0.9
    )
    ax.bar(
        x_labels,
        definition_bars,
        label="legislative documents comprising definition",
        bottom=celex_bars,
        color="#d95f02",
        width=0.9,
    )

    ax.set_xlim(min(x_labels) - 1, max(x_labels) + 1)
    plt.legend()
    plt.savefig("../insights/year_distribution.png", dpi=400)
    plt.show()


def plot_pie_distribution(definition_celex: List[str]):
    """
    Plots a pie distribution of document types among legislative documents containing definitions.

    Args:
        definition_celex (List[str]): A list of CELEX IDs for legislative documents containing definitions.
    """
    definition_document_distribution = Counter(
        [identify_publishing_document(celex_id) for celex_id in definition_celex]
    )

    # Sort the dictionary by values in descending order
    sorted_distribution = dict(
        sorted(
            definition_document_distribution.items(), key=lambda x: x[1], reverse=True
        )
    )

    # Separate the top N items and group the rest into "Other"
    top_n_items = dict(list(sorted_distribution.items())[:3])
    other_count = sum(list(sorted_distribution.values())[3:])

    # Include "Other" in the top N items
    top_n_items["Other"] = other_count

    labels = list(top_n_items.keys())
    sizes = list(top_n_items.values())

    colors = ["#1b9e77", "#ff7f0e", "#8c564b", "#9467bd"]

    label_definitions = {
        "A": "Opinions",
        "B": "Budget",
        "C": "Declarations",
        "D": "Decisions",
        "E": "Common and foreign security policy",
        "F": "Police and judicial cooperation in criminal matters",
        "G": "Resolutions",
        "H": "Recommendations",
        "J": "Non-oppositioin to a notified joint venture",
        "K": "ECSC recommendations",
        "L": "Directives",
        "M": "Commission decisions - Non-opposition to a notified concentration",
        "O": "ECB guidelines",
        "Q": "Institutional arrangements",
        "R": "Regulations",
        "S": "ECSC decisions of general interest",
        "X": "Other documents published in OJ-L",
        "Y": "Other documents published in the OJ C series",
    }

    replaced_labels = [label_definitions.get(label, label) for label in labels]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))
    ax.pie(sizes, colors=colors, autopct="%1.1f%%", startangle=180)
    ax.legend(replaced_labels, title="Types of legislative documents", loc="best")

    plt.savefig(
        "../insights/document_distribution_pie.png", dpi=400, bbox_inches="tight"
    )
    plt.show()


def opensearch_extraction(os_connection, database):
    """
    Extracts CELEX IDs from an OpenSearch database.

    Args:
        os_connection: The OpenSearch connection object.
        database (str): The name of the OpenSearch index.

    Returns:
        List[str]: A list of extracted CELEX IDs.
    """
    celex_ids_list = []

    # Execute the initial search request
    response = os_connection.search(index=database, scroll="50m", size=1000, body={})

    # Get the scroll ID and hits from the initial search request
    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]
    total_docs = response["hits"]["total"]["value"]  # Get the total number of documents

    with tqdm(total=total_docs) as pbar:
        while hits:
            if len(hits) == 0:
                progress_status = True
            else:
                progress_status = False

            if not progress_status:
                batch_celex_id = []
                batch_celex_id = [record["_id"] for record in tqdm(hits)]
                celex_ids_list.extend(batch_celex_id)

                pbar.update(len(hits))

                # Paginate through the search results using the scroll parameter
                response = os_connection.scroll(scroll_id=scroll_id, scroll="50m")
                hits = response["hits"]["hits"]
                scroll_id = response["_scroll_id"]

    return celex_ids_list


def postgresql_extraction(pg_connection):
    """
    Extracts CELEX IDs from a PostgreSQL database for documents containing specific terms within their text.

    Args:
        pg_connection: The PostgreSQL connection object.

    Returns:
        List[str]: A list of CELEX IDs for documents matching the extraction criteria.
    """
    metadata = MetaData()
    metadata.reflect(pg_connection)

    articles_table = metadata.tables["lexdrafter_energy_articles"]
    definition_celex = []

    definition_query = select(articles_table.c.celex_id).where(
        and_(
            or_(
                articles_table.c.article_title == "Definitions",
                articles_table.c.article_title == "Definition",
            ),
            or_(
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+"
                ),
                articles_table.c.article_text.op("~")("([‘]?[“]?[^]+[’]?[”]?):[^.]+"),
            ),
            articles_table.c.article_text != "",
        )
    )

    with pg_connection.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(definition_query)

        while True:
            results_list = []
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_list = [row[0] for row in results_chunk]
            definition_celex.extend(results_list)

    scope_query = select(articles_table.c.celex_id).where(
        and_(
            articles_table.c.article_title == "Scope",
            articles_table.c.article_text.op("~")("‘[^’]+’:[^.]+"),
            articles_table.c.article_text != "",
        )
    )

    with pg_connection.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(scope_query)

        while True:
            results_list = []
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_list = [row[0] for row in results_chunk]
            definition_celex.extend(results_list)

    fishing_zones_query = select(articles_table.c.celex_id).where(
        and_(
            articles_table.c.article_title == "Fishing zones",
            or_(
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+"
                ),
                articles_table.c.article_text.op("~")(
                    "([‘]?[“]?[^]+[’]?[”]?) are as defined[^.]+"
                ),
            ),
            articles_table.c.article_text != "",
        )
    )

    with pg_connection.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(
            fishing_zones_query
        )

        while True:
            results_list = []
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_list = [row[0] for row in results_chunk]
            definition_celex.extend(results_list)

    return definition_celex


def main(argv=None):
    """
    Main function to orchestrate the extraction and plotting of document distributions.

    This function coordinates the extraction of CELEX IDs from both OpenSearch and PostgreSQL databases,
    and plots the temporal distribution and pie distribution of document types.
    """
    try:
        CONFIG = utils.loadConfigFromEnv()
        database = CONFIG["DB_LEXDRAFTER_INDEX"]

        pg_connection = postgres_connection()
        os_connection = opensearch_connection()

        total_count = 0

        with open("./opensearch_celex.json", "r") as file:
            celex_ids = json.load(file)

        # definition_celex_ids = postgresql_extraction(pg_connection)
        with open("./postgres_celex.json", "r") as file:
            definition_celex_ids = json.load(file)

        plot_temporal_distribution(celex_ids, definition_celex_ids)
        plot_pie_distribution(definition_celex_ids)

    finally:
        pg_connection.dispose()


if __name__ == "__main__":
    main()
