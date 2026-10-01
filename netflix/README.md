# Netflix Data Analysis Dashboard
**Python • SQL (MySQL) • Excel • Power BI • Data Visualization**

Source: Netflix Titles dataset (7,787 titles, data through Jan 2021).

## Pipeline
| Step | File | What it does |
|---|---|---|
| 1 | `scripts/01_clean_data.py` | Pandas cleaning: missing values, duplicate checks, date + duration standardisation, derived columns, normalised genre/country tables |
| 2 | `sql/01_schema_mysql.sql`, `sql/02_analysis_queries.sql` | MySQL 8 schema/load + 14 analysis queries (type, genre, country, rating, release year; window functions, CTEs) |
| 3 | `scripts/03_visualizations.py` → `charts/` | 9 Python charts (matplotlib/seaborn) |
| 4 | `Netflix_Analysis.xlsx` | Cleaned data, formula-driven Summary dashboard + charts, cleaning log |
| 5 | `backend/app.py` + `backend/static/` | Flask REST API over the database + red/black Netflix dashboard (KPI cards, filters, donut, top-5 genres, country map, content-by-year, searchable titles table). `dashboard/netflix_dashboard.html` is an optional offline snapshot |
| 6 | `powerbi/` | Power BI-ready tables + build guide (model, DAX, layout) |

## How to run
```bash
pip install -r requirements.txt
python run_all.py        # prepares data (steps 1-4), starts the Flask backend, opens the dashboard
```
The dashboard opens at **http://127.0.0.1:5000** (press Ctrl+C in the terminal to stop). To start only the server later: `python open_dashboard.py`.

## Architecture
```
Raw CSV -> Pandas cleaning -> SQLite database (indexed) -> Flask REST API -> Dashboard front end (HTML/CSS/JS)
                                                      \-> Excel report, Python charts, Power BI tables
```
| API endpoint | Returns |
|---|---|
| `GET /api/health` | server status + row count |
| `GET /api/filters` | genre and year options |
| `GET /api/summary` | movies, TV shows, avg runtime, countries |
| `GET /api/genres` | top 5 genres split by type |
| `GET /api/countries` | titles per country (map bubbles) |
| `GET /api/years` | titles per release year, 2010+ |
| `GET /api/titles?page=n` | paginated title table |

Every endpoint accepts the filters `?q=<title text>&genre=<genre>&year=<release year>`, so the front end never holds the data itself.

## Data cleaning summary
- Missing: director 2,389, cast 718, country 507, rating 7, date_added 10. Text fields filled with "Unknown"/"Not Rated"; the 10 missing dates are left blank rather than invented.
- Duplicates checked on full row and on title+type+year: none found.
- `date_added` text converted to a real date; `duration` split into `duration_min` (movies) and `seasons` (TV).
- Multi-valued `listed_in` and `country` columns split into bridge tables for correct genre/country counts.

## Key insights
1. **Movie-heavy catalog:** 69% movies (5,377) vs 31% TV shows (2,410).
2. **Rapid scale-up, then a dip:** titles added jumped from 88 (2015) to 2,153 (2019), then fell 6.7% in 2020. 2021 is a partial year and should not be read as a drop.
3. **Not just the US:** US leads (3,297 titles) but India (990) and the UK (723) follow; the non-US share of added titles grew after 2016 and now exceeds the US share every year.
4. **Genres:** International Movies (2,437), Dramas (2,106) and Comedies (1,471) lead; International TV Shows (1,199) is the biggest TV category.
5. **Mature-skewed audience:** TV-MA (2,863) and TV-14 (1,931) make up about 62% of titles; kids' ratings are a small share.
6. **Recent content favoured:** TV shows are added about 2.3 years after release on average vs 5.6 for movies; movies are also getting shorter (about 113 min in the 1990s to about 90 min in the 2020s).
7. **TV shows are short-run:** 1,608 of 2,410 shows (67%) have one season, which suggests a "limited series" strategy.

## Limitations
- Snapshot dataset ends January 2021; it shows catalog composition, not viewership or popularity.
- `country` lists production countries only; titles with blank country are labelled "Unknown".
