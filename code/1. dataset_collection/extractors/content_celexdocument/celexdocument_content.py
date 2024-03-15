from extractors.libraries import *

def get_file_by_id(lang, celex_id):
    """
    Extracts content from a EUR-Lex document with the given CELEX ID and language.

    Prioritizes retrieval from HTML format if available, otherwise downloads and extracts from PDF.

    Args:
        lang (str): Language code for the document (e.g., "EN", "FR", "DE").
        celex_id (str): CELEX number of the document to extract.

    Returns:
        dict: Dictionary containing:
            - rawDocument: The raw HTML or None if not available.
            - documentContent: The extracted text content.
            - document_format: The format of the extracted document ("HTML" or "PDF").
    """

    # Dictionary to save info for each iteration
    dict = {}

    # Tracking dictonary which type of document (HTML / PDF / NONE) in respective language
    track_dict = {}
    track_dict['celex_id'] = celex_id  

########################################################################################################
    # Preparing URLs based on given number & Language.
    url_HTML = f'https://eur-lex.europa.eu/legal-content/{lang}/TXT/HTML/?uri=CELEX:{celex_id}'
    url_PDF = f'https://eur-lex.europa.eu/legal-content/{lang}/TXT/PDF/?uri=CELEX:{celex_id}'
########################################################################################################
    try:
        # First try to get HTML information
        HTML_content = requests.get(url_HTML).text
        if 'The requested document does not exist.' in HTML_content:
            pass
            # If there is no HTML available, then try to get PDF info.
            pdf_info = requests.get(url_PDF)
        
            if 'The requested document does not exist.' in pdf_info.text:
                # If PDF is also not available , then Raise Exception.
                raise Exception
            
            document = None
            track_dict[lang] = "PDF"

            # Save the PDF document
            working_dir = os.getcwd()
            directory = os.path.join(working_dir, 'Scrapped_Data_Information')
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            pdf_directory = os.path.join(directory, 'PDF_Documents')
            if not os.path.exists(pdf_directory):
                os.makedirs(pdf_directory)

            pdf_document_path = os.path.join(pdf_directory, celex_id + "_" + lang + ".pdf" )

            save_pdf = open(pdf_document_path, 'wb')
            save_pdf.write(pdf_info.content)
            save_pdf.close()

            read_pdf = PyPDF2.PdfFileReader(pdf_document_path, strict=False)

            all_pages = {}
            num = read_pdf.getNumPages()
            for page in range(num):
                data = read_pdf.getPage(page)

                # extract the page's text
                page_text = data.extractText()

                # put the text data into the dict
                all_pages[page] = page_text
            
            content = ''
            for page in all_pages:
                content = content + '[NEW PAGE] ' + all_pages[page] 
            
            document_content = content   
        else:
            # Saving HTML File (if available)
            if "docHtml" in HTML_content:
                HTML_text = BeautifulSoup(HTML_content, "html.parser").find("div", {"id": "docHtml"})
                document_content = HTML_text.text
                document = HTML_content
            else:
                HTML_text = BeautifulSoup(HTML_content, "html.parser")
                document_content = HTML_text.text
                document = HTML_content
            
            track_dict[lang] = "HTML"

        dict['rawDocument'] = document
        dict['documentContent'] = document_content

    except :
        track_dict[lang] = None
        dict['rawDocument'] = None
        dict['documentContent'] = None
    
    dict['document_format'] = track_dict[lang]
    logging.info(track_dict)

    return dict

def get_pdf_url(lang, celex_ids):
    """
    Generates a list of PDF URLs for the given CELEX IDs and language.

    Args:
        lang (str): Language code for the documents.
        celex_ids (list): List of CELEX numbers to generate URLs for.

    Returns:
        list: List of PDF URLs for the specified CELEX IDs and language.
    """

    # Dictionary to save info for each iteration
    celex_id_pdf = []

    for celex in celex_ids:
        # Preparing URLs based on given number & Language.
        url_PDF = f'https://eur-lex.europa.eu/legal-content/{lang}/TXT/PDF/?uri=CELEX:{celex}'
        celex_id_pdf.append(url_PDF)
    
    return celex_id_pdf