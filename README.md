# jspace

Research project on **J-space** — the "directional axis space" named by Anthropic in July 2026 —
and on the much older lineage of work that treats *concepts as directions in latent space*.

The goal is coverage, not a quick summary: find everything, follow every lead, and keep the
citation structure machine-readable so it can be explored visually.

## Status

| Phase | State |
|---|---|
| Primary source located, read, archived | done |
| Bibliography extracted (171 refs, complete) | done |
| Citation graph, depth 2 | done — **3,129 nodes / 5,011 edges / 8,194 citation contexts** from 96 crawled papers |
| Reception / commentary / replication | done — all three invited commentaries read |
| TCAV ↔ J-lens relationship, verified from both primaries | done |
| Visual graph explorer | done — `index.html`, self-contained, force + provenance layouts |
| Forward citation cone (who cites it since 2026-07) | **not started** — needs an S2 key; see [notes/04](notes/04-open-threads.md) |

### The backbone of this literature

In-degree over the deduplicated depth-2 graph — how many of the 96 crawled papers cite each work.
`*` marks a direct reference of the J-space paper.

| in-deg | | work |
|---|---|---|
| 34 | | Vaswani et al. 2017 — *Attention is all you need* |
| **29** | **\*** | **nostalgebraist 2020 — *Interpreting GPT: the logit lens*** |
| 28 | \* | Elhage et al. 2021 — *A mathematical framework for transformer circuits* |
| 26 | | Radford et al. 2019 — GPT-2 |
| 26 | | Brown et al. 2020 — GPT-3 |
| 25 | | Meng et al. — *Locating and editing factual associations in GPT* (ROME) |
| 22 | \* | Belrose et al. 2023 — *Tuned lens* |
| 22 | \* | Bricken et al. 2023 — *Towards monosemanticity* |
| 21 | \* | Cunningham et al. 2023 — *Sparse autoencoders find highly interpretable features* |
| 20 | \* | Geva et al. 2022 — *FF layers build predictions by promoting concepts in the vocabulary space* |
| 19 | \* | Olsson et al. 2022 — *In-context learning and induction heads* |
| 18 | \* | Elhage et al. 2022 — *Toy models of superposition* |

A LessWrong post from 2020 is the second most-cited work in this entire literature, ahead of the
transformer-circuits framework and every model paper except the originals. Excluding the
architecture and model releases, the top of the list is almost exactly two threads:
**read the residual stream in vocabulary coordinates** (logit lens → Geva → tuned lens → J-lens)
and **superposition / dictionary learning** (toy models → monosemanticity → SAEs). J-space sits at
the confluence.

## What J-space is

From Gurnee et al. 2026 (§2), stated precisely rather than journalistically:

For each layer ℓ,

```
J_ℓ = E_{t, t'≥t, prompt} [ ∂h_final,t' / ∂h_ℓ,t ]
```

— an average Jacobian from the residual stream at layer ℓ, position `t`, to the final-layer
residual stream at *every subsequent position* `t'`, expectated over ~1000 pretraining-like
prompts. Applying it:

```
lens(h_ℓ) = softmax( W_U · norm( J_ℓ · h_ℓ ) )
```

The **J-lens vectors** are the rows of `W_U J_ℓ`: one direction in residual-stream space per
vocabulary token. Because `n_vocab > d_model` they form an overcomplete set. The **J-space** is
the set of points expressible as a *sparse nonnegative* combination of J-lens vectors — in
practice k ≤ ~25, chosen because that is roughly how many are meaningfully active at once.
Membership is solved with gradient pursuit (Blumensath & Davies 2008).

The logit lens is the special case `J_ℓ = I`.

So "j-space is a directional axis space" is exactly right: it is a token-indexed frame of
directions, and the claim is that this particular frame is *privileged* — the model can report,
hold, manipulate, and reason with whatever it projects onto, and mostly cannot with the rest.

## Layout

```
index.html   the citation-graph explorer (generated; this is what Pages serves)
data/        machine-readable graph: nodes.json, edges.json, cite_contexts.json, references.json
notes/       the research write-up
sources/     archived primary documents + cached arXiv HTML — gitignored, see below
```

`sources/` is not committed: it is 25 MB+ of publisher PDFs that are re-derivable and not ours to
redistribute. To rebuild it:

```bash
python arxiv_graph.py --depth 2
```

That re-fetches and caches the arXiv HTML for every crawlable reference. The three PDFs read by
hand — the paper itself, the Dehaene & Naccache commentary, and the external commentary volume —
are linked in [notes/01](notes/01-primary-source.md); `python pdftext.py <pdf>` extracts them.

## The explorer

```bash
python build_viewer.py
```

Writes `index.html` at the repo root — one self-contained file, data inlined (fetch is blocked on
`file://`, and it keeps GitHub Pages to a single static file). Serve it with any static server:

```bash
python -m http.server 8825
```

Clicking a paper opens a panel with its metadata, an **open paper** link to the real source
(arxiv.org, transformer-circuits.pub, lesswrong.com, ACL, NeurIPS — 126 of the 171 references
resolve to a real URL; the remaining 45 are books and journal articles with no URL in the
bibliography, and fall back to a search).

Default view is the seed plus its 171 direct references, 730 citations among them. Nodes are sized
by how many papers in the crawl cite them and coloured by lineage cluster; `+ depth 2` adds
depth-2 papers with in-degree ≥ 4 (311 nodes) rather than all 3,129, which would be a hairball.

The part worth having is the **section filter**. Because the crawler kept every inline `\cite` in
place, you can ask what a specific section of the J-space paper leans on. Picking
*"2.4 Comparison to Related Techniques"* leaves six papers on screen — the seed, tuned lens, LRE,
logit lens, Future Lens, and Jump to Conclusions. That is the methodological ancestry from
[notes/02](notes/02-lineage.md), isolated by one dropdown. Clicking any node shows the actual
sentences it was cited in, with the section each came from.

Lineage clusters are keyword-assigned from the notes and are a reading aid, not ground truth —
5 of the 171 refs stay in `other`, which is honest rather than forced.

### Provenance view

`provenance view` swaps the force layout for a time-ordered one: **year on the x axis, one lane per
lineage**, so each cluster reads as a tree growing left to right and the whole thing as a forest
converging on the J-space paper at the top right. Citations are drawn as S-curves from the older
work to the newer one, so every edge points the way influence actually flows.

Selecting a node here highlights its **transitive** ancestry and descent, not just its immediate
neighbours, and the panel reports both counts. That is what makes it a provenance view rather than
a prettier graph — you can ask what a paper ultimately rests on, and what ultimately rests on it.

Read at depth 2, it separates two kinds of node cleanly:

| | |
|---|---|
| **nostalgebraist 2020**, logit lens | 0 ancestors, **63 descendants** — a true root of the forest |
| **Belrose 2023**, tuned lens | 61 ancestors, 58 descendants — a midpoint |

The logit lens having *zero* ancestors is not a data gap in the usual sense: it is a LessWrong post,
not an arXiv paper, so there is no bibliography to crawl. The most-descended node in the
vocabulary-space lineage is a blog post — which is the same point the in-degree table makes, in a
different shape.

The literal roots of the forest, ranked by transitive descent at depth 2, are the architecture and
model papers: Vaswani 2017 (81), BERT (76), GPT-3 (76), GPT-2 (74), Show-Attend-Tell (71),
Zeiler & Fergus (68), ResNet (68), ELMo (68).

## Tooling

```bash
python arxiv_graph.py --depth 2
```

Builds the citation graph from **arXiv's LaTeXML HTML** rather than a citation API. This was the
right call for three reasons: no rate limit (Semantic Scholar's unauthenticated pool returned
429 on every retry), the bibliography comes out already structured, and — the part no API
offers — every inline `\cite` keeps its position, so each edge carries the *section it was cited
from* and a sentence of surrounding context. Falls back to ar5iv for pre-2024 papers, and records
`html: false` for anything that resolves to neither, so coverage gaps stay visible.

```bash
python clean.py          # dedup + repair -> data/graph.json  (the canonical artifact)
python parse_refs.py     # independent bibliography parse from the PDF (cross-check)
python analyze.py        # rank references by in-text citation count and citing section
python hubs.py           # in-degree ranking over the depth-2 graph
python pdftext.py <pdf>  # PyMuPDF text extraction
```

`clean.py` exists because the raw crawl parses 96 different bibliographies rendered by LaTeXML and
inherits three failure modes worth knowing about if you extend this:

- **Year theft** — arXiv identifiers look like years. `arXiv:2005.14165` dated GPT-3 to 2005 and
  `arXiv:2012.14913` dated Geva's key-value memories to 2012. Identifiers are stripped before the
  year scan.
- **Split identity** — the same paper becomes two nodes when one bibliography hyperlinks arXiv and
  another only prints the title. Merging on a normalized title collapsed **1,227** duplicates;
  *Attention is all you need* alone had 33 copies.
- **Affiliation bleed** — LaTeXML folds `Affiliation:` / `Thanks:` / `Email:` lines into the first
  bibblock, so raw author strings arrive with a paragraph attached.

Counts quoted anywhere in these notes are post-clean.

`parse_refs.py` and `arxiv_graph.py` are deliberately redundant — two independent extractions of
the same bibliography. Both return 171 entries numbered 1–171 with no gaps, which is the main
reason to trust either.

`harvest.ps1` is the abandoned Semantic Scholar path. Kept because it becomes viable with an API
key, and the forward citation cone (who cites J-space) still needs a source that arXiv HTML
cannot provide.

## Notes

- [01 — Primary source](notes/01-primary-source.md)
- [02 — Lineage: concepts as directions](notes/02-lineage.md)
- [03 — Reception](notes/03-reception.md)
- [04 — Open threads](notes/04-open-threads.md)
