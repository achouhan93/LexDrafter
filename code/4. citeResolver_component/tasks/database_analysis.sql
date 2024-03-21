CREATE TABLE lexdrafter_energy_data_split AS
SELECT
    di.celex_id,
    te.term_id,
    te.doc_id,
    te.explanation
FROM lexdrafter_energy_document_information di
JOIN lexdrafter_energy_term_explanation te ON di.id = te.doc_id;
