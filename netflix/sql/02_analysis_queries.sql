-- Netflix content analysis (MySQL 8.0; also runs on SQLite for testing)

-- Q1. Movies vs TV Shows
SELECT type, COUNT(*) AS titles, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM titles),1) AS pct FROM titles GROUP BY type;

-- Q2. Top 10 genres
SELECT genre, COUNT(*) AS titles FROM title_genre GROUP BY genre ORDER BY titles DESC LIMIT 10;

-- Q3. Top 10 content-producing countries
SELECT country, COUNT(*) AS titles FROM title_country GROUP BY country ORDER BY titles DESC LIMIT 10;

-- Q4. Rating distribution
SELECT rating, COUNT(*) AS titles FROM titles GROUP BY rating ORDER BY titles DESC;

-- Q5. Titles added to Netflix per year, split by type
SELECT year_added, SUM(type='Movie') AS movies, SUM(type='TV Show') AS tv_shows, COUNT(*) AS total
FROM titles WHERE year_added IS NOT NULL GROUP BY year_added ORDER BY year_added;

-- Q6. Release-year trend by decade
SELECT decade, COUNT(*) AS titles FROM titles GROUP BY decade ORDER BY decade;

-- Q7. Year-over-year growth of titles added (window function)
WITH y AS (SELECT year_added, COUNT(*) AS n FROM titles WHERE year_added IS NOT NULL GROUP BY year_added)
SELECT year_added, n, LAG(n) OVER (ORDER BY year_added) AS prev_year,
       ROUND(100.0*(n-LAG(n) OVER (ORDER BY year_added))/LAG(n) OVER (ORDER BY year_added),1) AS yoy_pct
FROM y ORDER BY year_added;

-- Q8. Top 3 genres within each of the top 5 countries (RANK)
WITH top_c AS (SELECT country FROM title_country GROUP BY country ORDER BY COUNT(*) DESC LIMIT 5),
cg AS (SELECT c.country, g.genre, COUNT(*) AS n FROM title_country c
       JOIN title_genre g ON g.show_id=c.show_id WHERE c.country IN (SELECT country FROM top_c) GROUP BY c.country, g.genre),
r AS (SELECT *, RANK() OVER (PARTITION BY country ORDER BY n DESC) AS rnk FROM cg)
SELECT country, genre, n, rnk FROM r WHERE rnk<=3 ORDER BY country, rnk;

-- Q9. Audience mix by type
SELECT type, audience, COUNT(*) AS titles FROM titles GROUP BY type, audience ORDER BY type, titles DESC;

-- Q10. Average movie length by decade and TV season distribution
SELECT decade, ROUND(AVG(duration_min),1) AS avg_minutes FROM titles WHERE type='Movie' GROUP BY decade ORDER BY decade;
SELECT seasons, COUNT(*) AS shows FROM titles WHERE type='TV Show' GROUP BY seasons ORDER BY seasons;

-- Q11. Lag between release and Netflix addition (years), by type
SELECT type, ROUND(AVG(year_added-release_year),1) AS avg_lag_years FROM titles WHERE year_added IS NOT NULL GROUP BY type;

-- Q12. Share of "recent" content (released within 2 years of being added) per year added
SELECT year_added, ROUND(100.0*SUM(year_added-release_year<=2)/COUNT(*),1) AS pct_fresh
FROM titles WHERE year_added IS NOT NULL GROUP BY year_added ORDER BY year_added;

-- Q13. International vs US content by year added
SELECT year_added, SUM(primary_country='United States') AS us, SUM(primary_country NOT IN ('United States','Unknown')) AS non_us
FROM titles WHERE year_added IS NOT NULL GROUP BY year_added ORDER BY year_added;

-- Q14. Top 10 directors
SELECT director, COUNT(*) AS titles FROM titles WHERE director<>'Unknown' AND director NOT LIKE '%,%'
GROUP BY director ORDER BY titles DESC LIMIT 10;
