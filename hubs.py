"""Rank the depth-2 graph by in-degree: what does the J-space literature collectively rest on?

In-degree here means "how many distinct papers in this crawl cite it", which is a
co-citation signal over a corpus that was selected by one paper's bibliography --
so it reads as the shared backbone of the field J-space sits in.
"""
import collections
import json
import pathlib

DATA = pathlib.Path(__file__).parent / "data"
SEED = "arXiv:2607.15495"

nodes = {n["id"]: n for n in json.loads((DATA / "nodes.json").read_text(encoding="utf-8"))}
edges = json.loads((DATA / "edges.json").read_text(encoding="utf-8"))

indeg = collections.Counter()
for e in edges:
    indeg[e["to"]] += 1

seed_refs = {e["to"] for e in edges if e["from"] == SEED}
crawled = {n["id"] for n in nodes.values() if n.get("html")}

print(f"nodes {len(nodes)}  edges {len(edges)}  crawled-with-html {len(crawled)}")
print(f"depth-1 refs of seed: {len(seed_refs)}")
print()

def title_of(nid):
    n = nodes.get(nid, {})
    t = n.get("title") or (n.get("raw") or "")[:80]
    a = (n.get("authors") or "").split(",")[0].strip()
    y = n.get("year") or ""
    return f"{a} {y} — {t}"[:104]

print("=" * 96)
print("MOST-CITED ACROSS THE WHOLE DEPTH-2 GRAPH  (* = also a direct reference of the J-space paper)")
print("=" * 96)
for nid, c in indeg.most_common(35):
    mark = "*" if nid in seed_refs else " "
    print(f"{c:>4}  {mark} {title_of(nid)}")

print()
print("=" * 96)
print("HIGH IN-DEGREE BUT *NOT* CITED BY THE J-SPACE PAPER  (what its neighbours read that it didn't)")
print("=" * 96)
shown = 0
for nid, c in indeg.most_common(400):
    if nid in seed_refs or nid == SEED:
        continue
    print(f"{c:>4}    {title_of(nid)}")
    shown += 1
    if shown >= 30:
        break
