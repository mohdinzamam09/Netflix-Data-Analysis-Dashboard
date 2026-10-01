"""Netflix Analytics backend (Flask + SQLite).  Run: python backend/app.py"""
import os, sqlite3, threading, webbrowser
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, abort
from countries import COORDS

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "netflix.db"
app = Flask(__name__, static_folder="static", static_url_path="")

def db():
    if not DB.exists(): abort(500, "Database missing. Run: python run_all.py")
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row; return con

def query(sql, params=()):
    with db() as con: return [dict(r) for r in con.execute(sql, params).fetchall()]

def where():
    """Build a WHERE clause from ?q=&genre=&year=  (table alias: t)."""
    c, p = ["1=1"], []
    if request.args.get("q"): c.append("t.title LIKE ?"); p.append(f"%{request.args['q']}%")
    if request.args.get("genre"):
        c.append("EXISTS (SELECT 1 FROM title_genre g WHERE g.show_id=t.show_id AND g.genre=?)"); p.append(request.args["genre"])
    if request.args.get("year", "").isdigit(): c.append("t.release_year=?"); p.append(int(request.args["year"]))
    return " AND ".join(c), p

def ensure_indexes():
    if not DB.exists(): return
    with sqlite3.connect(DB) as con:
        for n, t, c in [("idx_titles_id","titles","show_id"),("idx_titles_year","titles","release_year"),("idx_tg_genre","title_genre","genre, show_id"),
                        ("idx_tg_id","title_genre","show_id"),("idx_tc_country","title_country","country, show_id"),("idx_tc_id","title_country","show_id")]:
            con.execute(f"CREATE INDEX IF NOT EXISTS {n} ON {t}({c})")

@app.get("/")
def index(): return send_from_directory(app.static_folder, "index.html")

@app.get("/api/health")
def health():
    return jsonify(status="ok", titles=query("SELECT COUNT(*) n FROM titles")[0]["n"])

@app.get("/api/filters")
def filters():
    return jsonify(genres=[r["genre"] for r in query("SELECT genre FROM title_genre GROUP BY genre ORDER BY genre")],
                   years=[r["release_year"] for r in query("SELECT DISTINCT release_year FROM titles WHERE release_year>=2010 ORDER BY release_year DESC")])

@app.get("/api/summary")
def summary():
    w, p = where()
    r = query(f"""SELECT COALESCE(SUM(t.type='Movie'),0) movies, COALESCE(SUM(t.type='TV Show'),0) tv,
                  ROUND(AVG(CASE WHEN t.type='Movie' THEN t.duration_min END)) avg_runtime FROM titles t WHERE {w}""", p)[0]
    r["countries"] = query(f"SELECT COUNT(DISTINCT c.country) n FROM title_country c JOIN titles t ON t.show_id=c.show_id WHERE {w}", p)[0]["n"]
    return jsonify(r)

@app.get("/api/genres")
def genres():
    w, p = where()
    return jsonify(query(f"""SELECT g.genre, SUM(t.type='Movie') movies, SUM(t.type='TV Show') tv FROM title_genre g
                             JOIN titles t ON t.show_id=g.show_id WHERE {w} GROUP BY g.genre ORDER BY movies+tv DESC LIMIT 5""", p))

@app.get("/api/countries")
def countries():
    w, p = where()
    rows = query(f"""SELECT c.country, COUNT(*) n FROM title_country c JOIN titles t ON t.show_id=c.show_id
                     WHERE {w} GROUP BY c.country ORDER BY n DESC""", p)
    for r in rows: r["lat"], r["lon"] = COORDS.get(r["country"], (None, None))
    return jsonify(rows)

@app.get("/api/years")
def years():
    w, p = where()
    return jsonify(query(f"""SELECT t.release_year year, SUM(t.type='Movie') movies, SUM(t.type='TV Show') tv FROM titles t
                             WHERE {w} AND t.release_year>=2010 GROUP BY t.release_year ORDER BY t.release_year""", p))

@app.get("/api/titles")
def titles():
    w, p = where(); page = max(1, int(request.args.get("page", 1) if request.args.get("page", "1").isdigit() else 1)); size = 8
    total = query(f"SELECT COUNT(*) n FROM titles t WHERE {w}", p)[0]["n"]
    rows = query(f"""SELECT t.title, t.type, t.release_year year, t.rating, t.primary_country country, t.primary_genre genre
                     FROM titles t WHERE {w} ORDER BY t.release_year DESC, t.title LIMIT ? OFFSET ?""", p + [size, (page-1)*size])
    return jsonify(rows=rows, total=total, page=page, pages=max(1, -(-total // size)))

if __name__ == "__main__":
    ensure_indexes()
    port = int(os.environ.get("PORT", 5000))
    if not os.environ.get("NO_BROWSER"): threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    print(f"\n  Netflix dashboard running at http://127.0.0.1:{port}  (Ctrl+C to stop)\n")
    app.run(host="127.0.0.1", port=port)
