"""Build the jspace citation graph from arXiv's LaTeXML HTML.

Why HTML and not an API: arXiv renders LaTeX submissions to HTML with stable
LaTeXML classes, so a paper's bibliography comes out structured *and* every
inline \\cite keeps its position in the document. That gives us edges plus the
section each citation was made from -- context Semantic Scholar does not expose
-- and there is no rate limit beyond being polite.

Coverage: arxiv.org/html exists for LaTeX submissions from ~Dec 2023 onward.
Older papers fall back to ar5iv, which backfilled the same renderer. Anything
that resolves to neither is recorded with `html: false` so the gaps are visible
rather than silently dropped.

Usage:
    python arxiv_graph.py --depth 1        # seed's refs only
    python arxiv_graph.py --depth 2        # + refs of every arXiv ref
"""
import argparse
import json
import pathlib
import re
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
CACHE = ROOT / "sources" / "html"
DATA = ROOT / "data"
SEED = "2607.15495"

UA = {"User-Agent": "jspace-research/0.1 (citation graph; nathaniel.gibson@gmail.com)"}
DELAY = 3.0                      # arXiv asks for a few seconds between hits
ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")


# ------------------------------------------------------------------ fetching
def cache_path(aid):
    return CACHE / f"{aid}.html"


def fetch_html(aid):
    """Return (html, source) for an arXiv id, or (None, None). Cached on disk."""
    cp = cache_path(aid)
    meta = CACHE / f"{aid}.source"
    if cp.exists():
        src = meta.read_text(encoding="utf-8").strip() if meta.exists() else "cache"
        return cp.read_text(encoding="utf-8", errors="replace"), src

    for url in (f"https://arxiv.org/html/{aid}",
                f"https://ar5iv.labs.arxiv.org/html/{aid}"):
        try:
            r = requests.get(url, headers=UA, timeout=60, allow_redirects=True)
        except Exception as e:
            print(f"    {aid}: {type(e).__name__} on {url}")
            time.sleep(DELAY)
            continue
        time.sleep(DELAY)
        if r.status_code != 200 or len(r.text) < 5000:
            continue
        # ar5iv serves a styled "not available" stub for papers it never built.
        if "ltx_biblist" not in r.text and "ltx_bibitem" not in r.text:
            continue
        CACHE.mkdir(parents=True, exist_ok=True)
        cp.write_text(r.text, encoding="utf-8")
        meta.write_text(url, encoding="utf-8")
        return r.text, url
    return None, None


# ------------------------------------------------------------------ parsing
def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def parse_biblio(soup):
    """Extract bibliography entries keyed by their LaTeXML anchor id."""
    out = {}
    for li in soup.select("li.ltx_bibitem"):
        key = li.get("id") or ""
        blocks = [clean(b.get_text(" ")) for b in li.select("span.ltx_bibblock")]
        raw = clean(" ".join(blocks)) or clean(li.get_text(" "))
        # Strip the leading "[12]" tag if LaTeXML folded it into the text.
        raw = re.sub(r"^\[\d+\]\s*", "", raw)

        rec = {"key": key, "raw": raw}
        # Prefer an explicit arXiv link over regex over the whole string, which
        # can pick up a page number that happens to look like an id.
        for a in li.select("a[href]"):
            href = a["href"]
            if "arxiv.org" in href:
                m = ARXIV_RE.search(href)
                if m:
                    rec["arxiv"] = m.group(1)
                    break
        if "arxiv" not in rec:
            m = re.search(r"arXiv[:\s]*(\d{4}\.\d{4,5})", raw, re.I)
            if m:
                rec["arxiv"] = m.group(1)
        m = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", raw)
        if m:
            rec["year"] = int(m.group(1))
        if blocks:
            rec["authors"] = blocks[0].rstrip(".")
            if len(blocks) > 1:
                rec["title"] = blocks[1].rstrip(".")
        out[key] = rec
    return out


def section_of(node):
    """Nearest enclosing section title, for citation context."""
    for parent in node.parents:
        cls = parent.get("class") or []
        if any(c in ("ltx_section", "ltx_subsection", "ltx_appendix") for c in cls):
            h = parent.find(class_=re.compile(r"ltx_title_(sub)?section|ltx_title_appendix"))
            if h:
                return clean(h.get_text(" "))
    return None


def parse_inline_cites(soup):
    """Every inline \\cite: which bib entry, from which section, in what sentence."""
    cites = []
    for c in soup.select("cite.ltx_cite"):
        targets = [a["href"].lstrip("#") for a in c.select("a[href^='#bib']")]
        if not targets:
            continue
        para = c.find_parent("p") or c.parent
        text = clean(para.get_text(" ")) if para else ""
        # Keep a window around the citation rather than a whole paragraph.
        marker = clean(c.get_text(" "))
        idx = text.find(marker) if marker else -1
        snippet = text[max(0, idx - 260): idx + 140] if idx >= 0 else text[:400]
        sec = section_of(c)
        for t in targets:
            cites.append({"bib": t, "section": sec, "context": snippet})
    return cites


def paper_meta(soup, aid):
    t = soup.select_one("h1.ltx_title_document") or soup.select_one("h1.ltx_title")
    authors = soup.select_one(".ltx_authors")
    return {
        "id": f"arXiv:{aid}",
        "arxiv": aid,
        "title": clean(t.get_text(" ")) if t else None,
        "authors": clean(authors.get_text(" "))[:400] if authors else None,
        "url": f"https://arxiv.org/abs/{aid}",
    }


# ------------------------------------------------------------------ crawl
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--seed", default=SEED)
    args = ap.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    nodes, edges, cite_ctx = {}, [], []
    frontier, done = [args.seed], set()

    for depth in range(args.depth):
        print(f"\n== depth {depth}: {len(frontier)} paper(s)")
        nxt = []
        for i, aid in enumerate(frontier, 1):
            if aid in done:
                continue
            done.add(aid)
            html, src = fetch_html(aid)
            if not html:
                print(f"  [{i}/{len(frontier)}] {aid}: NO HTML")
                nodes.setdefault(f"arXiv:{aid}", {"id": f"arXiv:{aid}", "arxiv": aid,
                                                  "html": False, "depth": depth})
                continue

            soup = BeautifulSoup(html, "lxml")
            meta = paper_meta(soup, aid)
            meta["html"] = True
            meta["depth"] = depth
            meta["source"] = src
            nodes[meta["id"]] = {**nodes.get(meta["id"], {}), **meta}

            biblio = parse_biblio(soup)
            inline = parse_inline_cites(soup)
            print(f"  [{i}/{len(frontier)}] {aid}: {len(biblio)} refs, "
                  f"{len(inline)} inline cites  ({(meta['title'] or '')[:52]})")

            # How many times, and from where, this paper cites each reference.
            by_bib = {}
            for c in inline:
                by_bib.setdefault(c["bib"], []).append(c)

            for key, ref in biblio.items():
                tgt = f"arXiv:{ref['arxiv']}" if "arxiv" in ref else f"ref:{aid}:{key}"
                if tgt not in nodes:
                    nodes[tgt] = {"id": tgt, "title": ref.get("title"),
                                  "authors": ref.get("authors"), "year": ref.get("year"),
                                  "arxiv": ref.get("arxiv"), "raw": ref.get("raw"),
                                  "depth": depth + 1, "html": None}
                hits = by_bib.get(key, [])
                edges.append({"from": meta["id"], "to": tgt, "n_cites": len(hits),
                              "sections": sorted({h["section"] for h in hits if h["section"]})})
                for h in hits:
                    cite_ctx.append({"from": meta["id"], "to": tgt,
                                     "section": h["section"], "context": h["context"]})
                if "arxiv" in ref and depth + 1 < args.depth:
                    nxt.append(ref["arxiv"])

        frontier = sorted(set(nxt) - done)

    (DATA / "nodes.json").write_text(json.dumps(list(nodes.values()), indent=2,
                                                ensure_ascii=False), encoding="utf-8")
    (DATA / "edges.json").write_text(json.dumps(edges, indent=2,
                                                ensure_ascii=False), encoding="utf-8")
    (DATA / "cite_contexts.json").write_text(json.dumps(cite_ctx, indent=2,
                                                        ensure_ascii=False), encoding="utf-8")
    resolved = sum(1 for n in nodes.values() if n.get("arxiv"))
    print(f"\nnodes={len(nodes)} (arXiv-resolvable={resolved})  edges={len(edges)}  "
          f"contexts={len(cite_ctx)}")


if __name__ == "__main__":
    main()
