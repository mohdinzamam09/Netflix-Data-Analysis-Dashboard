"""Step 1: Clean Netflix titles dataset (Pandas) and build Power BI / MySQL-ready tables."""
import pandas as pd, sqlite3

df = pd.read_csv("data/raw_netflix_titles.csv")
print("Raw shape:", df.shape)
report = {"raw_rows": len(df)}
report["missing_before"] = df.isna().sum().to_dict()

# 1. Duplicates (full-row and same title+type+release_year)
report["exact_duplicates"] = int(df.duplicated().sum())
df = df.drop_duplicates()
report["title_dupes"] = int(df.duplicated(["title", "type", "release_year"]).sum())
df = df.drop_duplicates(["title", "type", "release_year"])

# 2. Strip whitespace on all text columns
for c in df.select_dtypes("object"):
    df[c] = df[c].str.strip()

# 3. Missing values
for c in ["director", "cast", "country"]:
    df[c] = df[c].fillna("Unknown")
df["rating"] = df["rating"].fillna("Not Rated")
# Three rows have duration mistakenly placed in 'rating' (e.g. '74 min'): fix them
mask = df["rating"].str.contains("min", na=False)
df.loc[mask, "duration"] = df.loc[mask, "rating"]
df.loc[mask, "rating"] = "Not Rated"
df["duration"] = df["duration"].fillna("0 min")

# 4. Date format -> real datetime; derive year/month
df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), format="%B %d, %Y", errors="coerce")
report["date_added_missing"] = int(df["date_added"].isna().sum())
df["year_added"] = df["date_added"].dt.year.astype("Int64")
df["month_added"] = df["date_added"].dt.month_name()

# 5. Duration -> numeric (minutes for movies, seasons for TV shows)
df["duration_value"] = df["duration"].str.extract(r"(\d+)").astype(int)
df["duration_unit"] = df["duration"].str.extract(r"([A-Za-z]+)")[0].str.lower().replace({"seasons": "season"})
df["duration_min"] = df["duration_value"].where(df["type"] == "Movie")
df["seasons"] = df["duration_value"].where(df["type"] == "TV Show")

# 6. Rating -> audience group
grp = {"TV-MA": "Adults", "R": "Adults", "NC-17": "Adults", "NR": "Not Rated", "UR": "Not Rated", "Not Rated": "Not Rated",
       "TV-14": "Teens", "PG-13": "Teens", "TV-PG": "Older Kids", "PG": "Older Kids",
       "TV-Y7": "Older Kids", "TV-Y7-FV": "Older Kids", "TV-Y": "Kids", "TV-G": "Kids", "G": "Kids"}
df["audience"] = df["rating"].map(grp).fillna("Not Rated")

df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()
df["decade"] = (df["release_year"] // 10 * 10).astype(str) + "s"
df = df.reset_index(drop=True)

report["clean_rows"] = len(df)
report["missing_after"] = df.isna().sum()[lambda s: s > 0].to_dict()
df.to_csv("data/netflix_cleaned.csv", index=False)

# ---- Normalised tables (genre / country are multi-valued) ----
def explode(col, name):
    t = df[["show_id", col]].assign(**{name: df[col].str.split(",")}).explode(name)
    t[name] = t[name].str.strip()
    return t[["show_id", name]].query(f"{name} != 'Unknown' and {name} != ''").drop_duplicates()
genres, countries = explode("listed_in", "genre"), explode("country", "country")
dirs = explode("director", "director")
genres.to_csv("powerbi/title_genre.csv", index=False)
countries.to_csv("powerbi/title_country.csv", index=False)
fact = df.drop(columns=["cast", "description"])
fact.to_csv("powerbi/fact_titles.csv", index=False)
cal = pd.DataFrame({"year": range(int(df.release_year.min()), 2022)})
cal.to_csv("powerbi/dim_year.csv", index=False)

# Load into relational DB (SQLite here for validation; the same CSVs load into MySQL via sql/01_schema.sql)
con = sqlite3.connect("data/netflix.db")
df.drop(columns=["cast"]).assign(date_added=df["date_added"].dt.strftime("%Y-%m-%d")).to_sql("titles", con, index=False, if_exists="replace")
genres.to_sql("title_genre", con, index=False, if_exists="replace")
countries.to_sql("title_country", con, index=False, if_exists="replace")
for stmt in ["CREATE UNIQUE INDEX idx_titles_id ON titles(show_id)", "CREATE INDEX idx_titles_year ON titles(release_year)",
             "CREATE INDEX idx_tg_genre ON title_genre(genre, show_id)", "CREATE INDEX idx_tg_id ON title_genre(show_id)",
             "CREATE INDEX idx_tc_country ON title_country(country, show_id)", "CREATE INDEX idx_tc_id ON title_country(show_id)"]:
    con.execute(stmt)
con.commit(); con.close()
import json; json.dump(report, open("data/cleaning_report.json", "w"), indent=2, default=str)
print(json.dumps(report, indent=2, default=str))
