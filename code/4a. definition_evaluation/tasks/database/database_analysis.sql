-- Table Creation
CREATE TABLE definition_table (
	record_id INT GENERATED ALWAYS AS IDENTITY (CYCLE),
    celex_id VARCHAR (20) NOT NULL,
	chapter INT NOT NULL,
	section INT NOT NULL,
	article INT NOT NULL,
    article_fragment INT NOT NULL,
    article_subfragment INT NOT NULL,
	article_title VARCHAR (65535),
    article_text VARCHAR (65535),
    term VARCHAR (20000),
    relationship VARCHAR (100),
    definition_text VARCHAR (65535),
	processed_flag CHAR (1),
    regex VARCHAR (200)
);

-- Creat index for article_title
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_articles_title ON articles(article_title) -- Took 11 secs and 954 msecs

-- Create Materialised Views for the Definition
CREATE MATERIALIZED VIEW definitions_mv AS
SELECT
    celex_id,
    chapter_number,
    section_number,
    article_number,
    article_fragment_number,
    article_subfragment_number,
	article_title,
    article_text
FROM articles
WHERE article_title = 'Definitions' AND article_text <> ''
GROUP BY
    celex_id,
    chapter_number,
    section_number,
    article_number,
    article_fragment_number,
    article_subfragment_number;
	
-- Starting regex
article_text ~ '‘[^’]+’ means [a-zA-Z]+ [a-zA-Z]+'

-- Count the number of article text having definition in different Articles
SELECT article_title, COUNT(*) AS record_count
FROM articles
WHERE 
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+'
)
GROUP BY article_title
ORDER BY record_count DESC;

-- To Get total Sum: 55,352
SELECT 
    article_title, 
    COUNT(*) AS record_count
FROM articles
WHERE 
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+'
)
GROUP BY ROLLUP(article_title)
ORDER BY record_count DESC;

-- Considering most possibility of writing a definition
-- Query to find out all the Definitions from the Definition and Definition article present that are abiding the pattern => Count: 13,370
SELECT *
FROM articles
WHERE (article_title = 'Definitions' OR article_title = 'Definition') 
AND
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+'
)
AND article_text <> '';

-- Check in Scope - Count: 3
SELECT *
FROM articles
WHERE article_title = 'Scope' 
AND article_text ~ '‘[^’]+’:[^.]+'
AND article_text <> '';

-- \‘(?<term>[^\’]+)\’\:(?<definition>[^\.]+) - Regular Expression

-- Check for Fishing Zone: Count 187
SELECT *
FROM articles
WHERE (article_title = 'Fishing zones') 
AND
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+'
)
AND article_text <> '';
-- Regular Expression
-- means : [\‘]?[\“]?(?<term>[^\’]+)[\’]?[\”]? mean[s]?\s(?<definition>[^\.]+)

-- Check in Subject Matter and Scope/Comittee procedure/Subject matter/Objectives - Count: 0
SELECT *
FROM articles
WHERE (article_title = 'Objectives') 
AND
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+'
)
AND article_text <> '';

-- Procedure for the Code

-- Scope
SELECT *
FROM articles
WHERE article_title = 'Scope' 
AND article_text ~ '‘[^’]+’:[^.]+'
AND article_text <> '';
-- Total Count: 3
-- Regular Expression: \‘(?<term>[^\’]+)\’\:(?<definition>[^\.]+)



SELECT * FROM definition_table


-- Fishing zones
SELECT *
FROM articles
WHERE (article_title = 'Fishing zones') 
AND
(
	-- article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+' - Tackled
    -- OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+' - No records
	-- article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+' - No records
	-- article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+' - No records
	-- article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+' - No records
	-- article_text ~ '([‘]?[“]?[^]+[’]?[”]?) are as defined[^.]+' - Tackled
	-- article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+' - No records
	-- OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+' - Not Valid
)
AND article_text <> '';
-- Total : 187

SELECT *
FROM articles
WHERE (article_title = 'Fishing zones') 
AND
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
)
AND article_text <> '';
-- Total 123
-- Regular Expression: [\‘]?[\“]?(?<term>[^\’]+)[\’]?[\”]? mean[s]?\s(?<definition>[^\.]+)

SELECT *
FROM articles
WHERE (article_title = 'Fishing zones') 
AND
(
	article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined[^.]+'
)
AND article_text <> '';
-- Total 29
-- Regular expression: [‘]?[“]?(?<term>[^]+)[’]?[”]? (?:(?:is|are)) as defined in (?<definition>[^.]+)

SELECT *
FROM articles
WHERE (article_title = 'Fishing zones') 
AND NOT
(
	article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) are as defined[^.]+'
)
AND article_text <> '';
-- Total 130
-- Regular expression: [\‘]?[\“]?(?<term>[^\’]+)[\’]?[\”]? (?:(?:is|are) the (?:geographical)? area[s]?) (?<definition>[^\.]+)
-- [\‘]?[\“]?(?<term>[^\’]+)[\’]?[\”]? (?:(?:is|are) the area[s]?) (?<definition>[^\.]+)


-- Definitions
SELECT *
FROM articles
WHERE (article_title = 'Definitions' OR article_title = 'Definition') 
AND
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) \([‘]?[^’]+[’]?\) mean[s]?[^.]+'
    OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) has the meaning [^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall mean[s]?[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) refer[s]? to[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) as defined in[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?) shall be defined as[^.]+'
	OR article_text ~ '([‘]?[“]?[^]+[’]?[”]?):[^.]+'
)
AND article_text <> '';
-- Total: 13,370

SELECT *
FROM articles
WHERE (article_title = 'Definitions' OR article_title = 'Definition') 
AND
(
    article_text ~ '([‘]?[“]?[^]+[’]?[”]?) mean[s]?[^.]+'
)
AND article_text <> '';
-- Total: 13135
-- Regular expression: [\‘]?[\“]?(?<term>[^\’]+)[\’]?[\”]? mean[s]?\s(?<definition>[^\.]+)
-- Cleaning: html tags and few checks on term extracted for example: ‘small and medium-sized enterprises’ or ‘SMEs’
