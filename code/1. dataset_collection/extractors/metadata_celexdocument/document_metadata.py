from extractors.libraries import *

def clean_metadata (dict_obj):
    # """"""""""
    # Functionality: Cleaning of Metadata and assigning "NA" to the metadata values whose values are not present in Eur-Lex
    #
    # Signature of the function:
    #  Input: 
    #       dict_obj: Dictionary object with the metadata extracted from the Eur-lex website for a specific Celex Document
    # 
    #  Output:
    #       dict_obj: Cleaned Metadata for a Celex Document
    # """""""""" 
    document_metadata = ['title','ELI_LINK','Date of document: ','Date of signature: ','Date of effect: ','Deadline: ','Date of end of validity: ','EUROVOC descriptor: ','Subject matter: ','Directory code: ','Author: ','Form: ','Additional information: ','Procedure number: ','\nLink\n','Treaty: ','Legal basis: ','Proposal: ','Amended by: ','All consolidated versions: ','Instruments cited: ','Authentic language: ','Addressee: ','Date of notification: ','Responsible body: ','Related document(s): ','Internal comment: ','Affected by case: ','Subsequent related instruments: ','Internal reference: ','Date of transposition: ','Depositary: ','Internal procedures based on this legislative basic act','Co author: ']
    document_dates = ['Date of document: ','Date of effect: ','Date of signature: ','Deadline: ','Date of transposition: ','Date of end of validity: ', 'Date of notification: ']
        
    for key in document_metadata:
        if key in dict_obj:
            # If it is a date field, clean it further
            if key in document_dates:
                date_info = dict_obj[key].split(';')
                try:
                    date_obj = datetime.datetime.strptime(date_info[0], '%d/%m/%Y').date()
                    if isinstance(date_obj, datetime.date):
                        date_obj = datetime.datetime.strptime(date_info[0], '%d/%m/%Y')
                        formatted_date = date_obj.strftime('%Y/%m/%d')
                        dict_obj[key] = formatted_date
                    else:
                        dict_obj[key] = None
                except ValueError:
                    dict_obj[key] = None
        else:
            dict_obj[key] = None

    dict_obj['EUROVOC descriptor: '] = None if dict_obj['EUROVOC descriptor: '] is None else re.sub('  +', ', ',dict_obj['EUROVOC descriptor: '])
    dict_obj['Subject matter: '] = None if dict_obj['Subject matter: '] is None else re.sub('  +', ', ',dict_obj['Subject matter: '])
    dict_obj['Instruments cited: '] = None if dict_obj['Instruments cited: '] is None else re.sub('  +', ', ',dict_obj['Instruments cited: '])

# Function to extract the metadata of the list of Celex Numbers provided

def get_metadata(lang, celex_id):
    # """"""""""
    # Functionality: Extracting the metadata and content present in the Celex document from the Eur-lex website
    #
    # Signature of the function:
    #  Input: 
    #       list_of_celexs: List of Celex Number whose metadata needs to be extracted
    # 
    #  Output:
    #       details: List of Metadata and Content present in the Celex Document from the Eur-lex website
    # """""""""" 
    logging.info("Execution of Extraction of Metadata for respective Celex Document - Started")

    # Dictonary to structure data for mongo DB
    metadata = {}
    
    # Preparing URL for that CELEX_Number
    url = f'https://eur-lex.europa.eu/legal-content/{lang}/ALL/?uri=CELEX:{celex_id}'
    metadata_request = requests.get(url)
    # HTML for that information
    soup = BeautifulSoup(metadata_request.text, "html.parser")

    metadata['documentProcessedFlag']  = 'N'
    metadata['structureProcessedFlag'] = 'N'
      
    ########################################################################################################
    # parsing the Title of the document.
    try:
        t = soup.find_all("p", attrs={ "id": "title"})[0]
        metadata['title'] = t.text.replace('\n', ' ').replace('\r', '')
        
    except:
        try:
            t = soup.find_all("p", attrs={ "id": "originalTitle"})[0]
            metadata['title'] = t.text.replace('\n', ' ').replace('\r', '').strip()
            logging.error(" originalTitle considered in " + celex_id )

        except :
            metadata['title'] = None

    ########################################################################################################
    # parsing ELI_LINK of the document
    try:    
        t = soup.find_all("a", attrs={ "title": "Gives access to this document through its ELI URI."})[0]
        metadata['ELI_LINK'] = t.text.replace('\n', ' ').replace('\r', '').strip()
    except :
        metadata['ELI_LINK'] = None

    ########################################################################################################
    # parsing all metadata Information
    try:
        t = soup.find_all("dl", attrs={ "class": "NMetadata"})

        for tag in t:
            titles  = tag.find_all("dt")
            values = tag.find_all("dd")
            for t ,v in zip(titles, values):
                if t.text == 'Amendment to: ':
                    pass
                else:
                    metadata[t.text]  = v.text.replace('\n', ' ').replace('\r', '').strip()
    except :
        logging.error(" Major Error in " + str(celex_id) + " --- NMetadata class not available.")

    ########################################################################################################
    # fill non existing tags with "NA" and clean MetaData
    clean_metadata(metadata)
    logging.info(" Completed Extracting MetaData Information for : " + str(celex_id))
    
    return metadata