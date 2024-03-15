import utils
import logging

from sqlalchemy import select, and_, text
flag_yes = 'Y'

CONFIG = utils.loadConfigFromEnv()

def update_opensearch_batch(os_connect, documents, index_name):
    # Extract list of IDs from the batch
    ids = [d['celex_id'] for d in documents]

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
                    "documentProcessedFlag": new_value
                }
            }
        })

    # Send the bulk update request to OpenSearch
    response = os_connect.bulk(index=index_name, body=bulk_request)

    # check the response for errors
    if response.get("errors"):
        logging.info(f"Updating the document processed flags were Unsuccessfull\n")
    else:
        logging.info(f"Updating the document processed flags were successfull\n")