import os

import csv
from . import views

# choose a gold standard file to test
gold = 'myapp/gold_standard/32021R0444.csv'
result = 'myapp/results/relation.csv'


def compare_definitions_and_relations():
    with open(gold, 'r') as file:
        reader1 = csv.reader(file)
        data1 = set(tuple(row) for row in reader1)
    with open(result, 'r') as file:
        reader2 = csv.reader(file)
        data2 = set(tuple(row) for row in reader2)
    # find the different rows in two files
    diff1 = data1 - data2
    diff2 = data2 - data1
    if diff1:
        print("Rows in gold standard", "but not in the resulting file:",
              str(len(diff1)))
        for row in diff1:
            print(row)
    if diff2:
        print("Rows in the resulting file", "but not in gold standard:",
              str(len(diff2)))
        for row in diff2:
            print(row)


# choose a gold standard file to test
gold_sentences = 'myapp/gold_standard/32021R0444S.csv'
result_sentences = 'myapp/results/sentences.csv'


def compare_sentences():
    sent_set = views.get_sentences()
    file_path = os.path.join('myapp/results', 'sentences.csv')
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Definition', 'Sentence'])
        for definition in sent_set:
            for sent in sent_set[definition]:
                writer.writerow([definition, sent])
    with open(gold_sentences, 'r') as file:
        reader1 = csv.reader(file)
        data1 = set(tuple(row) for row in reader1)
    with open(result_sentences, 'r') as file:
        reader2 = csv.reader(file)
        data2 = set(tuple(row) for row in reader2)
    # find the different rows in two files
    diff1 = data1 - data2
    diff2 = data2 - data1
    if diff1:
        print("Sentences in gold standard", "but not in the resulting file:",
              str(len(diff1)))
        for row in diff1:
            print(row)
    if diff2:
        print("Sentences in the resulting file", "but not in gold standard:",
              str(len(diff2)))
        for row in diff2:
            print(row)
