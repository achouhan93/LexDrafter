def opensearch_en_mapping():
    """
    Defines the mapping for the OpenSearch index used to store extracted EUR-Lex documents.

    This function defines the schema for the index, specifying how different 
    fields will be analyzed and stored. The mapping utilizes a custom analyzer 
    named "modified_analyzer" to handle text data effectively.

    Returns:
        dict: The mapping definition for the OpenSearch index.
    """
    os_mapping = {
        "settings": {
            "number_of_shards":1,
            "number_of_replicas":0,
            "analysis": {
                "analyzer": {
                    "modified_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "preserve_original"
                    ]
                    }
                },
                "filter": {
                    "preserve_original": {
                    "type": "word_delimiter",
                    "preserve_original": True
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "english": {
                    "type": "nested",
                    "properties": {
                        "title": {
                            "type": "text"
                        }, 
                        "eliLink": {
                            "type": "keyword",
                            "null_value": "no eli link present for the eurlex document"
                        }, 
                        "dateOfDocument": {
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "effectDate": {
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "signatureDate":{
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "deadline": {
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "validityEndDate": {
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "eurovocDescriptor": {
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "subjectMatter": {
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "directoryCode": {
                            "type": "text"
                        },
                        "author": {
                            "type": "keyword",
                            "null_value": "no authors present for the eurlex document"
                        },
                        "form": {
                            "type": "keyword",
                            "null_value": "no form present for the eurlex document"
                        },
                        "additionalInformation":{
                            "type": "keyword",
                            "null_value": "no additional information present for the eurlex document"
                        },
                        "procedureNumber": {
                            "type": "keyword",
                            "null_value": "no procedure number present for the eurlex document"
                        },
                        "link": {
                            "type": "keyword",
                            "null_value": "no link present for the eurlex document"
                        },
                        "treaty": {
                            "type": "keyword",
                            "null_value": "no treaty present for the eurlex document"
                        },
                        "legalBasis": {
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "proposal": {
                            "type": "keyword",
                            "null_value": "no proposal present for the eurlex document"
                        },
                        "amendedBy":{
                            "type": "keyword",
                            "null_value": "no amended by present for the eurlex document"
                        },
                        "allConsolidateVersions":{
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "instrumentsCited": {
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "authenticLanguage":{
                            "type": "text"
                        },
                        "addressee":{
                            "type": "text"
                        },
                        "dateOfNotification":{
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "responsibleBody":{
                            "type": "keyword",
                            "null_value": "no responsible body present for the eurlex document"
                        },
                        "relatedDocuments": {
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "internalComment":{
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "affectedByCase":{
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "relatedInstruments":{
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "internalReference":{
                            "type": "text",
                            "analyzer": "modified_analyzer"
                        },
                        "dateOfTransposition":{
                            "type": "date",
                            "format": "yyyy/MM/dd",
                            "null_value": "1900/01/01"
                        },
                        "depositary":{
                            "type": "text"
                        },
                        "internalProcedures":{
                            "type": "text"
                        },
                        "coAuthor":{
                            "type": "keyword",
                            "null_value": "no co author present for the eurlex document"
                        },
                        "structureProcessedFlag": {
                            "type": "keyword",
                            "null_value": "N"
                        },
                        "documentProcessedFlag": {
                            "type": "keyword",
                            "null_value": "N"
                        },
                        "documentFormat":{
                            "type": "keyword",
                            "null_value": "NONE"
                        },
                        "documentInformation": {
                            "type": "nested",
                            "properties": {
                                "documentContent": {
                                    "type": "text",
                                    "analyzer": "modified_analyzer"
                                },
                                "rawDocument": {
                                    "type": "text"
                                },
                                "summaryContent": {
                                    "type": "text",
                                    "analyzer": "modified_analyzer"
                                },
                                "rawSummary": {
                                    "type": "text"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return os_mapping