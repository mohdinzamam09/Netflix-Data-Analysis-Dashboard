import sqlite3, re, pandas as pd
con = sqlite3.connect("data/netflix.db")
sql = open("sql/02_analysis_queries.sql").read()
blocks = re.split(r"\n(?=-- Q\d+)", sql)
pd.set_option("display.width", 200)
with open("data/sql_results.txt", "w") as f:
    for b in blocks[1:]:
        title = b.split("\n")[0]
        for stmt in [s for s in b.split(";") if re.search(r"\bSELECT\b|\bWITH\b", s)]:
            r = pd.read_sql(stmt, con)
            out = f"{title}\n{r.to_string(index=False)}\n"
            f.write(out + "\n"); print(out)
