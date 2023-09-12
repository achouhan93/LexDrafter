import utils
import logging

from sqlalchemy import select, and_, text
flag_yes = 'Y'

CONFIG = utils.loadConfigFromEnv()

def update_postgres(database_engine, aux_table, ground_table):
    """
    
    """
    #UPDATE article_aux AS aux
    # SET flag = 'Y'
    # WHERE EXISTS (
    # SELECT 1
    # FROM citation_ground_truth AS t
    # WHERE t.record_identifier = aux.article_info
    # );

    update_query = (
        aux_table.update()
        .where(
            aux_table.c.article_info.in_(
                select([ground_table.c.record_identifier])
            )
        )
        .values(
            flag=flag_yes
        )
    )

    with database_engine.connect() as conn:
        conn.execute(update_query)

def update_processed_articles_records(database_engine, article_table, records_list):
    
    with database_engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        
        for record in records_list:
            update_statement = (article_table.update()
                .where(
                    and_(
                        article_table.c.celex_id == record['citing_celex_id'],
                        article_table.c.chapter_number == record['citing_chapter'],
                        article_table.c.section_number == record['citing_section'],
                        article_table.c.article_number == record['citing_article'],
                        article_table.c.article_fragment_number == record['citing_article_fragment']
                    )
                )
                .values(
                    processed_flag=flag_yes
                )
            )

            conn.execute(update_statement)
        
        # Commit the changes
        trans.commit()


def update_opensearch_batch(os_connect, documents):
    index_name = CONFIG['DB_INDEX']

    # Extract list of IDs from the batch
    ids = [list(d.keys())[0] for d in documents]

    # define the new value for the "nlpProcessedFlag" field
    new_value = flag_yes

    # create a bulk update request for the specified documents
    bulk_request = []

    for doc_id in ids:
        bulk_request.append({
        "update": {
            "_index": index_name,
            "_id": doc_id
        }
        })
        bulk_request.append({
            "doc": {
                "english":{
                    "structureProcessedFlag": new_value
                }
            }
        })

    # Send the bulk update request to OpenSearch
    response = os_connect.bulk(index=index_name, body=bulk_request)

    # check the response for errors
    if response.get("errors"):
        logging.info(f"Updating the structure processed flags were Unsuccessfull\n")
    else:
        logging.info(f"Updating the structure processed flags were successfull\n")