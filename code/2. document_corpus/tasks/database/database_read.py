def opensearch_valid_record_query():
    """
    Constructs a query for OpenSearch to find valid records.

    This function creates a query to be used with an OpenSearch client to retrieve documents
    that have not been processed yet ('structureProcessedFlag' set to 'N'), are in HTML format,
    and do not contain certain phrases indicating the absence or unavailability of the document's content.

    The query filters out documents with the phrase "no raw document present for the eurlex document" 
    in the 'english.documentInformation.rawDocument' field, and documents indicating their content 
    cannot be displayed due to its size in the 'english.documentInformation.documentContent' field.

    Returns:
        dict: A dictionary representing the OpenSearch DSL query for fetching valid document records.
    """
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