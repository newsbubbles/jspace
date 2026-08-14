# 04 — Open threads

Ordered by what most changes the picture if pursued.

## A. The forward citation cone — the biggest hole

Everything collected so far looks *backward* from the seed. Nothing yet collects **who has cited
J-space since 6 July 2026** (~5 weeks as of 2026-08-14). arXiv HTML cannot give this — it is the
one thing the abandoned Semantic Scholar path was actually good for.

Options, in order of preference:
1. **Semantic Scholar API key** (free, requires signing up). Makes `harvest.ps1` work as written.
2. Poll the unauthenticated S2 endpoint slowly from a background loop — it 429s under burst but
   may pass with minutes between calls.
3. OpenAlex once it indexes the paper — it returned `count=0` on 2026-08-14, so it has lag; retry
   in a few weeks.
4. arXiv full-text search for `2607.15495` to catch citers whose HTML is available.

**Specific question to answer with it:** does anyone citing J-space bridge it back to TCAV /
Mikolov / the pre-2020 concept-direction tradition? That determines whether the gap documented in
[02](02-lineage.md) is a framing choice by this lab or a genuine blind spot in the field.

## B. Close the pre-2020 lineage by hand

The graph crawler only follows arXiv IDs the paper actually cites, so it will never reach the
missing ancestors. Add them as a manually-curated node set with an edge type like
`conceptual_ancestor` (asserted by this project, not by the paper):

- Mikolov et al. 2013 — *Efficient estimation of word representations* / *Linguistic regularities*
- Kim et al. 2018 — **TCAV**. Read closely: it defines a concept as a direction and measures
  **directional derivatives of the output w.r.t. that direction**. That is startlingly close to
  what the averaged Jacobian does. Worth a careful side-by-side — if TCAV's conceptual sensitivity
  score is a special case or near-relative of the J-lens construction, that is a genuinely
  publishable observation and the sharpest thing this project could produce.
- Bolukbasi et al. 2016 — gender direction, identify/measure/edit
- Radford et al. 2017 — sentiment neuron
- Bau et al. — Network Dissection
- Olah et al. — Feature Visualization / Building Blocks / Zoom In (the Distill circuits thread)
- Landauer & Dumais — LSA; Smolensky — distributed representations

## C. Read what is archived but not yet mined

- **Butlin, Shiller, Plunkett & Long commentary** — pp. 623–1306 of
  `sources/anthropic-external-commentary.txt`, entirely unread. The moral-status argument.
- The **117-page paper itself** is on disk as text; only §1–3, §2.4, §8 and the reference list have
  been worked through. Unread and likely load-bearing: **§4** (structural signatures — the section
  Nanda is least convinced by), **§5** (blackmail / evaluation awareness audits), **§6** (Assistant
  point of view), **§7** (counterfactual reflection training), **§9.3–9.4** (differences from human
  cognition; other theories), and appendices **A.6/A.7** (evals and reproduction details Nanda
  calls the most useful part), **A.9** (multi-token extension), **A.18** (features in the J-space —
  the SAE relationship), **A.19** (alternative broadcast quantifications), **A.24** (J-lens for
  mechanistic interpretability).
- [github.com/anthropics/jacobian-lens](https://github.com/anthropics/jacobian-lens) — not yet
  cloned or read. The implementation is ground truth for the method.
- [Neuronpedia J-lens](https://www.neuronpedia.org/qwen3.6-27b/jlens) and its
  [blog post](https://www.neuronpedia.org/blog/jacobian-lens) — an open-weights deployment to poke at.
- LessWrong ["A Research Engineer's Analysis"](https://www.greaterwrong.com/posts/vHxGD5HKsFuBStirq/anthropic-s-j-lens-a-research-engineer-s-analysis).

## D. Verify or kill the loose numbers

Secondary coverage repeats "median 6–7% of variance" and "swap flips the answer 59% of the time".
Neither is confirmed from the paper. Either find them in §4 / the appendices and cite the figure,
or strike them from the notes.

## E. The 2026 frontier in the bibliography

Papers newer than most training data, worth reading as the live edge of the field:

| ref | work |
|---|---|
| [7] | Arora, Wu, Steinhardt & Schwettmann 2026 — *Language model circuits are sparse in the neuron basis* (arXiv 2601.22594) |
| [8] | Atad et al. 2026 — *TensorLens* (2601.17958) |
| [46] | Fraser-Taliente et al. 2026 — *Natural language autoencoders* (cited 6×) |
| [47] | Asvin G, Lindsey et al. 2026 — *From simulation to enaction* |
| [48] | Gandikota & Bau 2026 — *Gaze heads: how VLMs look at what they describe* |
| [85] | Krojer et al. 2026 — *LatentLens* |
| [101] | Lu et al. 2026 — *The assistant axis* |
| [140] | Sofroniew et al. 2026 — *Emotion concepts and their function in an LLM* |
| [154] | Urbina-Rodriguez et al. 2026 — *A brain-like synergistic core in LLMs* |

## F. Build the visual explorer

`graph/` is empty. `data/nodes.json`, `edges.json`, and `cite_contexts.json` are the input. The
thing that would make it worth building rather than just using an off-the-shelf viewer is the
**citation context** — each edge knows which section cited it and carries a sentence of
surrounding text, so the graph can be filtered by *"show only what §8 Related Work cites"* vs
*"only what the Methods lean on"*. Colour by lineage cluster (lens / direction / GWT / Anthropic),
size by in-text citation count.

## G. Reproduce something

Lowest-cost real experiment available, and the reason it is cheap is documented: Nanda got a
working J-lens with **n=25 prompts**, and n=1 is "respectable". Cost is `O(n · d_model)` backward
passes.

`D:\face` already probes a residual stream on gemma-3-1b and reproduces the emotion-vector work of
**ref [140] — by Sofroniew, co-first-author of this paper.** The delta from that rig to a working
J-lens is the averaged Jacobian and the unembedding projection. Given the
[GTX 1080 thermal throttle](../../.claude/projects/D--/memory/gtx1080-thermal-throttle.md) that is
still a RunPod job, but a small one.

Open question that would make it more than a replication: does the emotion-concept axis from [140]
lie **inside** J-space? The paper provides the test — solve for a sparse nonnegative combination of
k J-lens vectors approximating a given steering vector via gradient pursuit. Running that on the
emotion vectors connects two Anthropic results that have not been connected in public.
