"""Parse the numbered bibliography out of the extracted J-space paper text.

The PDF text carries page markers and bare page-number lines, and entries wrap
across lines with hyphenation. We rebuild each [N] entry, then pull out the
fields we can identify with confidence (arXiv id, DOI, URL, year) plus a
best-effort author/title split. The raw string is always kept so nothing that
the heuristics mangle is actually lost.
"""
import json
import pathlib
import re

SRC = pathlib.Path(r"D:\jspace\sources\gurnee-2026-jspace.txt")
OUT = pathlib.Path(r"D:\jspace\data\references.json")

text = SRC.read_text(encoding="utf-8")

# The bibliography is the tail of the document, starting at the "References"
# heading on its own line.
start = re.search(r"^References\s*$", text, re.M)
if not start:
    raise SystemExit("no References heading found")
body = text[start.end():]

# Drop page furniture: "=== [page N] ===" markers and bare page numbers.
lines = []
for line in body.splitlines():
    s = line.strip()
    if not s:
        continue
    if re.fullmatch(r"=== \[page \d+\] ===", s):
        continue
    if re.fullmatch(r"\d{1,4}", s):          # running page number
        continue
    lines.append(s)

# Rejoin: a new entry starts with "[N]". Everything else continues the previous.
entries, cur = [], None
for s in lines:
    m = re.match(r"^\[(\d+)\]\s*(.*)$", s)
    if m:
        if cur:
            entries.append(cur)
        cur = {"n": int(m.group(1)), "parts": [m.group(2)]}
    elif cur:
        cur["parts"].append(s)
if cur:
    entries.append(cur)


def join(parts):
    out = ""
    for p in parts:
        if out.endswith("-"):
            out = out[:-1] + p          # de-hyphenate a wrapped word
        elif out:
            out += " " + p
        else:
            out = p
    return re.sub(r"\s+", " ", out).strip()


# Split on a period+space that is NOT preceded by a single capital (initials
# like "T. Ben Thompson") and not inside an arXiv/URL fragment.
SPLIT = re.compile(r"(?<![A-Z])\.\s")

records = []
for e in entries:
    raw = join(e["parts"])
    rec = {"n": e["n"], "raw": raw}

    arx = re.search(r"arXiv[:\s]*(\d{4}\.\d{4,5})", raw, re.I)
    if arx:
        rec["arxiv"] = arx.group(1)
    doi = re.search(r"\bdoi:\s*(10\.\S+?)(?:[.,]?\s|$)", raw, re.I)
    if doi:
        rec["doi"] = doi.group(1).rstrip(".")
    url = re.search(r"https?://\S+", raw)
    if url:
        rec["url"] = url.group(0).rstrip(".")
    yrs = re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", raw)
    if yrs:
        rec["year"] = int(yrs[-1])       # publication year is the last one cited

    # Strip trailing URL before doing the author/title split.
    head = raw.split(" URL ")[0]
    chunks = [c.strip() for c in SPLIT.split(head) if c.strip()]
    if chunks:
        rec["authors"] = chunks[0]
    if len(chunks) > 1:
        rec["title"] = chunks[1]
    if len(chunks) > 2:
        rec["venue"] = chunks[2]

    records.append(rec)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

ns = [r["n"] for r in records]
missing = sorted(set(range(1, max(ns) + 1)) - set(ns)) if ns else []
print(f"parsed {len(records)} references (numbered 1..{max(ns) if ns else 0})")
print(f"missing numbers: {missing if missing else 'none'}")
print(f"with arxiv id: {sum('arxiv' in r for r in records)}")
print(f"with doi:      {sum('doi' in r for r in records)}")
print(f"with url:      {sum('url' in r for r in records)}")
print(f"with title:    {sum('title' in r for r in records)}")
