import pandas as pd, json
df = pd.read_csv("data/netflix_cleaned.csv")
g = pd.read_csv("powerbi/title_genre.csv"); c = pd.read_csv("powerbi/title_country.csv")
G = sorted(g.genre.unique()); C = sorted(c.country.unique())
gm = g.groupby("show_id").genre.apply(lambda s: [G.index(x) for x in s]).to_dict()
cm = c.groupby("show_id").country.apply(lambda s: [C.index(x) for x in s]).to_dict()
t = [[r.title, int(r.type == "TV Show"), int(r.release_year),
      0 if pd.isna(r.duration_min) else int(r.duration_min), gm.get(r.show_id, []), cm.get(r.show_id, [])] for r in df.itertuples()]
LL = {"United States":[39,-98],"India":[21,78],"United Kingdom":[54,-2],"Canada":[56,-106],"France":[46,2],"Japan":[36,138],"Spain":[40,-4],"South Korea":[36,128],"Germany":[51,10],"Mexico":[23,-102],"China":[35,104],"Australia":[-25,134],"Egypt":[26,30],"Turkey":[39,35],"Brazil":[-10,-52],"Italy":[42,12],"Nigeria":[9,8],"Argentina":[-34,-64],"Indonesia":[-2,118],"Taiwan":[23.7,121],"Hong Kong":[22.3,114.2],"Thailand":[15,101],"Philippines":[13,122],"Netherlands":[52,5],"Belgium":[50.6,4.6],"Sweden":[62,15],"Denmark":[56,10],"Ireland":[53,-8],"Poland":[52,19],"Russia":[60,90],"South Africa":[-29,24],"Singapore":[1.3,103.8],"Colombia":[4,-72],"Chile":[-30,-71],"Lebanon":[33.9,35.9],"Israel":[31,35],"Pakistan":[30,70],"Norway":[61,9],"Switzerland":[46.8,8.2],"Czech Republic":[49.8,15.5],"Romania":[46,25],"Saudi Arabia":[24,45],"United Arab Emirates":[24,54],"Malaysia":[4,102],"Vietnam":[16,108],"New Zealand":[-41,174],"Finland":[64,26],"Austria":[47.5,14.5],"Greece":[39,22],"Iceland":[65,-18],"Kenya":[0,38],"Hungary":[47,19],"Portugal":[39.5,-8],"Peru":[-10,-76],"Bangladesh":[24,90],"Ukraine":[49,32],"Jordan":[31,36],"Iran":[32,53],"Kuwait":[29.3,47.5],"Morocco":[32,-6],"Uruguay":[-33,-56],"Venezuela":[7,-66],"Luxembourg":[49.8,6.1],"Bulgaria":[42.7,25.5],"Serbia":[44,21],"Croatia":[45.1,15.2],"Slovenia":[46,14.8],"Cambodia":[12.5,105],"Ghana":[8,-1],"Senegal":[14.5,-14.5],"Cuba":[21.5,-80],"Qatar":[25.3,51.2]}
html = open("dashboard/template.html").read()
html = html.replace("__DATA__", json.dumps({"g": G, "c": C, "t": t}, separators=(",", ":")).replace("</", "<\\/")).replace("__LATLON__", json.dumps(LL))
open("dashboard/netflix_dashboard.html", "w").write(html)
import os; print("Dashboard saved to", os.path.abspath("dashboard/netflix_dashboard.html"))
print(len(html)//1024, "KB;", "countries unmapped:", [x for x in C if x not in LL])
