"""What does the J-space paper actually lean on, and where?

Ranks the seed's references by how often they are cited in-text (not just
listed), and groups them by the section that cites them -- which is the fastest
way to see the intellectual lineage the authors are actually working from.
"""
import collections
import json
import pathlib

DATA = pathlib.Path(__file__).parent / "data"
SEED = "arXiv:2607.15495"

nodes = {n["id"]: n for n in json.loads((DATA / "nodes.json").read_text(encoding="utf-8"))}
edges = json.loads((DATA / "edges.json").read_text(encoding="utf-8"))
ctx = json.loads((DATA / "cite_contexts.json").read_text(encoding="utf-8"))


def label(nid):
    n = nodes.get(nid, {})
    a = (n.get("authors") or n.get("raw") or nid)
    a = a.split(",")[0].strip() or nid
    y = n.get("year") or ""
    t = (n.get("title") or "")[:70]
    return f"{a} {y} — {t}"


print("=" * 78)
print("MOST-CITED REFERENCES INSIDE THE J-SPACE PAPER (by in-text citation count)")
print("=" * 78)
seed_edges = [e for e in edges if e["from"] == SEED and e["n_cites"] > 0]
for e in sorted(seed_edges, key=lambda e: -e["n_cites"])[:30]:
    secs = ", ".join(e["sections"][:3]) or "—"
    print(f'{e["n_cites"]:>2}x  {label(e["to"])[:78]}')
    print(f'      in: {secs[:96]}')

print()
print("=" * 78)
print("CITATIONS BY SECTION")
print("=" * 78)
by_sec = collections.Counter(c["section"] for c in ctx if c["section"])
for sec, n in by_sec.most_common(25):
    print(f"{n:>3}  {sec}")

print()
print(f"references listed: {len([e for e in edges if e['from'] == SEED])}")
print(f"never cited in-text (listed only): {len([e for e in edges if e['from'] == SEED and e['n_cites'] == 0])}")
