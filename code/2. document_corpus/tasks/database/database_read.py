from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_
import pandas as pd
from tasks.intext_citations import intext_citation_recognition_relation
from tasks.database.database_insert import insert_postgres
from tasks.database.database_update import update_postgres, update_processed_articles_records
import logging

def process_records_in_batches(database_engine):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    
    # Query must select the article records from the article table
    # where:
    #   1. celex document whose title is blank must not be considered
    #   2. celex_id must be after 2000
    #   3. article text must not be blank
    #   4. article text must comprises of Article followed by the Regulation or Directives or Decisions
    # Everything must be in ascending order of the primary key in article table

    metadata = MetaData()
    metadata.reflect(database_engine)

    articles_table = metadata.tables['lexdrafter_energy_articles']
    titles_table = metadata.tables['lexdrafter_energy_titles']
    article_aux_table = metadata.tables['lexdrafter_energy_article_aux']
    ground_truth_table = metadata.tables['lexdrafter_energy_citation_ground_truth']
    
    # SELECT a.*
    # FROM articles AS a
    # LEFT JOIN titles AS t ON a.celex_id = t.celex_id
    # LEFT JOIN article_aux AS aux ON REPLACE(CONCAT(a.celex_id, '-', a.chapter_number,'-',a.section_number,'-',a.article_number,'-',a.article_fragment_number), '"', '') = aux.article_info
    # WHERE (t.title_text <> '' OR t.title_text IS NOT NULL)
    # AND substring(a.celex_id, 2, 4)::integer > '2000'
    # AND (a.article_text ~ 'Articles? [0-9]+.*?(Regulations?|Directives?|Decisions?)')
    # AND (aux.flag = 'N')
    # AND (a.processed_flag = 'N')
    # ORDER BY a.celex_id ASC, a.chapter_number ASC, a.section_number ASC, a.article_number ASC, a.article_fragment_number ASC;

    query = (
        articles_table.select()
        .select_from(
            articles_table
            .join(
                titles_table,
                articles_table.c.celex_id == titles_table.c.celex_id,
                isouter=True
            )
            .join(
            article_aux_table,
            func.replace(
                func.concat(
                    articles_table.c.celex_id, '-', articles_table.c.chapter_number, '-',
                    articles_table.c.section_number, '-', articles_table.c.article_number, '-',
                    articles_table.c.article_fragment_number
                ), '"', ''
            ) == article_aux_table.c.article_info,
            isouter=True
            )
        )
        .where(
            and_(
                or_(
                    titles_table.c.title_text != '',
                    titles_table.c.title_text == None,
                ),
                #func.substring(articles_table.c.celex_id, 2, 4).cast(Integer) > 2000,
                articles_table.c.article_text.op('~')('Articles? [0-9]+.*?(Regulations?|Directives?|Decisions?)'),
                article_aux_table.c.flag == 'N',
                articles_table.c.processed_flag == 'N'
            )
        )
        .order_by(
            articles_table.c.celex_id.asc(),
            articles_table.c.chapter_number.asc(),
            articles_table.c.section_number.asc(),
            articles_table.c.article_number.asc(),
            articles_table.c.article_fragment_number.asc()
        )
    )

    with database_engine.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(query)

        while True:
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_dict = [dict(row) for row in results_chunk]
            success = False

            try:
                df_intext_citation, records = intext_citation_recognition_relation(results_dict)
                if not df_intext_citation.empty:
                    insert_postgres(database_engine, df_intext_citation, "citation_ground_truth")
                    update_postgres(database_engine, article_aux_table, ground_truth_table)
                
                success = True
            except Exception as e:
                success = False
                logging.error(f'Error while inserting the dataframes in Postgresql due to error {e}')

            if success:    
                update_processed_articles_records(database_engine, articles_table, records)


def opensearch_valid_record_query():
    valid_record_query = {
                    "_source": "english.documentInformation.rawDocument",
                    "query": {
                        "bool": {
                            "must_not": [
                                {
                                "nested": {
                                "path": "english.documentInformation",
                                "query": {
                                    "match_phrase": {
                                    "english.documentInformation.rawDocument": "no raw document present for the eurlex document"
                                    }
                                    }
                                }
                                },
                                {
                                "nested": {
                                "path": "english.documentInformation",
                                "query": {
                                    "match_phrase": {
                                    "english.documentInformation.documentContent": "Unfortunately this document cannot be displayed due to its size"
                                    }
                                    }
                                }
                                }
                            ],
                            "must": [
                                {
                                "nested": {
                                    "path": "english",
                                    "query": {
                                    "match_phrase": {
                                        "english.structureProcessedFlag": "N"
                                    }
                                    }
                                }
                                },
                                {
                                "nested": {
                                    "path": "english",
                                    "query": {
                                    "match_phrase": {
                                        "english.documentFormat": "HTML"
                                    }
                                    }
                                }
                                }
                            ]
                        }
                    }
                }
    
    return valid_record_query