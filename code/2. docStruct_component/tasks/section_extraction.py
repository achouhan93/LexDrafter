import regex as re

# Regular expressions to identify various components of the document's structure in HTML format.

# Matches the `doc-ti` class for titles and annex headings
doc_regex = re.compile(r".*doc-ti")

# Matches the `ti-grseq-1` class for structural descriptions
# (e.g., Chapter, Section, Article names)
doc_name_regex = re.compile(r".*ti-grseq-1")

# Matches the `normal` class for textual content within section bodies
normal_regex = re.compile(r".*normal")

# Matches the `ti-section-1` class for section headings (e.g., CHAPTER, Section)
chapter_regex = re.compile(r".*ti-section-1")

# Matches the `ti-section-2` class for detailed section headings
chapter_name_regex = re.compile(r".*ti-section-2")

# Matches the `ti-art` class for articles within the document
article_regex = re.compile(r".*\bti-art\b")

# Matches the `sti-art` class for article headings
article_name_regex = re.compile(r".*\bsti-art\b")

# Matches links within the text to identify hyperlinks
link_regex = re.compile(r"<a href")


def title_extraction(document):
    """
    Extracts the title of a document from its HTML representation.

    Args:
        document (BeautifulSoup): The parsed HTML document.

    Returns:
        dict: A dictionary containing the extracted title information with keys 'category', 'name', and 'content'.
    """
    # Extract Document Title
    section = {}
    title_name = ""
    doc_title = document.find_all(class_=doc_regex)

    # Accumulate the document title from the elements matched by the `doc_regex`
    for title in doc_title:
        if "ANNEX" in title.text:
            break
        title_name = title_name + " " + title.text

    # Clean and format the title text
    possible_title = title_name.replace("\xa0", " ").replace("\n", " ").strip()

    # Structure the title information in a dictionary
    section["category"] = "title"
    section["name"] = "title"
    section["content"] = possible_title

    return section


def document_information(parsed_document, document_list):
    """
    Extracts information from a parsed HTML document excluding the title, categorizing each section based on its content and structure.

    Args:
        parsed_document (BeautifulSoup): The parsed HTML document.
        document_list (list): The list to which extracted document sections are appended.

    Returns:
        list: An updated list with dictionaries representing different sections of the document, including their categories, names, and content.
    """
    section = {}
    section["category"] = "recital"
    section["name"] = "recital"
    content = ""
    previous_class = ""

    paragraphs = parsed_document.find_all("p")

    for paragraph in paragraphs:
        # Skip paragraphs without a class attribute
        if "class" not in paragraph.attrs:
            continue

        # Accumulate content for sections matching the `normal` class
        if normal_regex.search(paragraph.attrs["class"][0]):
            for index in range(len(paragraph.contents)):
                if not link_regex.search(str(paragraph.contents[index])):
                    content = content + " " + str(paragraph.contents[index])

                previous_class = paragraph.attrs["class"][0]

        # Check for transitions to new sections based on class changes
        elif (
            normal_regex.search(previous_class)
            or chapter_name_regex.search(previous_class)
        ) and (
            chapter_regex.search(paragraph.attrs["class"][0])
            or article_regex.search(paragraph.attrs["class"][0])
            or doc_regex.search(paragraph.attrs["class"][0])
        ):
            section["content"] = content.replace("\xa0", " ")

            # Ensure there is a 'name' key in the section
            if "name" not in section:
                section["name"] = " "
            document_list.append(section)

            # Reset for the next section
            section = {}
            content = ""

            if paragraph.contents[0] == "\n":
                section["category"] = paragraph.contents[1].text
            else:
                section["category"] = paragraph.contents[0]

            previous_class = paragraph.attrs["class"][0]
        # Capture names for chapters, articles, or structural descriptions
        elif (
            chapter_name_regex.search(paragraph.attrs["class"][0])
            or article_name_regex.search(paragraph.attrs["class"][0])
            or doc_name_regex.search(paragraph.attrs["class"][0])
        ) and (len(paragraph.contents) != 0):
            if paragraph.contents[0] == "\n":
                section["name"] = paragraph.contents[1].text
            else:
                section["name"] = paragraph.contents[0]

            previous_class = paragraph.attrs["class"][0]

    section["content"] = content.replace("\xa0", " ")
    if "name" not in section:
        section["name"] = " "

    document_list.append(section)

    return document_list
