"""Deduplicate and clean the crawled graph into data/graph.json.

Three problems in the raw crawl, all artifacts of parsing 96 different papers'
bibliographies rendered by LaTeXML:

1. Year theft. arXiv ids look like years -- "arXiv:2005.14165" (GPT-3) yields
   "2005", "arXiv:2012.14913" yields "2012". Strip identifiers before scanning.
2. Split identity. The same paper is one node when a bibliography hyperlinks
   arXiv and a different node when it does not. Merge on normalized title,
   preferring the arXiv-keyed id so edges collapse onto a real identifier.
3. Affiliation bleed. LaTeXML folds "Affiliation:", "Thanks:", "Email:" and
   correspondence lines into the first bibblock, so the authors field arrives
   with a paragraph of noise attached.
"""
import collections
import json
import pathlib
import re
import unicodedata

DATA = pathlib.Path(__file__).parent / "data"
SEED = "arXiv:2607.15495"

nodes = json.loads((DATA / "nodes.json").read_text(encoding="utf-8"))
edges = json.loads((DATA / "edges.json").read_text(encoding="utf-8"))

NOISE = re.compile(
    r"\b(Affiliation|Thanks|Email|Correspondence(\s+to)?|Equal contribution|"
    r"denotes equal|Work done during|Code and data|Open-source code)\b.*",
    re.I | re.S)
# LaTeXML also emits bare superscript affiliation markers ("Evan Hernandez 1 1 1
# Massachusetts Institute of Technology"), so cut at the first institution word
# and drop the orphaned digit runs it leaves behind.
INSTITUTION = re.compile(
    r"\s+\d*\s*\b(University|Universite|Universität|Institute|Institut|College|"
    r"Laborator(y|ies)|\bLab\b|School of|Center for|Centre for|Technion|MIT|"
    r"DeepMind|Google|Anthropic|OpenAI|Meta AI|Microsoft|EleutherAI|Eleuther AI|"
    r"FAR AI|Northeastern|Carnegie Mellon|Stanford|Berkeley|Tel Aviv|"
    r"Independent researcher|Center for AI Safety)\b.*", re.I | re.S)
DIGIT_RUN = re.compile(r"\s+\d+(\s+\d+)*\s*$")
# A run of standalone digits is always a superscript affiliation marker here, and
# everything after it belongs to the institution, not the author list.
SUPERSCRIPT_CUT = re.compile(r"\s+\d+(?:\s+\d+)*(?=\s|$).*", re.S)
IDENT = re.compile(r"(arxiv[:\s]*)?\b\d{4}\.\d{4,5}(v\d+)?\b", re.I)


def clean_authors(a):
    if not a:
        return None
    a = NOISE.sub("", a)
    a = SUPERSCRIPT_CUT.sub("", a)
    a = INSTITUTION.sub("", a)
    a = re.sub(r"\s*[∗*†‡§¶]+\s*", " ", a)
    a = DIGIT_RUN.sub("", a)
    a = re.sub(r"\s+", " ", a).strip(" ,.;:")
    return a[:200] or None


def norm_title(t):
    """Aggressive normalization -- titles differ in case, punctuation, and
    LaTeXML's stray spacing across bibliographies."""
    if not t:
        return None
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t if len(t) > 14 else None      # too short to key on safely


def best_year(rec):
    """Year from the raw string, with arXiv-style identifiers removed first."""
    for field in ("raw", "title", "authors"):
        s = rec.get(field)
        if not s:
            continue
        s = IDENT.sub(" ", s)
        yrs = [int(y) for y in re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", s)]
        if yrs:
            return max(yrs)
    return None


# ---- pass 1: choose a canonical id per normalized title ---------------------
by_title = collections.defaultdict(list)
for n in nodes:
    nt = norm_title(n.get("title"))
    if nt:
        by_title[nt].append(n)

canon = {}                      # old id -> canonical id
for nt, group in by_title.items():
    if len(group) == 1:
        continue
    # Prefer a node with a real arXiv id; among those prefer the one we crawled.
    group.sort(key=lambda n: (bool(n.get("arxiv")), bool(n.get("html"))), reverse=True)
    keep = group[0]["id"]
    for n in group[1:]:
        canon[n["id"]] = keep

merged = collections.Counter(canon.values())

# ---- pass 2: rebuild nodes -------------------------------------------------
out = {}
for n in nodes:
    nid = canon.get(n["id"], n["id"])
    rec = out.setdefault(nid, {"id": nid})
    for k, v in n.items():
        if k == "id" or v in (None, ""):
            continue
        rec.setdefault(k, v)
    rec["depth"] = min(rec.get("depth", 99), n.get("depth", 99))

for rec in out.values():
    rec["authors"] = clean_authors(rec.get("authors"))
    y = best_year(rec)
    if y:
        rec["year"] = y
    elif "year" in rec:
        del rec["year"]
    rec.pop("raw", None)

# ---- pass 3: rebuild edges, dropping self-loops and duplicates -------------
seen, out_edges = set(), []
for e in edges:
    a = canon.get(e["from"], e["from"])
    b = canon.get(e["to"], e["to"])
    if a == b or (a, b) in seen:
        continue
    seen.add((a, b))
    out_edges.append({"from": a, "to": b,
                      "n_cites": e.get("n_cites", 0),
                      "sections": e.get("sections", [])})

indeg = collections.Counter(e["to"] for e in out_edges)
for nid, rec in out.items():
    rec["in_degree"] = indeg.get(nid, 0)
    rec["seed_ref"] = any(e["from"] == SEED and e["to"] == nid for e in out_edges)

(DATA / "graph.json").write_text(
    json.dumps({"seed": SEED, "nodes": list(out.values()), "edges": out_edges},
               indent=2, ensure_ascii=False), encoding="utf-8")

print(f"nodes  {len(nodes)} -> {len(out)}   ({len(canon)} merged away)")
print(f"edges  {len(edges)} -> {len(out_edges)}")
print(f"with year: {sum('year' in r for r in out.values())}")
print(f"seed refs: {sum(r['seed_ref'] for r in out.values())}")
print("\ntop merges:")
for nid, c in merged.most_common(5):
    print(f"  {c+1} copies -> {(out[nid].get('title') or nid)[:70]}")
print("\ntop by in-degree after dedup:")
for nid, c in indeg.most_common(12):
    r = out[nid]
    mark = "*" if r["seed_ref"] else " "
    print(f"  {c:>3} {mark} {(r.get('authors') or '').split(',')[0][:22]:<22} "
          f"{r.get('year') or '----'}  {(r.get('title') or '')[:60]}")
