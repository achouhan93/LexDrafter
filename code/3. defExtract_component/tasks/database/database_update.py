import utils
import logging

from sqlalchemy import select, and_, text

# Define the flag value indicating processing completion
flag_yes = 'Y'

# Load configuration from environment variables or other sources
CONFIG = utils.loadConfigFromEnv()

def update_opensearch_batch(os_connect, documents, index_name):
    """
    Updates a batch of documents in an OpenSearch index to mark them as processed.

    This function constructs a bulk update request to set the 'documentProcessedFlag'
    for a list of documents, indicating they have been processed by NLP services or similar.

    Parameters:
        os_connect: The OpenSearch connection object.
        documents (list of dict): A list of document dictionaries, where each dictionary contains
                                  at least the 'celex_id' of the document to be updated.
        index_name (str): The name of the OpenSearch index where the documents are stored.

    Logs an informational message indicating the success or failure of the bulk update.
    """
    # Extract list of IDs from the batch
    ids = [d['celex_id'] for d in documents]

    # Define the new value for the "documentProcessedFlag" field
    new_value = flag_yes

    # Create a bulk update request for the specified documents
    bulk_request = []

    for doc_id in ids:
        # Append the command to update the specific document by ID
        bulk_request.append({
        "update": {
            "_index": index_name,
            "_id": doc_id
        }
        })
        # Append the new data to be updated in the document
        bulk_request.append({
            "doc": {
                "english":{
                    "documentProcessedFlag": new_value
                }
            }
        })

    # Send the bulk update request to OpenSearch and capture the response
    response = os_connect.bulk(index=index_name, body=bulk_request)

    # Check the response for errors and log the outcome
    if response.get("errors"):
        logging.info(f"Updating the document processed flags were Unsuccessfull\n")
    else:
        logging.info(f"Updating the document processed flags were successfull\n")