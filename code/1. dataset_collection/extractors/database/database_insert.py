from extractors.libraries import *


def opensearch_en_insert(os_index, index_name, celex_details):
    """
    Inserts CELEX document information into the specified OpenSearch index.

    This function iterates through a list of CELEX details (dictionaries)
    and prepares bulk insertion actions for the OpenSearch index.
    It extracts relevant information like title, ELI link, and dates
    from the provided data and builds the document structure.

    Args:
        es_index (object): An established connection to the OpenSearch instance.
        index_name (str): Name of the OpenSearch index where documents are inserted.
        celex_details (list): List of dictionaries containing CELEX document information.

    Returns:
        bool: True if insertion is successful, False otherwise.
    """
    success = False
    actions = []

    for celex_information in celex_details:
        action = {"index": {"_index": index_name, "_id": celex_information["_id"]}}
        doc = {
            "english": {
                "title": (
                    "no title present for the eurlex document"
                    if celex_information["EN"]["metadata"]["title"] is None
                    else celex_information["EN"]["metadata"]["title"]
                ),
                "eliLink": celex_information["EN"]["metadata"]["ELI_LINK"],
                "dateOfDocument": celex_information["EN"]["metadata"][
                    "Date of document: "
                ],
                "effectDate": celex_information["EN"]["metadata"]["Date of effect: "],
                "signatureDate": celex_information["EN"]["metadata"][
                    "Date of signature: "
                ],
                "deadline": celex_information["EN"]["metadata"]["Deadline: "],
                "validityEndDate": celex_information["EN"]["metadata"][
                    "Date of end of validity: "
                ],
                "eurovocDescriptor": (
                    "no eurovoc descriptor present for the eurlex document"
                    if celex_information["EN"]["metadata"]["EUROVOC descriptor: "]
                    is None
                    else celex_information["EN"]["metadata"]["EUROVOC descriptor: "]
                ),
                "subjectMatter": (
                    "no subject matter present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Subject matter: "] is None
                    else celex_information["EN"]["metadata"]["Subject matter: "]
                ),
                "directoryCode": (
                    "no directory code present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Directory code: "] is None
                    else celex_information["EN"]["metadata"]["Directory code: "]
                ),
                "author": celex_information["EN"]["metadata"]["Author: "],
                "form": celex_information["EN"]["metadata"]["Form: "],
                "additionalInformation": celex_information["EN"]["metadata"][
                    "Additional information: "
                ],
                "procedureNumber": celex_information["EN"]["metadata"][
                    "Procedure number: "
                ],
                "link": celex_information["EN"]["metadata"]["\nLink\n"],
                "treaty": celex_information["EN"]["metadata"]["Treaty: "],
                "legalBasis": (
                    "no legal basis present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Legal basis: "] is None
                    else celex_information["EN"]["metadata"]["Legal basis: "]
                ),
                "proposal": celex_information["EN"]["metadata"]["Proposal: "],
                "amendedBy": celex_information["EN"]["metadata"]["Amended by: "],
                "allConsolidateVersions": (
                    "no consolidated version present for the eurlex document"
                    if celex_information["EN"]["metadata"][
                        "All consolidated versions: "
                    ]
                    is None
                    else celex_information["EN"]["metadata"][
                        "All consolidated versions: "
                    ]
                ),
                "instrumentsCited": (
                    "no instrument cited present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Instruments cited: "]
                    is None
                    else celex_information["EN"]["metadata"]["Instruments cited: "]
                ),
                "authenticLanguage": (
                    "no authentic language present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Authentic language: "]
                    is None
                    else celex_information["EN"]["metadata"]["Authentic language: "]
                ),
                "addressee": (
                    "no addressee present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Addressee: "] is None
                    else celex_information["EN"]["metadata"]["Addressee: "]
                ),
                "dateOfNotification": celex_information["EN"]["metadata"][
                    "Date of notification: "
                ],
                "responsibleBody": celex_information["EN"]["metadata"][
                    "Responsible body: "
                ],
                "relatedDocuments": (
                    "no related documents present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Related document(s): "]
                    is None
                    else celex_information["EN"]["metadata"]["Related document(s): "]
                ),
                "internalComment": (
                    "no internal comment present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Internal comment: "] is None
                    else celex_information["EN"]["metadata"]["Internal comment: "]
                ),
                "affectedByCase": (
                    "no affected by case present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Affected by case: "] is None
                    else celex_information["EN"]["metadata"]["Affected by case: "]
                ),
                "relatedInstruments": (
                    "no related instruments present for the eurlex document"
                    if celex_information["EN"]["metadata"][
                        "Subsequent related instruments: "
                    ]
                    is None
                    else celex_information["EN"]["metadata"][
                        "Subsequent related instruments: "
                    ]
                ),
                "internalReference": (
                    "no internal reference present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Internal reference: "]
                    is None
                    else celex_information["EN"]["metadata"]["Internal reference: "]
                ),
                "dateOfTransposition": celex_information["EN"]["metadata"][
                    "Date of transposition: "
                ],
                "depositary": (
                    "no depositary present for the eurlex document"
                    if celex_information["EN"]["metadata"]["Depositary: "] is None
                    else celex_information["EN"]["metadata"]["Depositary: "]
                ),
                "internalProcedures": (
                    "no internal procedures present for the eurlex document"
                    if celex_information["EN"]["metadata"][
                        "Internal procedures based on this legislative basic act"
                    ]
                    is None
                    else celex_information["EN"]["metadata"][
                        "Internal procedures based on this legislative basic act"
                    ]
                ),
                "coAuthor": celex_information["EN"]["metadata"]["Co author: "],
                "structureProcessedFlag": celex_information["EN"]["metadata"][
                    "structureProcessedFlag"
                ],
                "documentProcessedFlag": celex_information["EN"]["metadata"][
                    "documentProcessedFlag"
                ],
                "documentFormat": (
                    "none"
                    if celex_information["EN"]["documentInformation"]["document_format"]
                    is None
                    else celex_information["EN"]["documentInformation"][
                        "document_format"
                    ]
                ),
                "documentInformation": {
                    "documentContent": (
                        "no document content present for the eurlex document"
                        if celex_information["EN"]["documentInformation"][
                            "documentContent"
                        ]
                        is None
                        else celex_information["EN"]["documentInformation"][
                            "documentContent"
                        ]
                    ),
                    "rawDocument": (
                        "no raw document present for the eurlex document"
                        if celex_information["EN"]["documentInformation"]["rawDocument"]
                        is None
                        else celex_information["EN"]["documentInformation"][
                            "rawDocument"
                        ]
                    ),
                },
            }
        }
        actions.append(action)
        actions.append(doc)
    try:
        os_index.bulk(index=index_name, body=actions)
        success = True
        return success
    except Exception as e:
        success = False
        logging.error(
            "Bulk Indexing failed to push in OpenSearch due to error {}".format(e)
        )
        return success
