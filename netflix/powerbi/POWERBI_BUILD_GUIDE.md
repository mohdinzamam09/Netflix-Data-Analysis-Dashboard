# Power BI Dashboard – Build Guide (≈30 min)

I can't generate a `.pbix` file (Power BI Desktop is Windows-only), so this gives you the exact model, DAX and layout.

## 1. Load data (Home → Get Data → Text/CSV)
- `fact_titles.csv`, `title_genre.csv`, `title_country.csv`, `dim_year.csv`
- Power Query: set `date_added` = Date; `release_year`, `year_added`, `duration_min`, `seasons` = Whole number.

## 2. Model (Model view)
| From | To | Cardinality |
|---|---|---|
| fact_titles[show_id] | title_genre[show_id] | 1 → many |
| fact_titles[show_id] | title_country[show_id] | 1 → many |
| dim_year[year] | fact_titles[year_added] | 1 → many |

Set cross-filter direction to **Both** on the genre and country relationships so slicers on a genre filter the fact table.

## 3. DAX measures
```DAX
Total Titles   = DISTINCTCOUNT(fact_titles[show_id])
Movies         = CALCULATE([Total Titles], fact_titles[type] = "Movie")
TV Shows       = CALCULATE([Total Titles], fact_titles[type] = "TV Show")
% Movies       = DIVIDE([Movies], [Total Titles])
Countries      = DISTINCTCOUNT(title_country[country])
Genres         = DISTINCTCOUNT(title_genre[genre])
Avg Movie Min  = CALCULATE(AVERAGE(fact_titles[duration_min]), fact_titles[type] = "Movie")
Titles Added   = CALCULATE([Total Titles], NOT ISBLANK(fact_titles[year_added]))
Titles PY      = CALCULATE([Titles Added], SAMEPERIODLASTYEAR(dim_year[year]))  -- or use PREVIOUSYEAR with a Date table
YoY Growth %   = DIVIDE([Titles Added] - [Titles PY], [Titles PY])
Non-US Share   = DIVIDE(CALCULATE([Total Titles], fact_titles[primary_country] <> "United States", fact_titles[primary_country] <> "Unknown"), [Total Titles])
```
(If `SAMEPERIODLASTYEAR` complains, create a proper Date table or use `CALCULATE([Titles Added], dim_year[year] = MAX(dim_year[year]) - 1)`.)

## 4. Page layout (16:9, dark #221F1F background, accent #E50914)
- **Top row – 6 KPI cards:** Total Titles, Movies, TV Shows, % Movies, Countries, Avg Movie Min
- **Slicers (left rail):** type, year_added (range), rating, audience, genre (from title_genre), country (from title_country)
- **Line + clustered column:** Titles Added by year_added, legend = type (*content growth*); filter year_added ≤ 2020, since 2021 is partial
- **Bar:** Top 10 genres (title_genre[genre], count of show_id, Top N filter = 10)
- **Filled map + bar:** Titles by country (title_country[country])
- **Donut:** Movies vs TV Shows
- **Stacked column:** Rating / audience mix by type
- **Decomposition tree or table:** Director → Titles (optional drill-through page)

## 5. Finish
Add tooltips, a title ("Netflix Content Strategy Dashboard"), bookmark a "Reset filters" button, then **File → Publish**.
