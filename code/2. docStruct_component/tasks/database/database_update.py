import utils
import logging

flag_yes = 'Y'

CONFIG = utils.loadConfigFromEnv()


def update_opensearch_batch(os_connect, documents):
    """
    Updates the 'structureProcessedFlag' field in OpenSearch documents in bulk.

    This function takes a list of document identifiers and updates their 'structureProcessedFlag'
    field to 'Y', indicating that these documents have been processed for structure. It constructs
    a bulk update request and sends it to OpenSearch, logging the outcome of the operation.

    Args:
        os_connect (OpenSearch): The OpenSearch connection object to execute the bulk update.
        documents (list): A list of dictionaries, each containing the document ID as its key.

    The function logs the result of the bulk update operation, indicating success or failure.
    """
    index_name = CONFIG['DB_LEXDRAFTER_INDEX']

    # Extract list of IDs from the batch
    ids = [list(d.keys())[0] for d in documents]

    # Define the new value for the "nlpProcessedFlag" field
    new_value = flag_yes

    # Create a bulk update request for the specified documents
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

    # Check the response for errors and log the outcome
    if response.get("errors"):
        logging.info(f"Updating the structure processed flags were Unsuccessfull\n")
    else:
        logging.info(f"Updating the structure processed flags were successfull\n")