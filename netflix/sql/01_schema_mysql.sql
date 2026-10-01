-- MySQL 8.0 schema + load. Run after scripts/01_clean_data.py (CSV files in /data and /powerbi)
CREATE DATABASE IF NOT EXISTS netflix_db; USE netflix_db;

DROP TABLE IF EXISTS titles;
CREATE TABLE titles (
  show_id VARCHAR(10) PRIMARY KEY, type VARCHAR(10), title VARCHAR(255),
  director TEXT, country TEXT, date_added DATE NULL, release_year INT, rating VARCHAR(12),
  duration VARCHAR(20), listed_in VARCHAR(255), year_added INT NULL, month_added VARCHAR(12) NULL,
  duration_value INT, duration_unit VARCHAR(10), duration_min INT NULL, seasons INT NULL,
  audience VARCHAR(15), primary_country VARCHAR(80), primary_genre VARCHAR(80), decade VARCHAR(8)
);
CREATE TABLE title_genre   (show_id VARCHAR(10), genre   VARCHAR(80), FOREIGN KEY (show_id) REFERENCES titles(show_id));
CREATE TABLE title_country (show_id VARCHAR(10), country VARCHAR(80), FOREIGN KEY (show_id) REFERENCES titles(show_id));

-- Load (adjust path; enable local_infile). Columns of fact_titles.csv match 'titles' except description/cast removed.
LOAD DATA LOCAL INFILE 'powerbi/fact_titles.csv' INTO TABLE titles
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS
(show_id,type,title,director,country,@d,release_year,rating,duration,listed_in,@ya,@ma,duration_value,duration_unit,@dm,@se,audience,primary_country,primary_genre,decade)
SET date_added = NULLIF(@d,''), year_added = NULLIF(@ya,''), month_added = NULLIF(@ma,''),
    duration_min = NULLIF(@dm,''), seasons = NULLIF(@se,'');
-- NOTE: if column order differs from the CSV header in your export, list columns explicitly from the CSV header.
LOAD DATA LOCAL INFILE 'powerbi/title_genre.csv'   INTO TABLE title_genre   FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
LOAD DATA LOCAL INFILE 'powerbi/title_country.csv' INTO TABLE title_country FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
