import pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
RED, DARK = "#E50914", "#221F1F"
sns.set_theme(style="whitegrid", rc={"axes.edgecolor": DARK, "axes.titleweight": "bold", "font.family": "DejaVu Sans"})
df = pd.read_csv("data/netflix_cleaned.csv", parse_dates=["date_added"])
g = pd.read_csv("powerbi/title_genre.csv"); c = pd.read_csv("powerbi/title_country.csv")
def save(name): plt.tight_layout(); plt.savefig(f"charts/{name}.png", dpi=150); plt.close()

# 1 type split
fig, ax = plt.subplots(figsize=(5, 5))
t = df.type.value_counts(); ax.pie(t, labels=t.index, autopct="%1.1f%%", colors=[RED, DARK], startangle=90, wedgeprops=dict(width=.45, edgecolor="w"), textprops={"color": "w", "weight": "bold"} )
for tx in ax.texts[:2]: tx.set_color(DARK)
ax.set_title("Movies vs TV Shows"); save("01_type_split")

# 2 content growth
y = df.dropna(subset=["year_added"]).query("year_added<=2020").groupby(["year_added", "type"]).size().unstack(fill_value=0); y.index = y.index.astype(int)
y.plot(kind="bar", stacked=True, color=[RED, DARK], figsize=(9, 4.5)); plt.title("Titles Added to Netflix per Year (2021 excluded: partial year)")
plt.xlabel(""); plt.ylabel("Titles"); save("02_content_growth")

# 3 genres / 4 countries
for data, col, n, nm, title in [(g, "genre", 10, "03_top_genres", "Top 10 Genres"), (c, "country", 10, "04_top_countries", "Top 10 Producing Countries")]:
    s = data[col].value_counts().head(n).sort_values(); s.plot(kind="barh", color=RED, figsize=(8, 4.5)); plt.title(title); plt.xlabel("Titles"); plt.ylabel(""); save(nm)

# 5 ratings
r = df.rating.value_counts().head(8).sort_values(); r.plot(kind="barh", color=DARK, figsize=(7, 4)); plt.title("Rating Distribution (Top 8)"); plt.xlabel("Titles"); plt.ylabel(""); save("05_ratings")

# 6 US vs international share
d = df.dropna(subset=["year_added"]).query("2014<=year_added<=2020").assign(intl=lambda x: ~x.primary_country.isin(["United States", "Unknown"]))
s = d.groupby("year_added").intl.mean() * 100; s.index = s.index.astype(int); s.plot(marker="o", color=RED, figsize=(7, 4)); plt.ylim(0, 100); plt.title("Share of Non-US Titles Added (%)"); plt.xlabel(""); plt.ylabel("%"); save("06_intl_share")

# 7 movie duration histogram
df.dropna(subset=["duration_min"]).duration_min.plot(kind="hist", bins=40, color=RED, figsize=(7, 4)); plt.title("Movie Duration Distribution (minutes)"); plt.xlabel("Minutes"); save("07_movie_duration")

# 8 heatmap: top genres x top countries
tg, tc = g.genre.value_counts().head(8).index, c.country.value_counts().head(8).index
m = c.merge(g, on="show_id"); m = m[m.genre.isin(tg) & m.country.isin(tc)]
plt.figure(figsize=(9, 5.5)); sns.heatmap(pd.crosstab(m.country, m.genre), annot=True, fmt="d", cmap="Reds", cbar=False); plt.title("Genre x Country (titles)"); plt.xlabel(""); plt.ylabel(""); plt.xticks(rotation=35, ha="right"); save("08_genre_country_heatmap")

# 9 audience by type
pd.crosstab(df.audience, df.type).reindex(["Kids", "Older Kids", "Teens", "Adults", "Not Rated"]).plot(kind="bar", color=[RED, DARK], figsize=(7, 4)); plt.title("Audience Mix by Type"); plt.xlabel(""); plt.xticks(rotation=0); save("09_audience")
print("done")
