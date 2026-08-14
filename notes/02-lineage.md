# 02 — Lineage: concepts as directions in latent space

The J-space paper coined a name. It did not invent the idea that concepts live along directions
in a latent space, and its own bibliography shows which parts of that history it draws on and
which it skips.

Three distinct ancestries converge in the paper. Reference numbers `[n]` are the paper's own.

---

## A. The vocabulary-space "lens" lineage — the *methodological* parent

This is where J-lens literally comes from: project an intermediate activation into vocabulary
space and read off tokens.

| ref | work | relation to J-lens |
|---|---|---|
| [118] | **nostalgebraist 2020**, *interpreting GPT: the logit lens* (LessWrong) | **The direct ancestor.** J-lens with `J_ℓ = I`. Works in late layers because of residual connections; degrades earlier. |
| [12] | **Belrose et al. 2023**, *tuned lens* | Trains per-layer linear maps to match output distribution. Paper's objection: **correlational, not causal**; on prompts with unverbalized intermediate computation it "skips ahead" to the output instead of surfacing the intermediates. |
| [51] | Geva et al. 2022 | FFN layers build predictions by promoting concepts in vocabulary space |
| [34] | Dar et al. 2023 | Analyzing transformers in embedding space |
| [167] | Yom Din et al. 2024 | Jump to conclusions: short-cutting transformers with linear transformations |
| [122] | **Pal et al. 2023**, *Future Lens* | Anticipating **subsequent** tokens from a single hidden state — closest in spirit to the `t' ≥ t` term |
| [80] | Katz et al. 2024, *Backward lens* | Projecting **gradients** into vocabulary space |
| [53] | Ghandeharioun et al. 2024, *Patchscopes* | Unifying framework for inspecting hidden representations |
| [65] | **Hernandez et al. 2024**, *Linearity of relation decoding* (LRE) | **The closest methodological precursor.** Uses Jacobians to derive per-relation linear maps subject→object. J-lens applies the same first-order approximation, but to the map from activations to *model outputs*. |
| [54] | Golden 2025 | Equivalent linear mappings of LLMs |
| [151][146][85][8] | Diffusion lens, diffusion steering lens, LatentLens, TensorLens | The 2024–26 lens proliferation |

The whole family is "read the residual stream in vocabulary coordinates." J-lens's novelty is the
*averaged Jacobian over future positions*, which is what makes it approximately causal rather than
correlational.

---

## B. The "concept as direction" lineage — the *conceptual* parent

This is the tradition the user correctly identified as older than the J-space name.

**Probing and the linear representation hypothesis**

| ref | work |
|---|---|
| [1] | **Alain & Bengio 2016**, *Understanding intermediate layers using linear classifier probes* — oldest ML entry in the whole bibliography |
| [66][67] | Hewitt & Liang 2019, control tasks; Hewitt & Manning 2019, structural probe for syntax |
| [148] | Tenney et al. 2019, *BERT rediscovers the classical NLP pipeline* |
| [99] | Liu et al. 2019, linguistic knowledge and transferability |
| [41] | Elazar et al., amnesic probing |
| [125] | **Park, Choe & Veitch 2023**, *The linear representation hypothesis and the geometry of large language models* — the formal statement |
| [155] | Valeriani et al. 2023, geometry of hidden representations |

**Superposition and dictionary learning**

| ref | work |
|---|---|
| [42] | Elhage et al. 2021, *A mathematical framework for transformer circuits* |
| [43] | Elhage et al. 2022, *Toy models of superposition* |
| [21] | Bricken et al. 2023, *Towards monosemanticity* |
| [33] | Cunningham et al. 2023, *Sparse autoencoders find highly interpretable model directions* |
| [147] | Templeton et al. 2024, *Scaling monosemanticity* (Claude 3 Sonnet) |
| [25][92] | Chanin et al. 2024 feature absorption; Leask et al. 2025 *SAEs do not find canonical units of analysis* |

**Steering vectors — directions used causally**

| ref | work |
|---|---|
| [153] | Turner et al. 2023, *Activation addition* (ActAdd) |
| [171] | Zou et al. 2023, *Representation engineering* |
| [124] | Panickssery et al. 2024, *Contrastive activation addition* |
| [94] | Li et al. 2023, *Inference-time intervention* |
| [6] | **Arditi et al. 2024**, *Refusal in language models is mediated by a single direction* |
| [149] | Tigges et al. 2023, linear representations of sentiment |
| [150][63] | Todd et al. 2024 *Function vectors*; Hendel et al. 2023 *task vectors* |
| [144] | Stolfo et al. 2024, instruction-following via activation steering |
| [109] | **Merullo et al. 2024**, *Language models implement simple word2vec-style vector arithmetic* |

---

## The verified gap

**The pre-2020 concept-direction tradition is essentially absent from this paper.**

Checked by grep over both the independently parsed bibliography (`data/references.json`) and the
full 117-page extracted text (`sources/gurnee-2026-jspace.txt`):

| Absent | Why it would belong |
|---|---|
| **Mikolov et al. 2013** — word2vec / *Linguistic regularities in continuous space word representations* | The origin of `king − man + woman ≈ queen`; the founding demonstration that concepts are directions |
| **Kim et al. 2018 — TCAV** (*Testing with Concept Activation Vectors*) | *The* foundational concept-activation-vector paper. **Built on the same first-order object as J-lens** — see below |
| **Bolukbasi et al. 2016** — *Man is to Computer Programmer as Woman is to Homemaker* | Established that semantic axes (gender) are identifiable, measurable, and editable directions |
| **Bau et al. — Network Dissection** | The vision-side "unit ↔ concept" tradition |
| **Radford et al. 2017** — the sentiment neuron | First famous single-direction-controls-a-concept result in a language model |
| Landauer & Dumais (LSA), Firth, Smolensky | The distributional-semantics prehistory |

`word2vec` occurs **exactly once** in 117 pages — inside the title of Merullo et al. [109]. `TCAV`,
`Mikolov`, `Bolukbasi`, and `concept activation vector` occur **zero** times.

So the pre-2020 lineage enters only by proxy, one hop removed, through a 2024 paper that
re-derives word2vec-style arithmetic inside transformers.

**Read this as a finding about the field, not a defect in the paper.** Anthropic's interpretability
tradition is genealogically self-contained: it descends from Olah-lineage circuits work, the
2020 logit lens, and superposition, and treats the direction-as-concept idea as ambient background
rather than a cited inheritance. For this project that gap is the most interesting thing in the
bibliography — it is precisely the seam the user pointed at, and the citation graph makes it
visible rather than anecdotal.

*Caveat, honestly stated:* absence from one paper's reference list is evidence about that paper's
framing, not proof the connection is unrecognized in the literature. The forward cone (who cites
J-space, and whether anyone bridges it back to TCAV) is not yet collected — see
[04 — Open threads](04-open-threads.md).

### TCAV and J-lens are the same first-order object, used in opposite directions

This is the sharpest thing in the project so far, and both sides are verified against primary
sources rather than recalled.

**TCAV** (Kim, Wattenberg, Gilmer, Cai, Wexler, Viégas & Sayres, ICML 2018; arXiv 1711.11279,
archived at `sources/kim-2018-tcav.pdf`). Eq. 1, verbatim:

```
S_C,k,l(x)  =  lim_{ε→0} [ h_l,k(f_l(x) + ε·v_C^l) − h_l,k(f_l(x)) ] / ε
            =  ∇h_l,k(f_l(x)) · v_C^l
```

where `f_l(x)` is the layer-l activation, `h_l,k : R^m → R` maps it to the logit for class k, and
`v_C^l` is a unit **CAV** — a concept direction obtained by training a linear classifier to
separate activations of concept examples from others, then taking the normal to that boundary.

**J-lens**, again:

```
J_ℓ = E_{t, t'≥t, prompt}[ ∂h_final,t' / ∂h_ℓ,t ]      →  J-lens vectors = rows of  W_U J_ℓ
```

Both are the gradient of an output logit with respect to an intermediate activation. The
difference is which end is the unknown:

| | TCAV (2018) | J-lens (2026) |
|---|---|---|
| Concept direction | **supplied** — learned from labelled examples | **derived** — read off as rows of `W_U J` |
| Output | a scalar sensitivity, per class | a full **token-indexed frame** of directions |
| Vocabulary | one user-chosen concept at a time | all `n_vocab` at once, overcomplete |
| Averaging | over inputs within a class | over **~1000 prompts** *and* **all future positions `t' ≥ t`** |
| Needs labelled data | **yes** | no |

So J-lens is structurally **TCAV inverted and enumerated**: instead of scoring a concept you
already have, take the same Jacobian, compose it with the unembedding, and let its rows *be* the
concept directions — one per token, no supervision.

The genuinely new ingredient is the **`t' ≥ t` expectation**. TCAV differentiates one immediate
output. J-lens differentiates everything the model might say *later*, which is what turns a
sensitivity score into a readout of what the model is *poised to verbalize*. Nanda's commentary
independently confirms this is where the gain lives: single-token-restricted J-lens variants
"only mildly outperform logit lens; the performance gap is explained by allowing future tokens."

Nanda also writes that J-lens is "closer to being a causal method… while most concept direction
finding methods are purely correlational." That is true of *probe*-derived directions, but it is
worth noting that TCAV's directional derivative is not correlational either — it is the same
first-order causal sensitivity. The unsupervised, vocabulary-wide, future-averaged construction is
the advance; the causal framing is inherited, whether or not the lineage is cited.

**Status.** This comparison is my own synthesis from the two primary texts, not a claim either
paper makes.

*Adversarial check run 2026-08-14* — searched specifically to find prior art that would kill it.
Nothing found: no source connects TCAV to J-lens, and the search engine's own summary noted that
its results "don't specifically connect this work to TCAV." **This is weak evidence.** Two
cautions worth keeping attached to it:

1. One of the search tools *itself* drew a similar comparison in its answer text. That is a model
   synthesizing on demand, not a published claim — it is not prior art, and it is not
   corroboration either.
2. Web search is not a literature review. The paper is ~5 weeks old; the XAI/concept-vector
   community is large, and someone may have made this point in a venue search does not surface —
   or may publish it next week.

So: survives a first pass, not established as novel. Do the real check (thread A in
[04 — Open threads](04-open-threads.md)) before leaning on it anywhere public.

---

## C. The consciousness / global-workspace lineage

| ref | work |
|---|---|
| [10] | **Baars 1988**, *A Cognitive Theory of Consciousness* — the origin of GWT |
| [37] | Dehaene, Kerszberg & Changeux 1998, *A neuronal model of a global workspace in effortful cognitive tasks* |
| [36] | **Dehaene & Naccache 2001** — the canonical GNW reference |
| [35] | Dehaene & Changeux 2011, experimental and theoretical approaches to conscious processing |
| [38] | **Dehaene, Lau & Kouider 2017**, *What is consciousness, and could machines have it?* — source of the **C1 (global availability) / C2 (self-monitoring)** criteria the commentary applies |
| [108] | Mashour et al. 2020 — most-cited GNW reference in the paper (6×) |
| [18] | **Block 1995** — access vs phenomenal consciousness; the distinction that lets the paper claim the former and disclaim the latter |
| [22] | **Butlin, Long et al. 2023**, *Consciousness in AI: Insights from the science of consciousness* |

**Workspace ideas already inside ML:**

| ref | work |
|---|---|
| [13] | Bengio 2017, *The consciousness prior* |
| [55] | Goyal et al. 2022, *Coordination among neural modules through a shared global workspace* |
| [156] | VanRullen & Kanai, *Deep learning and the global workspace theory* |
| [154] | Urbina-Rodriguez et al. 2026, *A brain-like synergistic core in LLMs drives behaviour and learning* |

**Competing theories of consciousness, cited to be set aside** (§9.4): IIT 4.0 [2]; higher-order
theories [45][91][131]; attention schema [56][57]; recurrent processing [89][90]; biological
naturalism [137]; Chalmers [23][24]; Searle [136].

**Cognitive-psychology scaffolding:** Miller 1956 [111] and Cowan 2001 [32] on capacity limits;
Baddeley 2003 [11] working memory; Kahneman 2011 [77]; Wegner 1987/1994 [160][161] on thought
suppression (the "don't think about X" experiments); blindsight [163][128]; Jacoby 1991 process
dissociation [70].

---

## D. Anthropic's own immediate precursors

The tightest cluster, and the one that most determines the paper's shape:

| ref | work |
|---|---|
| [98] | Lindsey et al. 2025, *On the biology of a large language model* — most-cited overall (7×) |
| [3] | Ameisen et al. 2025, *Circuit tracing* |
| [97] | **Lindsey 2025**, *Emergent introspective awareness in large language models* |
| [60] | Gurnee et al. 2025, *When models manipulate manifolds: the geometry of a counting task* |
| [140] | **Sofroniew et al. 2026**, *Emotion concepts and their function in a large language model* |
| [20] | Bogdan & Lindsey 2026, *Slot machines: how LLMs keep track of multiple entities* |
| [101] | Lu et al. 2026, *The assistant axis: situating and stabilizing the default persona* |
| [106] | Marks et al. 2025, *Auditing language models for hidden objectives* |
| [104] | MacDiarmid et al. 2025, *Natural emergent misalignment from reward hacking in production RL* |
| [103] | Lynch et al. 2025, *Agentic misalignment* |

> **Direct tie to existing work on this machine:** ref [140], *Emotion concepts and their function
> in a large language model*, is the Anthropic emotion-vectors paper that `D:\face` reproduces —
> and **Nicholas Sofroniew is co-first-author of the J-space paper**. The emotion-axis work and
> J-space are the same group, one year apart. `D:\face`'s residual-stream probing rig is already
> most of a J-lens implementation; the missing piece is the averaged Jacobian, and Nanda reports
> n=25 prompts is enough. Also note [101] *The assistant axis* — another literal "axis" paper from
> the same lab.
