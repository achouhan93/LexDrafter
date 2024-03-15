from sqlalchemy import select, update, Table, MetaData, and_, text, cast, Integer
from sqlalchemy.dialects.postgresql import JSONB
from tqdm import tqdm

def cited_fetch_data(conn, articles_table, citation_table, row):
    # Extract celex_id, article number, and article fragment number from jsonb field
    celex_id = row['cited_information'].get('cited_celex_id')
    article_num = row['cited_information'].get('cited_article_number')
    fragment_num = row['cited_information'].get('cited_article_fragment_number')

    if fragment_num == -1:
        # Fetch article text from articles table
        article_query = select([articles_table.c.article_text]).where(
            articles_table.c.celex_id == celex_id).where(
            articles_table.c.article_number == article_num)
    else:
        # Fetch article text from articles table
        article_query = select([articles_table.c.article_text]).where(
            articles_table.c.celex_id == celex_id).where(
            articles_table.c.article_number == article_num).where(
            articles_table.c.article_fragment_number == fragment_num)

    result = conn.execute(article_query)

    if result.rowcount == 0:
        article_text = 'no reference text found'
    elif result.rowcount == 1:
        row = result.fetchone()
        article_text = row[0]
    elif result.rowcount > 1:
        row = result.fetchall()
        article_text = ' '.join([t[0] for t in row]).strip()

    # Update citation_table with article text
    update_query = (
        update(citation_table)
        .where(
            and_(
                text("cited_information ->> 'cited_celex_id' = :celex_id")
                .bindparams(celex_id=celex_id),
                text("cited_information ->> 'cited_article_number' = :article_num")
                .bindparams(article_num=article_num),
                text("cited_information ->> 'cited_article_fragment_number' = :fragment_num")
                .bindparams(fragment_num=str(fragment_num))
            )
        )
        .values(
            cited_information=cast({'cited_celex_id': celex_id,
                     'cited_article_number': article_num,
                     'cited_article_fragment_number': fragment_num,
                     'cited_article_text': article_text}, JSONB)
        )
    )

    conn.execute(update_query)

def citing_fetch_data(conn, articles_table, citation_table, row):
    # Extract celex_id, article number, and article fragment number from jsonb field
    celex_id = row['citing_information'].get('citing_celex_id')
    chapter_num = row['citing_information'].get('citing_chapter')
    section_num = row['citing_information'].get('citing_section')
    article_num = row['citing_information'].get('citing_article')
    fragment_num = row['citing_information'].get('citing_article_fragment')

    # Fetch article text from articles table
    citing_article_query = select([articles_table.c.article_text]).where(
        articles_table.c.celex_id == celex_id).where(
        articles_table.c.chapter_number == chapter_num).where(
        articles_table.c.section_number == section_num).where(
        articles_table.c.article_number == article_num).where(
        articles_table.c.article_fragment_number == fragment_num)

    result = conn.execute(citing_article_query)
    row = result.fetchone()
    article_text = row[0]

    # Update citation_table with article text
    update_citing_query = (
        update(citation_table)
        .where(
            and_(
                text("citing_information ->> 'citing_celex_id' = :celex_id")
                .bindparams(celex_id=celex_id),
                cast(text("citing_information ->> 'citing_chapter'"), Integer) == chapter_num,
                cast(text("citing_information ->> 'citing_section'"), Integer) == section_num,
                cast(text("citing_information ->> 'citing_article'"), Integer) == article_num,
                cast(text("citing_information ->> 'citing_article_fragment'"), Integer) == fragment_num
            )
        )
        .values(
            citing_information=cast({'citing_celex_id': celex_id,
                     'citing_chapter': chapter_num,
                     'citing_section': section_num,
                     'citing_article': article_num,
                     'citing_article_fragment': fragment_num,
                     'citing_text': article_text}, JSONB)
        )
    )

    conn.execute(update_citing_query)

def article_text_completion(database_engine):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """

    # metadata = MetaData(bind=database_engine)
    metadata = MetaData()
    metadata.reflect(database_engine) 

    citation_table = metadata.tables['citation_ground_truth']
    articles_table = metadata.tables['articles']

    with database_engine.connect() as conn:
        query = select([citation_table])
        result = conn.execute(query)
        for row in tqdm(result):
            cited_fetch_data(conn, articles_table, citation_table, row)
            citing_fetch_data(conn, articles_table, citation_table, row)