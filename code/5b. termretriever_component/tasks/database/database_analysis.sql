-- Distribution of number of definitions per document
SELECT d.celex_id, t.doc_id, COUNT(t.term_id) AS term_count
FROM lexdrafter_energy_definition_term as t
JOIN lexdrafter_energy_document_information as d
ON t.doc_id = d.id
GROUP BY d.celex_id, t.doc_id
ORDER BY term_count ASC;

-- Analysis of the year and how many definitions are present per year
-- This helps to split the dataset into train, validate, test split
SELECT 
	SUBSTRING(d.celex_id, 2, 4) AS year,
	COUNT(t1.term_id) AS definition_count
FROM lexdrafter_energy_term_explanation t1
	JOIN lexdrafter_energy_document_information AS d ON t1.doc_id = d.id
GROUP BY
  year
ORDER BY
  year ASC;

-- Evaluation will be performed in two manners:
-- 1. The Definition generation part of the framework
-- 2. The working of TermRetriever component

-- For the second evaluation criteria below tables are required
CREATE TABLE lexdrafter_energy_document_split (
    celex_id TEXT,
    split TEXT
);

-- Create a CTE with the row numbers
WITH cte AS (
    SELECT
        celex_id,
        ROW_NUMBER() OVER (ORDER BY celex_id) AS row_num
    FROM lexdrafter_energy_document_information
)
INSERT INTO lexdrafter_energy_document_split (celex_id, split)
SELECT
    cte.celex_id,
    CASE
        WHEN cte.row_num <= 65 THEN 'train'
        WHEN cte.row_num <= 82 THEN 'validate'
        ELSE 'test'
    END AS split
FROM cte;
