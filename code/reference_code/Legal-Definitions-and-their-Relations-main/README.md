# Identification and Visualization of Legal Definitions and their Relations Based on European Regulatory Document
***
This project is based on the [Bachelor Thesis](https://mediatum.ub.tum.de/1656157?query=Anastasiya&show_id=1715461) and introduces an automated prototype capable of extracting legal definitions and their corresponding semantic relations (i.e., hyponymy, meronymy, and synonymy) from the _Regulations of the European Parliament and of the Council_ published on [EUR-Lex](https://eur-lex.europa.eu). We consider this tool beneficial for law experts and the general public, and the approach can be expanded or applied to a wider variety of European regulatory documents.
## Motivation
***
Numerous companies constantly face the problem of rising compliance requirements derived from the IT environment due to digital business activities and processes. The task of business process compliance is to ensure that the organization's business operations comply with the regulatory laws affecting the organization. If the organization fails to achieve compliance, this can result in financial penalties and a loss of investors. Thus, companies attach significant importance to obeying regulatory laws and reviewing the current updates of legal documents, which is a manual process that costs substantial amounts of time and effort. The most considerable disadvantages of the manual procedure are time consumption, costs, and fallibility since the chance of overlooking crucial information or misinterpreting the content is pretty high. Additionally, misjudging or slipping up by observing regulations can result in the organization's forfeiting a large amount of money.

In this project, we focus on digitizing business process compliance and facilitating the interpretation of the legal text by extracting legal definitions and their semantic relations from regulatory documents.
Legal definitions determine the specific lexical terms used within legal texts' discourse utilizing normative rules and are described as a rule at the beginning of each legal act. These terms are not entirely used for precise and effective communication but ensure the correct interpretation
of the legal text. They further aid in comparing the meaning of legal definitions used in other acts, which possibly describe the same concept but with different terms.

![definition drawio](https://github.com/AnastasiyaDmrsk/Identification-and-Visualization-of-Legal-Definitions-and-Relations/assets/87528008/b978470b-f70f-43dd-9c76-5ac086d2002d)
## General Information
***
This project concentrates on three primary assignments: **definition extraction**, including extracting text segments containing legal terms and attaching annotations with explanations to the corresponding definitions, **relation extraction**, and **visualization** of extracted information. The intention is to facilitate the understanding of regulatory documents and accelerate the search for relevant information in legal text. The contributions of this project are as follows: 
+ Approach for legal definitions and semantic relation extraction and visualization, including obtaining **text segments containing legal terms** and **annotating the entered regulation** by applying NLP techniques.
+ Intuitive **web service** that adopts the proposed approach to enable users to access the extracted information referring to legal definitions.
+ Discovery of the frequency of specific definitions and their locations in the form of **frequency diagrams** to accelerate the legal search and provide insight into the regulation's objective.
+ Graphical Visualization of the extracted semantic relations in the form of a **network graph**. 

![Overview drawio](https://github.com/AnastasiyaDmrsk/Identification-and-Visualization-of-Legal-Definitions-and-Relations/assets/87528008/93bbd775-3f6f-40ef-b934-83dd63ff7adf)

### Preparation and Input Verification
Before processing a regulation, the tool validates the entered [CELEX number](https://eur-lex.europa.eu](https://eur-lex.europa.eu/content/tools/eur-lex-celex-infographic-A3.pdf)) for referring to a legislation sector and regulations. If it is the case, the prototype checks whether the document with the number exists and if it contains an article called _"Definitions"_.  

### Definition Extraction
The extraction of legal definitions is implemented with the support of BeautifulSoup HTML parser and spaCy NLP techniques like tokenization, POS tagging, and dependency parsing. For assigning annotations and storing text segments mentioning legal definitions, we applied BeautifulSoup and rewrote the content of detected sentences with a new data-tooltip tag. 

### Relation Extraction 
With the purpose of identifying semantic relations among legal definitions, such as hyponymy, meronymy, and synonymy, we apply spaCy and iterate over each term's explanation, searching for the noun phrases. Depending on the relation pattern, the prototype saves the relations as follows: 
+ **Hyponymy**: _"definition + ' is a hyponym of ' + hyperonym"_
+ **Meronymy**: _"definition + ' is a meronym of ' + holonym"_
+ **Synonymy**: _"definition 1 + ', ' + ... + ', ' + definition n + ' are synonyms'"_

Additionally, the semantic relations are saved as a dictionary for each kind of relation. This is required for the graphical representation.

The resulting text file depicting the obtained semantic relations is sorted alphabetically to simplify the search for the specific legal definition. At the end of the file, users can also find a hyponymy tree to gain a more profound understanding of the terms' meanings.

### Visualization 
To design a layout of the prototype, we applied Django Forms and Bootstrap. A user is supposed to submit a valid CELEX number of a regulation containing an article _"Definitions"_; otherwise, a validation error is raised with an individual message depending on the problem. If the regulation passes the criteria, the prototype handles the document and redirects users to the resulting page. With the purpose of increasing usability, the tool extracts the full title of the entered regulation. Additionally, it displays five options: the user can be redirected to the original source in EUR-Lex or download all the generated output files in the specified format. Furthermore, the prototype renders the statistics relying on the regulation, such as the date of execution and the number of legal definitions, together with more specific statistics referring to the extracted definitions, such as the most frequent definitions and the number of articles where they occur. 

![layout](https://github.com/AnastasiyaDmrsk/Legal-Definitions-and-their-Relations/assets/87528008/9910cf23-5fb8-4bcf-ab0c-4b1bc21e7ca3)

#### Knowledge Graph and Frequency Diagram
For better visualization of extracted semantic relations, the web service provides a knowledge graph for legal definitions. Since a general graph with all semantic relations and terms would be too complex, the user should pick from the list one legal definition and submit it. Additionally, the user can choose which type of relation should be the base of the graph. After the submission, the tool loads a graph, highlighting the entered definition in red and the other legal definitions in pink. Below the graph, the summary of the frequency data referring to the input term is provided.
![graph-2](https://github.com/AnastasiyaDmrsk/Legal-Definitions-and-their-Relations/assets/87528008/d618fa8b-fdfd-478a-936a-2bcc6f7a0ecc)

## Technologies
***
A list of technologies used within the project:
* PyCharm (https://www.jetbrains.com/de-de/pycharm/): Version 2021.2.3
* Python (https://www.python.org/): Version 3.10.0
* BeautifulSoup (https://beautiful-soup-4.readthedocs.io/en/latest/)
* spaCy (https://spacy.io)
* WordNet (https://wordnet.princeton.edu)
* NLTK (https://www.nltk.org)
* Django (https://www.djangoproject.com/): Version 3.2.9
* NetworkX (https://networkx.org)
* Matplotlib (https://matplotlib.org/)
* HTML (https://dev.w3.org/html5/): Version 5.0
* CSS (https://www.w3.org/Style/CSS/)
* Bootstrap (https://getbootstrap.com/): Version 5.1.3
## Installation
***
1. Clone a remote repository 
```bash
git clone https://github.com/AnastasiyaDmrsk/Legal-Definitions-and-their-Relations.git
```
2. Go into the project directory
```bash
cd Legal-Definitions-and-their-Relations
```
3. In case you have already cloned the repository before use:
```bash
git pull
```
4. Go into the src directory 
```bash
cd src
```
5. Install all project dependencies with the help of the package manager [pip](https://pip.pypa.io/en/stable/)
```bash
pip install -r requirements.txt
```
6. Run the server (locally)
```bash
python manage.py runserver
```
Enjoy!
## Evaluation
***
We manually created gold standards for definition and relation extraction evaluation, as well as for sentences extraction. For testing purposes, we selected 18 regulations from EUR-Lex with the filter option "relevance." All the gold standards can be found in `src/myapp/gold_standard` directory. 

1. In order to test a specific regulation, in `tests.py` `_gold_` (for definition and relation extraction) or `_gold_sentences_` (for sentences extraction) variable should be adjusted depending on the CELEX number of the regulation.  
2. Then go to `views.py` and uncomment line 138 for senteces extraction evaluation (`compare_sentences()`) or line 139 for definition and relation extraction (`compare_definitions_and_relations()`).
3. Run the project and enter a CELEX number to start processing a regulation.
4. Compare the output results in the terminal, which are empty if the gold standard file is the same as the resulting file. 

The prototype was able to identify and extract legal definitions in 99.8% of cases as well as their semantic relations in 96.7% of cases, using NLP techniques, particularly dependency parsing, tokenization, and POS-tagging.
