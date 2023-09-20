from collections import Counter
import re
import json

# Define a function to calculate term frequency in a text
def calculate_term_frequency(text, term):
    word = term.split()
    
    if len(word) == 1:
        term_count = len(re.findall(r'\b' + re.escape(term.lower()) + r'\b', text.lower()))
    else:
        term_count = len(re.findall(re.escape(term.lower()), text.lower()))

    return term_count

def calculate_sentence_score(data):
    for item in data:
        term = item['term']
        item['scores'] = {}  # Create a dictionary to store scores for each article

        # Iterate through each article
        for article, sentences in item['existing_sentences'].items():
            article_score = 0
            statement_scores = []  # Store scores for each statement

            # Check if it's Article 2 and the term is between '\u2018' and '\u2019'
            if article == "Article 2":
                for sentence in sentences:
                    if f'\u2018{term}\u2019' in sentence:
                        article_score = 0
                        statement_scores.append(0)
                        continue
                    else:
                        term_frequency = calculate_term_frequency(sentence, term)
                        article_score += term_frequency
                        statement_scores.append(term_frequency)
            else:
                # Calculate term frequency in all other articles and statements
                for sentence in sentences:
                    term_frequency = calculate_term_frequency(sentence, term)
                    article_score += term_frequency
                    statement_scores.append(term_frequency)

            # Store the score for this article and statements
            item['scores'][article] = {
                'article_score': article_score,
                'statement_scores': statement_scores
            }

            item['processed'] = "N"
    
    return data