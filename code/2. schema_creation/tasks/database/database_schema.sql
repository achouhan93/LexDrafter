-- For energy replace lexdrafter_ with lexdrafter_energy
CREATE TABLE lexdrafter_titles (
	celex_id VARCHAR (20) PRIMARY KEY,
	title_text VARCHAR (65535) NOT NULL
);

CREATE TABLE lexdrafter_recitals(
	celex_id VARCHAR (20) NOT NULL,
	recital_fragment_number INT NOT NULL,
	recital_fragment_original_value INT NOT NULL,
	recital_subfragment_number INT NOT NULL,
	recital_text VARCHAR (65535),
	PRIMARY KEY (celex_id, recital_fragment_number, recital_subfragment_number),
	FOREIGN KEY (celex_id)
      REFERENCES lexdrafter_titles (celex_id)
);

CREATE TABLE lexdrafter_chapters (
	celex_id VARCHAR (20) NOT NULL,
	chapter_number INT NOT NULL,
	chapter_title VARCHAR (65535),
	PRIMARY KEY (celex_id, chapter_number),
	FOREIGN KEY (celex_id)
      REFERENCES lexdrafter_titles (celex_id)
);


CREATE TABLE lexdrafter_sections (
	celex_id VARCHAR (20) NOT NULL,
	chapter_number INT NOT NULL,
	section_number INT NOT NULL,
	section_title VARCHAR (65535),
	PRIMARY KEY (celex_id, chapter_number, section_number),
	FOREIGN KEY (celex_id)
      REFERENCES lexdrafter_titles (celex_id)
);


CREATE TABLE lexdrafter_articles (
	celex_id VARCHAR (20) NOT NULL,
	chapter_number INT NOT NULL,
	section_number INT NOT NULL,
	article_number INT NOT NULL,
	article_title VARCHAR (65535),
	article_fragment_number INT NOT NULL,
	article_fragment_original_value INT NOT NULL,
	article_subfragment_number INT NOT NULL,
    article_text VARCHAR (65535),
	processed_flag CHAR (1),
	PRIMARY KEY (celex_id, chapter_number, section_number, article_number, article_fragment_number, article_subfragment_number),
	FOREIGN KEY (celex_id)
      REFERENCES lexdrafter_titles (celex_id)
);


CREATE TABLE lexdrafter_annexs (
	celex_id VARCHAR (20) NOT NULL,
	annex_number VARCHAR (10) NOT NULL,
	annex_fragment_number INT NOT NULL,
	annex_subfragment_number INT NOT NULL,
	annex_title VARCHAR (65535),
	annex_text VARCHAR (65535),
	PRIMARY KEY (celex_id, annex_number, annex_fragment_number, annex_subfragment_number),
	FOREIGN KEY (celex_id)
      REFERENCES lexdrafter_titles (celex_id)
);


CREATE TABLE IF NOT EXISTS lexdrafter_article_aux
(
    article_info text,
    flag text,
	PRIMARY KEY (article_info)
);

-- Investigate the databases
SELECT COUNT(*) FROM lexdrafter_titles