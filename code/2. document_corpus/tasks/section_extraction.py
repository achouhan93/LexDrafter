# import src.config => Throwing Error
import regex as re

# Regular Expression to extract the logical structure of the document

# class *doc-ti comprises of Title and Annex headings present in the html document
doc_regex = re.compile(r".*doc-ti") 

# class *ti-grseq-1 comprises of the structure description, 
# i.e., Chapter name or Section name or Article name
# present in the html document
doc_name_regex = re.compile(r".*ti-grseq-1")

# class *normal comprises of all the textual content present in a section body
normal_regex = re.compile(r".*normal")

# class *ti-section-1 provides the heading of each section, i.e., 
# CHAPTER or Section
chapter_regex = re.compile(r".*ti-section-1")

# class *ti-section-2 provides the heading description of each section, i.e., 
# CHAPTER heading or Section heading
chapter_name_regex = re.compile(r".*ti-section-2")

# class *ti-art provides the articles present in the document
article_regex = re.compile(r'.*\bti-art\b')

# class *sti-art provides the articles heading in the document
article_name_regex = re.compile(r'.*\bsti-art\b')

# regex to check if links are present in the text
link_regex = re.compile(r'<a href')

def title_extraction(document):
    '''
    Title Extraction from the Document
    '''
    # Extract Document Title
    section = {}
    title_name = ''
    doc_title = document.find_all(class_ = doc_regex)

    # Title Name extracted
    for title in doc_title:
        if 'ANNEX' in title.text:
            break
        title_name = title_name + ' ' +title.text 
    
    possible_title = title_name.replace(u"\xa0", u" ").replace(u"\n", u" ").strip()
    
    section['category'] = "title"
    section['name'] = "title"
    section['content'] = possible_title

    return section

def document_information(parsed_document, document_list):
    section = {}
    section['category'] = "recital"
    section['name'] = "recital"
    content = ""
    previous_class = ""

    paragraphs = parsed_document.find_all('p')

    for paragraph in paragraphs:
        if 'class' not in paragraph.attrs:
            continue
            
        if normal_regex.search(paragraph.attrs['class'][0]):
            for index in range(len(paragraph.contents)):
                if not link_regex.search(str(paragraph.contents[index])):
                    content = content + " " + str(paragraph.contents[index])
                
                previous_class = paragraph.attrs['class'][0]
        elif (
                (
                    normal_regex.search(previous_class) or
                    chapter_name_regex.search(previous_class)
                )
            and
                (
                    chapter_regex.search(paragraph.attrs['class'][0]) or
                    article_regex.search(paragraph.attrs['class'][0]) or 
                    doc_regex.search(paragraph.attrs['class'][0])
                )
            ):
            section['content'] = content.replace(u"\xa0", u" ")

            if 'name' not in section:
                section['name'] = " "
            document_list.append(section)
            section = {}
            content = ''
            
            if paragraph.contents[0] == "\n":  
                section['category'] = paragraph.contents[1].text
            else:
                section['category'] = paragraph.contents[0]
                
            previous_class = paragraph.attrs['class'][0]
        elif (
                (
                chapter_name_regex.search(paragraph.attrs['class'][0]) or
                article_name_regex.search(paragraph.attrs['class'][0]) or
                doc_name_regex.search(paragraph.attrs['class'][0]) 
                )
            and
                ( len(paragraph.contents) != 0 )
            ):
            if paragraph.contents[0] == "\n":  
                section['name'] = paragraph.contents[1].text
            else:
                section['name'] = paragraph.contents[0]
            
            previous_class = paragraph.attrs['class'][0]
        
    section['content'] = content.replace(u"\xa0", u" ")
    if 'name' not in section:
        section['name'] = " "

    document_list.append(section)

    return document_list