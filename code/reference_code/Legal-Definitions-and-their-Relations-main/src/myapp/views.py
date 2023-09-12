import re
import unicodedata
from collections import Counter, defaultdict
import requests
from bs4 import BeautifulSoup
from django.http import FileResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from myapp.definitions import find_definitions, get_annotations, \
    check_more_definitions_in_text, any_definition_in_text, get_dictionary
from myapp.relations import noun_relations, build_tree, get_hyponymy, get_meronymy, get_synonymy
from .forms import FormCELEX, FormDefinition
from .graph import create_bar_chart, construct_default_graph, construct_relation_graph
from .tests import compare_sentences, compare_definitions_and_relations

site = ""
celex = ""
reg_title = ""
definitions = list(tuple())
relations = ""
annotations = {}
regulation_with_annotations = ""
done_date = ""
regulation_body = ""
frequency_articles = {}
sentences_set = {}
articles_set = {}
articles_set_and_frequency = {}


def index(request):
    if request.method == 'POST':
        form = FormCELEX(request.POST)

        if form.is_valid():
            global celex
            celex = form.cleaned_data['number']
            global site
            site = load_document(celex)
            return HttpResponseRedirect('result/')
    else:
        form = FormCELEX()
    return render(request, 'myapp/index.html', {'form': form})


def original_document(request):
    global site
    return HttpResponseRedirect(site)


def load_document(celex):
    # https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679&from=EN
    new_url = 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:' + celex + '&from=EN'
    return new_url


def result(request):
    extract_text(site)

    bar_chart_path = './myapp/static/myapp/top.png'
    result_template = 'myapp/result.html'

    # create a bar chart with most frequent definitions
    create_bar_chart(most_frequent_definitions(), bar_chart_path, 'Definitions', '# of hits',
                     'Top Most Frequent Definitions')

    context_dict = {'site': site, 'celex': celex, 'definitions': definitions,
                    'num_def': len(annotations.keys()),
                    'title': reg_title, 'date': done_date, 'path': 'myapp/top.png'}
    return render(request, result_template, context_dict)


# for testing purposes of assignment of annotations
def annotations_page(request):
    context_dict = {'body': regulation_body}
    annotation_template = 'myapp/annotations.html' 
    return render(request, annotation_template , context_dict)


# for relation graph
def graph(request):
    defin = get_dictionary()
    image_path = './myapp/static/myapp/graph.png'
    freq_image_path = './myapp/static/myapp/frequency.png'
    if request.method == 'POST':
        form = FormDefinition(request.POST)
        if form.is_valid():
            current_def = form.cleaned_data['definition']

            # construct a graph depending on the relation
            relation = form.cleaned_data['relation']
            if relation == 'meronymy':
                construct_relation_graph(get_meronymy(), defin, current_def, image_path)
            elif relation == 'synonymy':
                construct_relation_graph(get_synonymy(), defin, current_def, image_path)
            else:
                construct_relation_graph(get_hyponymy(), defin, current_def, image_path)

            # construct a frequency graph
            create_bar_chart(get_freq_dict(current_def), freq_image_path, 'Articles', '# of hits', 'Frequency Diagram')

            return render(request, 'myapp/graph.html',
                          {'form': form, 'definitions': defin, 'image_path': 'myapp/graph.png',
                           'freq': 'myapp/frequency.png'})
    else:
        # if the user enters no definition: create a default graph and an empty diagram
        form = FormDefinition()
        construct_default_graph(image_path)
        create_bar_chart(dict(), freq_image_path, 'Articles', '# of hits', 'Frequency Diagram')
    return render(request, 'myapp/graph.html', {'form': form, 'definitions': defin,
                                                'image_path': 'myapp/graph.png', 'freq': 'myapp/frequency.png'})


def extract_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    global reg_title
    reg_title = find_title(soup)
    global definitions
    definitions = find_definitions(soup)
    global done_date
    done_date = soup.find(string=re.compile("Done at"))
    global annotations
    annotations = get_annotations()
    add_annotations_to_the_regulation(soup)
    global regulation_body
    regulation_body = soup.body
    global regulation_with_annotations
    # adding some styling to the annotations
    regulation_with_annotations = '<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <title>Annotations' \
                                  '</title><style>[data-tooltip] {position: relative;}' \
                                  '[data-tooltip]::after {content:' \
                                  'attr(data-tooltip);position: absolute; width: 400px; left: 0; top: 0; background: ' \
                                  '#3989c9; color: #fff; padding: 0.5em; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); ' \
                                  'pointer-events: none; opacity: 0; transition: 1s; } [data-tooltip]:hover::after ' \
                                  '{opacity: 1; top: 2em; z-index: 99999; right: max(20px, calc(100% - 220px));} ' \
                                  '</style></head>"' + str(regulation_body) + '</html>'
    global relations
    relations = "\n".join(noun_relations(definitions))
    # uncomment for evaluation purposes
    # compare_sentences()
    # compare_definitions_and_relations()


def add_annotations_to_the_regulation(soup):
    global sentences_set
    sentences_set.clear()
    global articles_set
    articles_set.clear()
    global articles_set_and_frequency
    articles_set_and_frequency.clear()
    article = ""
    # case if a regulation has div for each article
    if soup.find("div", id="001") is not None:
        for div in soup.find_all("div"):
            div.unwrap()
    for sentence in soup.find_all("p"):
        if check_if_article(sentence.text):
            article = sentence.text
            create_an_article(article)
        for (key, value) in definitions:
            capitalized = key[0].islower() and sentence.text.__contains__(key.capitalize())
            if sentence.text.__contains__(key) or capitalized:
                text = sentence.text
                sentence.clear()
                if not check_more_definitions_in_text(key, text, capitalized):
                    # sort by the starting index
                    defs = sorted(any_definition_in_text(text), key=lambda x: x[2])
                    start_index = 0
                    for (k, v, start, end) in defs:
                        sentence.append(text[start_index:start])
                        tag = create_new_tag(soup, text, k, v, start, end)
                        sentence.append(tag)
                        start_index = end
                        sent = text.replace("\n\n", "\n").strip()
                        sent = unicodedata.normalize("NFKD", sent)

                        if k not in get_dictionary().keys():
                            k = k[0].lower() + k[1:]

                        if k not in sentences_set:
                            sentences_set[k] = set()
                        sentences_set[k].add(sent)
                        if k not in articles_set:
                            articles_set[k] = set()
                        articles_set[k].add(article)
                        if k not in articles_set_and_frequency:
                            articles_set_and_frequency[k] = list()
                        if len(article) != 0:
                            articles_set_and_frequency[k].append(article)

                        global frequency_articles
                        if len(article) != 0:
                            frequency_articles[article].add((key, sent))
                    sentence.append(text[start_index:])


def check_if_article(text):
    if len(text) > 11 or not text.__contains__("Article"):
        return False
    new_text = text.replace("Article", "").strip()
    if new_text.isdigit():
        return True
    return False


def create_an_article(article):
    global frequency_articles
    frequency_articles[article] = set()  # set of tuples (definition, sentence)


# returns a dictionary where a key is an article and a value is a set of tuples (legal definition, number of hits)
def count_article_frequency():
    global frequency_articles
    result_dict = {}
    for key, value in frequency_articles.items():
        counts = defaultdict(int)
        for (k, v) in value:
            counts[k] += 1
        result_dict[key] = [(k, count) for k, count in counts.items()]
    return result_dict


# creates a dictionary of a form Article #: # of hits for the given definition
def get_freq_dict(definition):
    counters = count_article_frequency()
    filtered_dict = {key: {(w, num) for w, num in value if w == definition} for key, value in counters.items()}
    result_dict = {}
    for article in filtered_dict.keys():
        for k, v in filtered_dict[article]:
            if k == definition:
                a = article.replace("Article ", "")
                result_dict[a] = v
    return result_dict


# can be adjusted depending on the processed document
def find_title(s):
    start_class = s.find("p", string=re.compile("REGULATION"))
    if start_class is None:
        return ""
    end_class = s.find("p", string=re.compile("THE EUROPEAN PARLIAMENT AND THE COUNCIL"))
    title = str(start_class.text)
    for element in start_class.next_siblings:
        if element == end_class:
            break
        title = title + " " + element.text
    return title


def create_new_tag(soup, text, key, value, start, end):
    new_tag = soup.new_tag('span')
    new_tag["style"] = "background-color: yellow;"
    new_tag["data-tooltip"] = key + ' ' + value
    new_tag.string = text[start:end]
    return new_tag


def most_frequent_definitions():
    def_list = dict()
    sorted_def = sorted(sentences_set.items(), key=lambda x: len(x[1]), reverse=True)
    top_five_definitions = [definition[0] for definition in sorted_def[:5]]
    for d in top_five_definitions:
        def_list[d] = len(sentences_set[d])
    return def_list


def calculate_the_frequency(key):
    counter = Counter(articles_set_and_frequency[key])
    repeated_elements = [(element, count) for element, count in counter.items()]
    articles = "Definition " + key + " can be found in: Article "
    for (element, count) in repeated_elements:
        num = re.findall(r'\d+', element)
        articles = articles + "".join(num) + "; "
    return articles.replace(" ; ", " ")


def cut_tag(tag):
    new_string = str(tag)
    start = new_string.find(">")
    end = new_string.rfind("<")
    return new_string[start + 1:end]


def get_sentences():
    return sentences_set


# create a txt. file to download with all definitions and their explanations
def download_definitions_file(request):
    with open("file.txt", "w") as file:
        for key, value in annotations.items():
            file.write(key + " " + value + "\n")
    response = FileResponse(open("file.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="file.txt"'
    return response


# create a txt. file to download with all sentences with definitions
def download_sentences(request):
    with open("sentences.txt", "w") as file:
        for key in sentences_set:
            file.write("Definition: " + key + "\n")
            file.write("Total number of text segments including definition: " + str(len(sentences_set[key])) + "\n\n")
            file.write(calculate_the_frequency(key) + "\n\n")
            for sent in sentences_set[key]:
                file.write("\t\t" + sent + "\n\n")
            file.write("\n\n")
    response = FileResponse(open("sentences.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="sentences.txt"'
    return response


# create an HMTL file to download with annotations
def download_annotations(request):
    with open("annotated_page.html", "w") as file:
        file.write(regulation_with_annotations)
    response = FileResponse(open("annotated_page.html", "rb"))
    response['Content-Disposition'] = 'attachment; filename="annotated_page.html"'
    return response


# create a text file to download with all semantic relations listed
def download_relations(request):
    with open("relations.txt", "w") as file:
        file.write(relations)
        file.write("\n\n")
        file.write("Hyponymy Tree: \n")
        hyponymy = get_hyponymy()
        keys = set(hyponymy.keys())
        values = set().union(*hyponymy.values())
        roots = keys.difference(values)
        for root in roots:
            file.write(build_tree(root))
    response = FileResponse(open("relations.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="relations.txt"'
    return response
