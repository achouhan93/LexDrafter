import regex as re
import pandas as pd

def split_fragment(regex_object, text):
    """
    Utility function to split the paragraph into fragments
    """
    # Replace misplaced utf8 chars
    text = text.replace(u"\xa0", u" ").strip()

    # Split the text based on the regex passed to the function
    if regex_object.group('first_level_number') is not None:
      text = re.sub(r"(?:(?:(?:^|[ ])(?P<first_level_number>\d+)\.\s{2,}))", r"[SPLIT]", text)
      original_value = 1 #1 is integer
    elif regex_object.group('second_level_number') is not None:
      text = re.sub(r"(?:[\:|\;|\.]\s\((?P<second_level_number>\d+)\)\s)", r"[SPLIT]", text)
      original_value = 1 #1 is integer
    elif regex_object.group('second_level_character') is not None:
      text = re.sub(r"(?!\:\s\(i\)\s)(?:[\:|\;|\.]\s\((?P<second_level_character>\D)\)\s)", r"[SPLIT]", text)
      original_value = 2 #2 is characters

    split_text = text.split("[SPLIT]")
    return (split_text, original_value)

def document_fragment(celex, document_structure):
    df_title = pd.DataFrame(columns = ["celex_id", "title_text"])
    df_recitals = pd.DataFrame(columns = ["celex_id", "recital_fragment_number", "recital_fragment_original_value", "recital_subfragment_number", "recital_text"])
    df_chapter = pd.DataFrame(columns = ["celex_id", "chapter_number", "chapter_title"])
    df_section = pd.DataFrame(columns = ["celex_id", "chapter_number", "section_number", "section_title"])
    df_articles = pd.DataFrame(columns = ["celex_id", "chapter_number", "section_number", "article_number", "article_title", "article_fragment_number", "article_fragment_original_value", "article_subfragment_number", "article_text", "processed_flag"])
    df_annex = pd.DataFrame(columns = ["celex_id", "annex_number", "annex_title", "annex_fragment_number", "annex_subfragment_number", "annex_text"])

    chapter_number = 0
    section_number = 0
    article_number = 0
    annex_number = 0
    previous_chapter_number = 0

    splitting_regex = re.compile('(?:(?:[\:|\;|\.]\s\((?P<second_level_number>\d+)\)\s)|(?!\:\s\(i\)\s)(?:[\:|\;|\.]\s\((?P<second_level_character>\D)\)\s)|(?:(?:(?:^|[ ])(?P<first_level_number>\d+)\.\s{2,})))')

    for index in range(len(document_structure)):
        information_dict = {}
        # Inorder to tackle the TITLE -> CHAPTER, Changes need to be done here
        #if 'title' in document_structure[index]['category'].lower():
        if 'title' in document_structure[index]['category']:
            information_dict['celex_id'] = celex
            information_dict['title_text'] = document_structure[index]['content'].title().replace(u'\n', u' ').strip()
            # Due to append error 
            # df_title = df_title.append(information_dict, ignore_index=True)
            df_title = pd.concat([df_title, pd.DataFrame([information_dict])], ignore_index=True)

        elif 'recital' in document_structure[index]['category'].lower():
            information_dict['celex_id'] = celex
            recitals = re.search(splitting_regex, document_structure[index]['content'])

            if recitals is not None:
                recitals_list = split_fragment(recitals, document_structure[index]['content'])
                original_index_value = recitals_list[1]
                value_list = recitals_list[0]
    
                for i, val in enumerate(value_list):
                    information_dict['recital_fragment_number'] = i
                    information_dict['recital_fragment_original_value'] = original_index_value
                    information_dict['recital_subfragment_number'] = 0
                    information_dict['recital_text'] = val.replace(u'\n', u' ').strip()
                    # df_recitals = df_recitals.append(information_dict, ignore_index=True)
                    df_recitals = pd.concat([df_recitals, pd.DataFrame([information_dict])], ignore_index=True)
            else:
                information_dict['recital_fragment_number'] = 0
                information_dict['recital_fragment_original_value'] = 0
                information_dict['recital_subfragment_number'] = 0
                information_dict['recital_text'] = document_structure[index]['content'].replace(u'\n', u' ').strip()
                df_recitals = pd.concat([df_recitals, pd.DataFrame([information_dict])], ignore_index=True)

        elif 'chapter' in document_structure[index]['category'].lower():
            chapter_number = chapter_number + 1
            information_dict['celex_id'] = celex
            information_dict['chapter_number'] = chapter_number
            information_dict['chapter_title'] = document_structure[index]['name'].title().replace(u'\n', u' ').strip()
            
            # df_chapter = df_chapter.append(information_dict, ignore_index=True)
            df_chapter = pd.concat([df_chapter, pd.DataFrame([information_dict])], ignore_index=True)

        elif 'section' in document_structure[index]['category'].lower():
            if previous_chapter_number != chapter_number:
                previous_chapter_number = chapter_number
                section_number = 0
            
            section_number = section_number + 1
            information_dict['celex_id'] = celex
            information_dict['chapter_number'] = chapter_number
            information_dict['section_number'] = section_number
            information_dict['section_title'] = document_structure[index]['name'].title().replace(u'\n', u' ').strip()
            
            # df_section = df_section.append(information_dict, ignore_index=True)
            df_section = pd.concat([df_section, pd.DataFrame([information_dict])], ignore_index=True)

        elif 'article' in document_structure[index]['category'].lower():
            if ("‘" in document_structure[index]['category'].lower()) and (len(df_articles) > 0):
                last_article_info = df_articles.iloc[-1]
                updated_text = f"{last_article_info['article_text']} {document_structure[index]['category']}/n{document_structure[index]['name']}/n{document_structure[index]['content']}"
                df_articles.loc[df_articles.index[-1], ['article_text']] = [updated_text]
                continue 
            
            article_number = article_number + 1
            information_dict['celex_id'] = celex
            information_dict['chapter_number'] = chapter_number
            information_dict['section_number'] = section_number
            information_dict['article_number'] = article_number
            information_dict['article_title'] = document_structure[index]['name']
            information_dict['processed_flag'] = 'N'

            articles = re.search(splitting_regex, document_structure[index]['content'])
            
            if articles is not None:
                articles_list = split_fragment(articles, document_structure[index]['content'])
                
                original_value = articles_list[1]
                article_value_list = articles_list[0]

                for i, val in enumerate(article_value_list):
                    information_dict['article_fragment_number'] = i
                    information_dict['article_fragment_original_value'] = original_value
                    information_dict['article_subfragment_number'] = 0
                    information_dict['article_text'] = val.replace(u'\n', u' ').strip()
                    
                    # df_articles = df_articles.append(information_dict, ignore_index=True)
                    df_articles = pd.concat([df_articles, pd.DataFrame([information_dict])], ignore_index=True)
            else:
                information_dict['article_fragment_number'] = 0
                information_dict['article_fragment_original_value'] = 0
                information_dict['article_subfragment_number'] = 0
                information_dict['article_text'] = document_structure[index]['content'].replace(u'\n', u' ').replace(u"\xa0", u" ").strip()
                
                df_articles = pd.concat([df_articles, pd.DataFrame([information_dict])], ignore_index=True)

        elif 'annex' in document_structure[index]['category'].lower():
            annex_number = annex_number + 1
            information_dict['celex_id'] = celex
            information_dict['annex_number'] = annex_number
            information_dict['annex_fragment_number'] = 0
            information_dict['annex_subfragment_number'] = 0
            information_dict['annex_title'] = document_structure[index]['name'].title()
            if len(document_structure[index]['content']) > 65530:
                truncated_string = document_structure[index]['content'][:65530] + "..."
            else:
                truncated_string = document_structure[index]['content']
            
            information_dict['annex_text'] = truncated_string
            
            # df_annex = df_annex.append(information_dict, ignore_index=True)
            df_annex = pd.concat([df_annex, pd.DataFrame([information_dict])], ignore_index=True)
    
    return (df_title, df_recitals, df_chapter, df_section, df_articles, df_annex)