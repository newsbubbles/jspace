import json, sys, pathlib
rs = json.loads(pathlib.Path(r"D:\jspace\data\references.json").read_text(encoding="utf-8"))
for r in rs:
    a = r.get("authors", "")
    first = a.split(",")[0].strip()
    if "," in a or " and " in a:
        first += " et al."
    print(f'{r["n"]:>3} | {r.get("year","----")} | {first[:26]:<26} | {r.get("title","")[:92]}')
