# 03 — Reception

Anthropic solicited and published three independent commentaries alongside the paper
(`sources/anthropic-external-commentary.pdf`, 53 pp). That is unusual and worth noting as a fact
about the release: the critique was commissioned, not spontaneous.

---

## 1. Stanislas Dehaene & Lionel Naccache — *"Does Claude possess a conscious global workspace?"*

Collège de France / NeuroSpin, and Sorbonne / Paris Brain Institute. With Changeux, **these are the
people who built the GNW model the paper is testing.** Standalone copy:
[unicog.org](https://unicog.org/wp_2025/wp-content/uploads/2026/07/Dehaene-and-Naccache-Workspace-commentary-on-Gurnee-Lindsey-June-2026.pdf),
archived at `sources/dehaene-naccache-commentary.pdf`.

**Process disclosure, in their own note:** the commentary is based on several rounds of
interaction with Jack Lindsey in late May / early June 2026, *during which the Anthropic report was
still evolving, partly in response to their queries.* They mark post-first-draft material in italic.
This is not arm's-length peer review, and they say so.

**Verdict:** "a landmark in consciousness research, because it provides a mechanistic, testable
version of the GNW hypothesis."

**On their own C1/C2 criteria** (Dehaene, Lau & Kouider 2017):
- **C1, global availability — met.** Their framing: the authors "went looking for reportable
  representations and found that those same representations turn out to be globally available to
  the rest of the network during flexible reasoning." That the criterion used to *find* J-space
  (reportability) is not the criterion it then *satisfies* (global availability) is what makes the
  result non-circular, and they treat this as the paper's central achievement.
- **C2, self-monitoring** — discussed, less firmly established.

**What they find most striking:**
- The concept-swap experiment is "an experiment that remains a dream for neuroscientists"
- Selectivity: swapping Spanish→French breaks high-level inference (language report, "hola",
  "peseta") while the model **keeps writing in Spanish** — automatic processing untouched
- Task-dependent entry of character counts into J-space: "a neat demonstration of the same
  information passing from an automatic to an accessible regime on demand"

**Their caution — the dissociation problem.** Human introspection is real but limited, and reliably
confabulates: choice blindness (Johansson et al. 2005), split-brain interpretation (Gazzaniga
1998), visual illusions affecting perception but not motor action (Aglioti et al. 1995), Ericsson
& Simon 1993 on verbal protocols. They point out that **the same group already showed this for
LLMs** — Lindsey et al. 2025 found that what a model says about how it adds has little to do with
how it actually computes the sum. J-space may inherit exactly this dissociation, and it is
"not yet sufficiently documented."

**Where they say the analogy breaks** (§ their conclusion): anatomy; sense of self; **no body**;
**no enduring episodic memory**. They also flag that in brains, broadcast is implemented by
recurrent loops and long-range axons — the paper itself concedes implementation is where the
analogy is weakest.

**Proposed further experiments,** drawn from the GNW empirical playbook — these are concrete and
are the most actionable output of the commentary: ignition (late, nonlinear, self-amplifying
bifurcation at ~250 ms with bimodal at-threshold responses, cf. Sergent et al. 2021), limited
capacity / bottleneck effects (attentional blink, psychological refractory period, inattentional
blindness), and masking.

---

## 2. Patrick Butlin, Derek Shiller, Dillon Plunkett & Robert Long

*"Consciousness and cognitive access in LLMs"*, Eleos AI Research (Shiller incoming; currently
Rethink Priorities). Butlin and Long co-led *Consciousness in Artificial Intelligence: Insights
from the Science of Consciousness* (2023) — ref [22], the indicator-properties survey the paper
leans on. Their angle is consciousness and **moral status**.

**Verdict:** "the most significant evidence of consciousness in LLMs so far uncovered by
mechanistic interpretability research" — and explicitly the kind of work they called for in 2023:
testing internal mechanisms against conditions from scientific theories of consciousness.

**Their central contribution — a three-rung claim ladder**, each rung strictly stronger:

1. **Privileged set** — certain representations display the characteristics of cognitive accessibility
2. **Privileged stream** — those representations form a *unified* stream (a set with "an appropriate
   source of cohesion", e.g. shared mechanisms they all interact with)
3. **GWT workspace** — that stream has the structure GWT actually specifies

Their assessment: the paper gives **strong evidence for rung 1**, but "more evidence is needed to
conclusively establish the existence of a workspace-like structure. It could be that the
privileged, cognitively accessible representations in LLMs **do not form a unified stream.**"
They do not object to the "global workspace" label — they just want the rungs kept apart.

**The GWT conditions** they check against (modified from Butlin, Long et al. 2023):

| condition | status |
|---|---|
| **Modules** — multiple specialised parallel subsystems | not emphasised in the paper |
| **Bottleneck** — limited-capacity workspace + selective attention | supported (tens of concepts) |
| **Global broadcast** — *the same* information sent to *all* modules | not established |
| **Selection** — entry depends on current workspace state, letting the workspace orchestrate modules | not established |

They note the two unmet conditions — integrating modular subsystems, and broadcasting identical
information to each — "may not hold even in the human case… uncertain, contested, and likely
idealized," and they agree with the authors that some GWT architecture may be idiosyncratic to
humans. Their point is bookkeeping, not objection.

**J-space vs W-space.** They introduce a hypothetical **W-space** — the real workspace that J-space
may only approximate. This is the *same move Nanda makes* with "the cognitive space", arrived at
independently, from philosophy rather than from interpretability. Two of the three commentaries
converging on "the measured thing is not the posited thing" is the strongest signal in the
reception, and the distinction should be treated as standard vocabulary from here on.

**On phenomenal consciousness.** They separate it sharply, via Block 1995 (ref [18]): access
consciousness is functional and widely agreed to be possible in AI in principle; phenomenal
consciousness is "what it is like", the subject of the hard problem, and far more contested. Their
position: to the extent the paper demonstrates a global workspace, it is evidence of **access
consciousness**; they "remain highly uncertain about phenomenal consciousness in LLMs", which are
"very different from humans in many ways that could plausibly matter."

They flag the live dispute honestly: Block 2007 and Lamme 2010 argue phenomenal experience can
outrun access; Mudrik et al. 2025 collects the disagreement; Dennett 2001 and — notably —
**Naccache 2018** hold that access consciousness is all there is, which would make the separate
question ill-posed. (Worth registering that Naccache co-wrote commentary #1.)

**On moral status:** a workspace-like mechanism could matter either as a *ground* of phenomenal
consciousness, or via a distinct route in which conscious access is **itself** morally significant.
They treat the result as welfare-relevant and as adding "urgency to further investigation."

---

## 3. Neel Nanda — with an independent replication

Leads LM interpretability at Google DeepMind. The most technically load-bearing commentary.

**He decomposes the paper into four claims and grades them separately:**

| claim | verdict |
|---|---|
| **Scientific** — a "cognitive space" exists inside the model storing intermediate variables during a forward pass | **Persuaded.** "An overwhelming amount of evidence… hard-to-fake." Notes he already suspected it. |
| **Methodological** — logit lens and J-lens both find it, J-lens is better | **Persuaded**, but considers it the less interesting claim |
| **Pragmatic** — J-lens is practically useful, e.g. for alignment audits | **Somewhat persuaded.** Wants to use it for auditing Gemini. Expects a *hypothesis-generation* tool with many false positives — "but basically no existing interpretability technique meets this bar" |
| **Philosophical** — this is analogous to a global workspace | **Declines to judge.** "The least interesting claim to me." Says the paper did not move him on moral significance or consciousness |

**Terminology correction worth adopting:** he separates *the cognitive space* (what the model
actually uses) from *J-space* (the span of sparse combinations of `J W_U` vectors). J-space is
**hoped to approximate** the cognitive space and is not the same thing. The paper's own framing
blurs these; keeping them distinct is cleaner.

**His first-principles argument for why it must exist** — worth preserving because it is the
cleanest statement of the direction-as-concept logic anywhere in the corpus:
1. LMs demonstrably do multi-step reasoning in a single forward pass (2–3 hop arithmetic)
2. Therefore intermediate values must be represented somewhere
3. The residual stream is the bottleneck between layers, so they live there
4. **"By the linear representation hypothesis, these should be represented as directions"**
5. If a concept is produced and read by many circuits, a *consistent* direction per layer is the
   efficient encoding — "in the same way that good code is modularised with clear APIs"

**Why Jacobian beats regression** (his clearest technical contribution): linear regression asks
"given the model is thinking about basketball, what will it think about at the final layer?" — which
drags in downstream-correlated concepts. The Jacobian asks "if the model thought about this concept
an **infinitesimal** amount more, what would it be more likely to say?" Infinitesimal means
nonlinearities cannot engage, so no further processing occurs: it reports the current contents
rather than their consequences. This is why J-lens is **closer to causal**, where "most concept
direction finding methods are purely correlational."

**Limitations he raises:**
- **Single-token bottleneck.** Concepts without a single-token name are invisible. He thinks a
  1:1 concept↔token correspondence is "highly unlikely" (e.g. digit-wise tokenization vs. a
  "twenty-two" concept). Wants multi-token extensions.
- **Noise.** The "average Jacobian on pretraining data" method is crude; expect false positives and
  misses. **Error is worse for causal intervention than observation** — ablation removes only part
  of a concept, tempting over-steering, which then steers along the error term.
- **Nothing canonical.** SAEs and probes also access this space. J-lens's edge is that it
  prioritizes *verbalizable* representations, which likely correlates with importance better than
  SAE sparsity does.
- **Variable, not algorithm, interpretability.** J-lens finds the features, not the circuits.
- Not convinced of the fine-grained property claims in §4; suspects some have alternative
  explanations or won't generalize across models.
- Multilingual results possibly confounded: English unembeddings may simply be higher-norm →
  higher-variance logits → favored by top-k. He judges this not cruxy.

### The replication — Qwen 3.6 27B

| result | outcome |
|---|---|
| Multilingual (probing **and** causal) | **replicated** |
| Typo | **replicated** |
| Association | replicated in substance (weak scores blamed on a single-correct-answer dataset) |
| Multi-hop factual recall | **did not hold** — swapping the *answer* strictly dominated. Diagnosis: the dataset of facts Qwen could do wasn't hard enough; pairs like France/Paris are linearly related, exactly the confound the original paper had to rule out |
| Poetry | **failed** — "plausibly experimenter error or worse model capabilities" |
| Arithmetic | **failed** — same caveat |

**Cost.** Cheap. The paper averages over n=1000 prompts, but its own ablations show n=10 is nearly
as good and n=1 respectable; cost is `O(n · d_model)` backward passes. He used **n=25**. Scaling
test on Qwen3.5-397B-A17B with n=4 took **~1 hour on 8×H200**. "A coding agent given the paper did
it pretty well, though we recommend sanity checking."

### New finding: interpretative meta-tokens

Because Qwen's tokenizer carries information-dense Chinese tokens, J-lens can name concepts that
are multi-token in English. They found four: 什么意思 (what meaning), 是什么意思 (what does it
mean), 这句话 (this sentence), 是何含义 (what does it mean).

These fire on **ambiguous** input — first noticed on the newline after a line of poetry, where the
unexpected break is the evidence that this is verse; the meta-tokens appear, then "song"/"poem"
shortly after. Adding clarifying text suppresses them and the genre appears earlier. They also
appear on crossword clues, tweets, wordplay, gibberish, and short unclear sentences; rarely in
Wikipedia text. They concentrate on **punctuation and control tokens** (paragraph break in
pretraining text, `\n` in chat) — consistent with the summarization-token hypothesis, that models
use punctuation to summarize a span and hand more abstract information forward.

Negative steering on them measurably reduces the model's ability to recognize context: a pun
prompt ("A boiled egg every morning is hard to beat") flips from "That's a classic pun!" to a
straight nutrition answer. Steering at any *single* position did not work; ablation was largely
ineffective; steering coefficients were swept to the largest coherent value.

He flags this as **J-lens doing algorithm interpretability, not just variable interpretability**:
the model detected ambiguity, ran a disambiguation subroutine, and J-lens both showed it and
perturbed it. Explicitly preliminary — meta-tokens may indicate confusion rather than intent to
disambiguate, and steering can always just break a model.

---

## 4. Press and secondary coverage

Useful for tracking uptake; **not** citable for technical claims. Several already propagate the
unverified "59% flip" and "6–7% variance" numbers (see [01](01-primary-source.md)).

- MIT Technology Review — ["Anthropic found a hidden space where Claude puzzles over concepts"](https://www.technologyreview.com/2026/07/09/1140293/anthropic-found-a-hidden-space-where-claude-puzzles-over-concepts/) (2026-07-09)
- VentureBeat — ["Anthropic's new J-lens reveals a silent workspace inside Claude"](https://venturebeat.com/technology/anthropics-new-j-lens-reveals-a-silent-workspace-inside-claude-that-mirrors-a-leading-theory-of-consciousness)
- Forbes (John Werner) — ["Anthropic Illuminates LLM J-Space With J-Lens"](https://www.forbes.com/sites/johnwerner/2026/07/12/anthropic-illuminates-llm-j-space-with-j-lens/) (2026-07-12)
- IBM Think — [what J-space means for the future of AI](https://www.ibm.com/think/news/what-anthropic-j-space-research-means-future-ai)
- LessWrong — ["Anthropic's J-Lens: A Research Engineer's Analysis"](https://www.greaterwrong.com/posts/vHxGD5HKsFuBStirq/anthropic-s-j-lens-a-research-engineer-s-analysis) *(not yet read)*
- Neuronpedia — [Welcome to the J-Space](https://www.neuronpedia.org/blog/jacobian-lens) *(not yet read; technical, open-weights)*
- theconsciousness.ai, unfinishablemap.org, snehal.ai — independent explainers *(not yet assessed)*
- 【DL輪読会】 Japanese reading-group deck, 2026-07-17
