# 01 — The primary source

## Citation

Wes Gurnee\*, Nicholas Sofroniew\*, Adam Pearce, Mateusz Piotrowski, Isaac Kauvar, Runjin Chen,
Anna Soligo, Paul Bogdan, Euan Ong, Rowan Wang, T. Ben Thompson, David Abrahams,
Subhash Kantamneni, Emmanuel Ameisen, Joshua Batson, Jack Lindsey\*†.
**"Verbalizable Representations Form a Global Workspace in Language Models."**
Transformer Circuits Thread, Anthropic, **6 July 2026**.
(\* core contributor, † correspondence: jacklindsey@anthropic.com)

| | |
|---|---|
| Canonical | https://transformer-circuits.pub/2026/workspace/index.html |
| arXiv | [2607.15495](https://arxiv.org/abs/2607.15495), submitted 16 July 2026, cs.CL / cs.AI / cs.LG |
| Code | https://github.com/anthropics/jacobian-lens |
| Interactive | https://www.neuronpedia.org/qwen3.6-27b/jlens · [Neuronpedia writeup](https://www.neuronpedia.org/blog/jacobian-lens) |
| Lab blog | https://www.anthropic.com/research/global-workspace |
| Commentary | [external commentary volume](../sources/anthropic-external-commentary.pdf) (53 pp, 3 invited pieces) |
| Local | `sources/gurnee-2026-jspace.pdf` (117 pp) + `.txt` |

Models: **Claude Sonnet 4.5** as default; main results reproduced on Haiku 4.5 and Opus 4.5, with
additional checks on Opus 4.6.

## The method

For each layer ℓ:

```
J_ℓ = E_{t, t'≥t, prompt} [ ∂h_final,t' / ∂h_ℓ,t ]
```

Expectation over the source position `t`, **all subsequent positions** `t' ≥ t`, and a corpus of
~1000 prompts from a pretraining-like distribution. Applying the lens to an activation is
equivalent to replacing all subsequent layers with the lens matrix, then unembedding as normal:

```
lens(h_ℓ) = softmax( W_U · norm( J_ℓ · h_ℓ ) )
```

**J-lens vectors** = the rows of `W_U J_ℓ`. One residual-stream direction per vocabulary token;
`n_vocab > d_model`, so the set is overcomplete.

**J-space** = points expressible as a *sparse nonnegative* combination of J-lens vectors, with
sparsity k typically ≤ 25 ("the number of J-lens vectors that are meaningfully active at a given
time"). Membership for a given activation, steering vector, or SAE feature direction is solved by
**gradient pursuit** (Blumensath & Davies 2008, ref [19]).

Framed against superposition: under the superposition hypothesis a model's activations decompose
as sparse combinations from an overcomplete **sparse frame** of feature directions. The paper's
positioning is that J-lens vectors are a **subframe** of that frame — a token-indexed subset of
the model's feature directions. This is the load-bearing theoretical claim linking J-space to the
SAE literature, and it is stated as an interpretation, not demonstrated exhaustively.

The averaging is the conceptual core: it separates representations *genuinely poised for report*
from ones that merely leak into the output in one particular context.

### Why the expectation over future positions matters

The `t' ≥ t` term is what distinguishes J-lens from every prior vocabulary-space lens. Nanda's
commentary confirms this is where the gains come from: J-lens variants restricted to a *single*
token only mildly outperform logit lens, and "the performance gap is explained by allowing future
tokens." J-space is about what the model is poised to say *eventually*, not next.

## Claims

**Five functional signatures of access consciousness** (§3):
1. **Verbal report** — contents can be reported
2. **Directed modulation** — "hold X in mind" works; contents can be deliberately summoned and held
3. **Internal reasoning** — carries intermediate steps of silent, unverbalized reasoning
4. **Flexible generalization** — passed as arguments to arbitrary downstream computations
5. **Selectivity** — mediates deliberate reasoning, *not* automatic fluency (text parsing and
   routine inference proceed without it)

**Structural signatures** (§4):
- Coherent content only in an **intermediate band of layers** (roughly ⅓–⅔ depth)
- Holds **on the order of tens of concepts** at a time
- **Broadcast by the model's weights more widely** than other representations (§4.3, "broadcast hub")
- Carries **<10% of activation variance** in any given layer

**Applications** (§5, §6):
- Alignment audits: surfaces strategic deliberation, evaluation awareness, and trained-in
  misaligned dispositions that never appear in outputs
- Post-training installs the **Assistant's point of view** into the workspace
- **Counterfactual reflection training** — trains only what a model would say if interrupted and
  asked to reflect, and improves behavior

### The signature experiments

- **Concept swap** — read a concept out of J-space, swap it, watch reasoning change. A Spanish
  passage is recognized as Spanish even when the task never asks. Swap Spanish→French and the
  model reports "French", says "Bonjour" for hello, and "Franc" for the pre-Euro currency — but
  **keeps writing in Spanish**. Automatic next-token prediction is untouched. (Fig. 20)
- **Massive ablation** of top J-space representations leaves most basic capacities intact but
  selectively impairs flexible reasoning. (Fig. 24)
- **Held content** — "compute 3²−2 while writing sentence X" puts the unreported 9 and 7 into J-space.
- **Task-dependent entry** — character counts per line are tracked automatically and stay *out* of
  J-space, but enter it when a task requires manipulating them. Same information crossing from the
  automatic to the accessible regime on demand.
- **Multi-step arithmetic** (Fig. 17) — intermediates probe well at discrete layer bands, in the
  predicted order.
- **Bandit** (Fig. 14) — happy/sad → switch/repeat stored at the end-of-turn full stop, causally
  upstream of the A/B answer.

## Provenance notes

Two figures circulating in secondary coverage that I could **not** confirm against the paper text
and should not be repeated without checking: "median 6–7% of variance" and "swap along it and the
answer flips 59% of the time". The paper and Dehaene & Naccache's commentary both support the
weaker, clearly-sourced "<10% of variance". Treat the specific percentages as unverified.

## Bibliography

171 references, numbered 1–171 with no gaps, extracted twice independently (PDF regex parse and
arXiv LaTeXML parse) with identical counts. **Every one is cited in-text** — 263 inline citations
total, zero listed-but-uncited.

Distribution of in-text citations by section:

| n | section |
|---|---|
| 113 | 8 Related work |
| 21 | 1.1 Motivation: conscious access and the global workspace |
| 16 | 9.4 Relationship to theories of consciousness |
| 13 | 1.2 A global workspace in language models |
| 13 | 9.3 Notable differences from human cognition |
| 11 | A.24 Applying the J-lens to mechanistic interpretability |
| 10 | 3.5 The J-space selectively mediates flexible but not automatic cognition |

Most-cited (in-text count):

| n | reference |
|---|---|
| 7× | Lindsey et al. 2025, *On the biology of a large language model* |
| 6× | Ameisen et al. 2025, *Circuit tracing* |
| 6× | Fraser-Taliente et al. 2026, *Natural language autoencoders* |
| 6× | Mashour et al. 2020, *Conscious processing and the global neuronal workspace hypothesis* |
| 5× | Baars 1988, *A Cognitive Theory of Consciousness* |
| 5× | Dehaene & Naccache 2001, *Towards a cognitive neuroscience of consciousness* |
| 4× | Bricken et al. 2023, *Towards monosemanticity* |
| 4× | Dehaene et al. 1998, *A neuronal model of a global workspace* |
| 4× | Elhage et al. 2021, *A mathematical framework for transformer circuits* |
| 4× | Gurnee et al. 2025, *When models manipulate manifolds* |
| 4× | Templeton et al. 2024, *Scaling monosemanticity* |

The shape of that list is the paper in miniature: Anthropic's own circuit-tracing stack, the SAE
line, and the Baars/Dehaene workspace tradition, in roughly equal measure.
