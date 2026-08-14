"""Emit graph/index.html -- a self-contained citation-graph explorer.

Data is inlined rather than fetched because the viewer is meant to open from
file:// and fetch() is blocked there. Payload is trimmed accordingly: full
metadata for every node, every edge, all 263 citation contexts from the seed
paper, and a capped sample of contexts from the rest of the crawl.

Run:  python build_viewer.py
"""
import json
import pathlib
import re
import urllib.parse

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
# Repo root, so GitHub Pages serving from "/" lands straight on the graph.
OUT = ROOT / "index.html"
SEED = "arXiv:2607.15495"
CTX_CAP = 1600           # non-seed contexts to inline
CTX_TRIM = 260           # chars per non-seed context

graph = json.loads((DATA / "graph.json").read_text(encoding="utf-8"))
contexts = json.loads((DATA / "cite_contexts.json").read_text(encoding="utf-8"))
refs = json.loads((DATA / "references.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------- link resolution
# The arXiv crawl only ever yields arxiv.org links. The J-space paper's own
# bibliography also carries transformer-circuits, ACL, NeurIPS and Anthropic
# URLs, so fold those in by arXiv id and then by title.
def norm_title(t):
    t = re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()
    return t if len(t) > 14 else None


def valid(u):
    # The PDF parser truncated some URLs at a line wrap ("https://" alone).
    return bool(u) and bool(re.match(r"https?://[^\s/]+\.[^\s/]+", u))


url_by_arxiv, url_by_title = {}, {}
for r in refs:
    # Re-extract from the raw entry. The bibliography wraps lines at arbitrary
    # points inside a URL ("https: //www.anthropic.com", "https://www. lesswrong
    # .com"), which defeats a \S+ match. In this format the URL is always the
    # last thing in the entry, so take everything from "http" and drop the
    # whitespace the wrapping introduced.
    raw = r.get("raw") or ""
    i = raw.find("http")
    u = re.sub(r"\s+", "", raw[i:]).rstrip(".") if i >= 0 else r.get("url")
    if not valid(u):
        continue
    u = u.rstrip(".,;")
    if r.get("arxiv"):
        url_by_arxiv.setdefault(r["arxiv"], u)
    nt = norm_title(r.get("title"))
    if nt:
        url_by_title.setdefault(nt, u)


def link_for(n):
    """(url, label) for a node -- the paper itself where known, else a search."""
    if n.get("arxiv"):
        return f"https://arxiv.org/abs/{n['arxiv']}", "arxiv.org"
    nt = norm_title(n.get("title"))
    u = url_by_title.get(nt) if nt else None
    if u:
        host = re.sub(r"^www\.", "", re.match(r"https?://([^/]+)", u).group(1))
        return u, host
    if n.get("title"):
        q = urllib.parse.quote_plus(n["title"][:180])
        return f"https://scholar.google.com/scholar?q={q}", "search"
    return None, None

# --------------------------------------------------------------- clustering
# Lineage buckets, from notes/02-lineage.md. Order matters: a paper is filed by
# what it is *about* before what lab wrote it, so "Scaling monosemanticity"
# lands in `direction` rather than `anthropic`.
CLUSTERS = [
    ("lens", r"logit lens|tuned lens|future lens|backward lens|patchscope|diffusion lens|"
             r"latentlens|tensorlens|jump to conclusions|embedding space|vocabulary space|"
             r"linearity of relation|equivalent linear mapping|promoting concepts|"
             r"contrasting layers|autocontrastive|self-interpretation|selfie|latentqa|"
             r"activation explainer|activation oracle|natural language autoencoder|"
             r"explain neurons|interpreting millions of features"),
    ("multilingual", r"multilingual|multilinguality|latent language|romanization|"
                     r"think in english|english-centric|what language"),
    ("circuits", r"circuit|attribution patching|activation patching|patching|atp|"
                 r"factual recall|factual associations|indirect object|greater-than|"
                 r"knowledge overshadowing|self-repair|hydra|localiz|"
                 r"linear computation graph|saliency|visualising image classification|"
                 r"mech interp team|feature interactions|stages of inference|"
                 r"layer-wise information|information trajector"),
    ("reasoning", r"chain-of-thought|\bcot\b|scratchpad|deliberative alignment|"
                  r"encoded reasoning|multi-hop reasoning|intermediate computation|"
                  r"reasoning enables|latently perform"),
    ("gwt", r"conscious|workspace|neuronal|blindsight|working memory|attention schema|"
            r"higher-order|integrated information|phenomenal|introspect|metacognit|"
            r"awareness|thought suppression|magical number|capacity limits|psychedelic|"
            r"selflessness|sensorimotor|ego dissolution|process dissociation|"
            r"cognitive unconscious|rediscovery of the mind|thinking, fast|"
            r"biological naturalism|information integration|astrocyte|consciousness prior|"
            r"know what they know|aware of their learned|internal attention|"
            r"mental control|mental operations|describe complex internal|"
            r"recognize and react|associative memory|fast weight|"
            r"recurrent processing|modes of vision|synergistic core|brain-like"),
    ("direction", r"prob(e|es|ing)|linear representation|superposition|monosemantic|"
                  r"sparse autoencoder|dictionary learning|steering|activation addition|"
                  r"representation engineering|refusal|function vector|task vector|"
                  r"inference-time intervention|transcoder|word2vec|"
                  r"geometry of hidden|sentiment|universal neuron|canonical units|"
                  r"absorption|neuron basis|concept|manifold|residual stream|"
                  r"hidden representation|vector arithmetic|direction|"
                  r"network representations|contextual representations|"
                  r"rediscovers the classical|"
                  r"vision-language representations|middle layers|intermediate hidden"),
    ("anthropic", r"circuit tracing|biology of a large language model|claude|"
                  r"attribution graph|assistant axis|slot machines|hidden objectives|"
                  r"reward hacking|agentic misalignment|emotion concepts"),
    ("infra", r"attention is all you need|llama|gpt-4|gpt-2|few-shot learners|"
              r"unsupervised multitask|mistral|gemma|qwen|the pile|adam:|"
              r"layer normalization|lora|squad|triviaqa|massive multitask|"
              r"learning to summarize|acceptability judgments|system card|"
              r"technical report|verifiers to solve math|mining reddit|"
              r"comprehension dataset|human feedback"),
]
COMPILED = [(name, re.compile(pat, re.I)) for name, pat in CLUSTERS]

ANTHROPIC_AUTHORS = re.compile(
    r"lindsey|gurnee|ameisen|batson|templeton|bricken|olah|sofroniew|bogdan|"
    r"kantamneni|pearce|anthropic|elhage|cunningham|olsson", re.I)


def cluster_of(node):
    hay = f"{node.get('title') or ''}"
    for name, rx in COMPILED:
        if rx.search(hay):
            return name
    if ANTHROPIC_AUTHORS.search(node.get("authors") or ""):
        return "anthropic"
    return "other"


nodes = []
for n in graph["nodes"]:
    rec = {
        "i": n["id"],
        "t": n.get("title") or n["id"],
        "a": (n.get("authors") or "")[:70],
        # NOT "y": the force layout writes x/y coordinates onto these records and
        # would silently overwrite the year.
        "yr": n.get("year"),
        "d": n.get("depth", 9),
        "g": n.get("in_degree", 0),
        "s": 1 if n.get("seed_ref") else 0,
        "c": cluster_of(n),
    }
    if n.get("arxiv"):
        # NOT "x": same trap as the year -- the layout writes x/y onto these.
        rec["ax"] = n["arxiv"]
    u, host = link_for(n)
    if u:
        rec["u"], rec["uh"] = u, host
    if n["id"] == SEED:
        rec["c"] = "seed"
        rec["s"] = 1
        rec["yr"] = 2026        # stripped as an identifier by the year scan
    nodes.append(rec)

# The viewer spreads each node record into its simulation object, so any payload
# key sharing a name with a layout field gets silently overwritten by a
# coordinate. This bit `year`->y and `arxiv`->x already; fail loudly instead.
LAYOUT_FIELDS = {"x", "y", "vx", "vy", "r", "tx", "ty"}
clash = LAYOUT_FIELDS & {k for n in nodes for k in n}
if clash:
    raise SystemExit(f"payload key(s) {sorted(clash)} collide with layout fields "
                     f"{sorted(LAYOUT_FIELDS)} and would be overwritten -- rename them")

edges = [{"f": e["from"], "t": e["to"], "n": e.get("n_cites", 0),
          "s": e.get("sections", [])} for e in graph["edges"]]

# --------------------------------------------------------------- contexts
seed_ctx, other_ctx = [], []
for c in contexts:
    rec = {"f": c["from"], "t": c["to"], "s": c.get("section"),
           "c": re.sub(r"\s+", " ", c.get("context") or "").strip()}
    if not rec["c"]:
        continue
    if c["from"] == SEED:
        seed_ctx.append(rec)
    elif len(other_ctx) < CTX_CAP:
        rec["c"] = rec["c"][:CTX_TRIM]
        other_ctx.append(rec)

all_ctx = seed_ctx + other_ctx

sections = sorted({c["s"] for c in seed_ctx if c["s"]})

payload = {"seed": SEED, "nodes": nodes, "edges": edges,
           "ctx": all_ctx, "sections": sections}
blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
blob = blob.replace("</", "<\\/")     # keep a stray </script> out of the tag

HTML = r"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>J-space Citation Graph</title>
<style>
:root{
  --bg:#f6f6f4; --panel:#fffffe; --ink:#1a1a19; --dim:#6b6b66; --line:#dedcd6;
  --seed:#c2410c; --lens:#2563eb; --direction:#059669; --gwt:#7c3aed;
  --anthropic:#d97706; --infra:#94a3b8; --other:#a8a29e;
  --circuits:#db2777; --multilingual:#0891b2; --reasoning:#65a30d;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#14140f; --panel:#1c1c18; --ink:#eceae4; --dim:#9a9891; --line:#2f2f28;
  --seed:#fb923c; --lens:#60a5fa; --direction:#34d399; --gwt:#a78bfa;
  --anthropic:#fbbf24; --infra:#64748b; --other:#78716c;
  --circuits:#f472b6; --multilingual:#22d3ee; --reasoning:#a3e635;
}}
:root[data-theme="dark"]{
  --bg:#14140f; --panel:#1c1c18; --ink:#eceae4; --dim:#9a9891; --line:#2f2f28;
  --seed:#fb923c; --lens:#60a5fa; --direction:#34d399; --gwt:#a78bfa;
  --anthropic:#fbbf24; --infra:#64748b; --other:#78716c;
  --circuits:#f472b6; --multilingual:#22d3ee; --reasoning:#a3e635;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden}
body{background:var(--bg);color:var(--ink);
  font:13px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}
#wrap{display:flex;height:100vh}
#main{flex:1;position:relative;min-width:0}
canvas{display:block;width:100%;height:100%;cursor:grab}
canvas.drag{cursor:grabbing}

#bar{position:absolute;top:0;left:0;right:0;padding:10px 14px;display:flex;
  gap:10px;align-items:center;flex-wrap:wrap;
  background:linear-gradient(var(--bg),transparent);pointer-events:none;z-index:5}
#bar>*{pointer-events:auto}
h1{font-size:14px;margin:0;font-weight:650;letter-spacing:-.01em}
h1 span{color:var(--dim);font-weight:400}
input,select,button{font:inherit;color:var(--ink);background:var(--panel);
  border:1px solid var(--line);border-radius:6px;padding:5px 9px}
input{width:190px}
select{max-width:290px}
button{cursor:pointer}
button:hover{border-color:var(--dim)}
button.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}

#legend{position:absolute;left:14px;bottom:14px;background:var(--panel);
  border:1px solid var(--line);border-radius:8px;padding:9px 11px;z-index:5;
  display:flex;flex-direction:column;gap:5px}
.lg{display:flex;align-items:center;gap:7px;cursor:pointer;user-select:none;
  font-size:12px;opacity:.4}
.lg.on{opacity:1}
.sw{width:10px;height:10px;border-radius:3px;flex:none}
.lg b{font-weight:500}
.lg i{color:var(--dim);font-style:normal;margin-left:auto;padding-left:10px;
  font-variant-numeric:tabular-nums}

#side{width:355px;flex:none;background:var(--panel);border-left:1px solid var(--line);
  overflow-y:auto;padding:16px}
#side h2{font-size:14px;margin:0 0 3px;line-height:1.35}
#side .meta{color:var(--dim);font-size:12px;margin-bottom:12px}
#side a{color:inherit}
.tag{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:99px;
  border:1px solid currentColor;margin:0 5px 5px 0;text-transform:uppercase;
  letter-spacing:.04em}
a.open{display:flex;align-items:center;gap:8px;margin:0 0 12px;padding:8px 11px;
  border:1px solid var(--line);border-radius:7px;text-decoration:none;
  font-weight:550;font-size:12.5px;background:var(--bg)}
a.open:hover{border-color:var(--ink)}
a.open .host{margin-left:auto;color:var(--dim);font-weight:400;font-size:11.5px}
a.open .arr{color:var(--dim);font-size:13px}
.ctx{border-left:2px solid var(--line);padding:0 0 0 11px;margin:0 0 13px}
.ctx .sec{font-size:11px;color:var(--dim);margin-bottom:3px;font-weight:500}
.ctx p{margin:0;font-size:12.5px;line-height:1.55}
.hint{color:var(--dim);font-size:12.5px}
hr{border:0;border-top:1px solid var(--line);margin:15px 0}
.k{display:flex;justify-content:space-between;font-size:12px;padding:2px 0}
.k span:last-child{color:var(--dim);font-variant-numeric:tabular-nums}
</style>

<div id="wrap">
  <div id="main">
    <div id="bar">
      <h1>J-space <span id="stat"></span></h1>
      <input id="q" placeholder="search title / author…">
      <select id="sec"><option value="">every section of the J-space paper</option></select>
      <button id="mode">provenance view</button>
      <button id="expand">+ depth 2</button>
      <button id="reset">reset view</button>
    </div>
    <canvas id="cv"></canvas>
    <div id="legend"></div>
  </div>
  <div id="side"><p class="hint">Click a node.<br><br>
    Nodes are sized by how many papers in this crawl cite them, and coloured by
    lineage. The orange node is the J-space paper itself.<br><br>
    Selecting a paper the J-space paper cites shows <b>the actual sentences it was
    cited in</b>, and which section they came from.</p></div>
</div>

<script id="d" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('d').textContent);
const CL = ['seed','lens','direction','circuits','reasoning','multilingual',
            'gwt','anthropic','infra','other'];
const LABEL = {seed:'J-space paper',lens:'vocabulary-space lenses',
  direction:'concepts as directions',circuits:'circuits & patching',
  reasoning:'chain-of-thought / latent reasoning',multilingual:'latent language',
  gwt:'consciousness, cognition & memory',anthropic:'Anthropic precursors',
  infra:'models, data, infra',other:'other'};

const byId = new Map(D.nodes.map(n=>[n.i,n]));
const css = getComputedStyle(document.documentElement);
const col = c => css.getPropertyValue('--'+c).trim() || '#888';

// ---- state
let on = new Set(CL), depth2 = false, query = '', section = '', sel = null;
let mode = 'force';                      // 'force' | 'prov'
let provYears = [], provLanes = [], provTop = 0, provLeft = 0;

// ---- ancestry
// An edge f->t means f *cites* t, so t is the older work: following outgoing
// edges walks backwards into a paper's ancestry, incoming edges walk forward
// into its descendants.
let adjOut = new Map(), adjIn = new Map();
function buildAdj(){
  adjOut = new Map(); adjIn = new Map();
  for (const n of N){ adjOut.set(n.i, []); adjIn.set(n.i, []); }
  for (const e of E){
    adjOut.get(N[e.a].i).push(N[e.b].i);
    adjIn.get(N[e.b].i).push(N[e.a].i);
  }
}
function reach(id, map){
  const seen = new Set(), st = [id];
  while (st.length){
    const c = st.pop();
    for (const nb of (map.get(c) || [])) if (!seen.has(nb)){ seen.add(nb); st.push(nb); }
  }
  seen.delete(id);
  return seen;
}
const ancestors   = id => reach(id, adjOut);
const descendants = id => reach(id, adjIn);

// ---- provenance layout: time on x, one lane per lineage, stacked within year
function layoutProv(){
  const COLW = 92, ROWH = 27, LANEPAD = 52, UNDATED = -1.4;
  const years = [...new Set(N.map(n => n.yr).filter(Boolean))].sort((a,b) => a-b);
  const xi = new Map(years.map((y,i) => [y,i]));
  const lanes = CL.filter(c => N.some(n => n.c === c));

  let cursor = 0;
  provLanes = [];
  for (const c of lanes){
    const inLane = N.filter(n => n.c === c)
                    .sort((a,b) => (a.yr||0)-(b.yr||0) || b.g-a.g);
    const col = new Map();
    let rows = 0;
    for (const n of inLane){
      const cx = n.yr ? xi.get(n.yr) : UNDATED;
      const r = col.get(cx) || 0;
      col.set(cx, r+1);
      n.tx = cx * COLW;
      n.ty = cursor + r * ROWH;
      rows = Math.max(rows, r+1);
    }
    provLanes.push({c, y0: cursor, h: rows*ROWH, n: inLane.length});
    cursor += rows*ROWH + LANEPAD;
  }

  const w = Math.max(1, years.length-1) * COLW;
  for (const n of N){ n.tx -= w/2; n.ty -= cursor/2; }
  provYears = years.map((y,i) => ({y, x: i*COLW - w/2}));
  for (const l of provLanes) l.y0 -= cursor/2;
  provTop = -cursor/2;
  provLeft = UNDATED*COLW - w/2;
}
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
let W=0,H=0, cam={x:0,y:0,k:1};

// ---- which nodes are in play
function visibleSet(){
  const keep = new Set();
  for (const n of D.nodes){
    if (!on.has(n.c)) continue;
    if (n.d <= 1 || n.i === D.seed) { keep.add(n.i); continue; }
    if (depth2 && n.g >= 4) keep.add(n.i);      // depth-2 hubs only, else unreadable
  }
  if (section){
    const ok = new Set([D.seed]);
    for (const c of D.ctx) if (c.f === D.seed && c.s === section) ok.add(c.t);
    for (const id of [...keep]) if (!ok.has(id)) keep.delete(id);
  }
  return keep;
}

let N=[], E=[];
function rebuild(){
  const keep = visibleSet();
  const old = new Map(N.map(n=>[n.i,n]));
  N = [...keep].map(id=>{
    const b = byId.get(id), p = old.get(id);
    const seed = id === D.seed;
    return {...b, x: p?p.x : (seed?0:(Math.random()-.5)*900),
                  y: p?p.y : (seed?0:(Math.random()-.5)*900),
                  vx:0, vy:0, r: seed?13:Math.max(3.2, 3.2+Math.sqrt(b.g)*1.6)};
  });
  const idx = new Map(N.map((n,j)=>[n.i,j]));
  E = [];
  for (const e of D.edges){
    const a = idx.get(e.f), b = idx.get(e.t);
    if (a!==undefined && b!==undefined) E.push({a,b,n:e.n});
  }
  buildAdj();
  if (mode === 'prov') layoutProv();
  document.getElementById('stat').textContent =
    `— ${N.length} papers, ${E.length} citations`;
  alpha = .9;
  drawLegend();
}

// ---- force layout
let alpha = 1;
function tick(){
  if (mode === 'prov'){                  // ease toward the computed slots
    for (const n of N){
      if (n === dragging || n.tx === undefined) continue;
      n.x += (n.tx - n.x) * .15;
      n.y += (n.ty - n.y) * .15;
    }
    return;
  }
  if (alpha < .003) return;
  alpha *= .988;
  const k = alpha;
  for (let i=0;i<N.length;i++){
    const a=N[i];
    for (let j=i+1;j<N.length;j++){
      const b=N[j];
      let dx=b.x-a.x, dy=b.y-a.y, d2=dx*dx+dy*dy;
      if (d2<1) d2=1;
      if (d2>360000) continue;
      const f = (a.r*b.r*26)/d2, d=Math.sqrt(d2);
      const fx=f*dx/d, fy=f*dy/d;
      a.vx-=fx; a.vy-=fy; b.vx+=fx; b.vy+=fy;
    }
  }
  for (const e of E){
    const a=N[e.a], b=N[e.b];
    let dx=b.x-a.x, dy=b.y-a.y, d=Math.hypot(dx,dy)||1;
    const rest = 105 + (a.r+b.r);
    const f = (d-rest)*0.010*(1+Math.min(e.n,4)*0.16);
    const fx=f*dx/d, fy=f*dy/d;
    a.vx+=fx; a.vy+=fy; b.vx-=fx; b.vy-=fy;
  }
  for (const n of N){
    if (n.i===D.seed){ n.vx-=n.x*.06; n.vy-=n.y*.06; }
    else { n.vx -= n.x*0.0016; n.vy -= n.y*0.0016; }
    if (n===dragging) continue;
    n.x += n.vx*k; n.y += n.vy*k;
    n.vx*=.82; n.vy*=.82;
  }
}

function drawProvChrome(){
  const step = provYears.length > 26 ? 5 : 1;
  ctx.save();
  // lane bands + names
  ctx.textAlign = 'left';
  ctx.font = `${11.5/cam.k}px ui-sans-serif,sans-serif`;
  for (const l of provLanes){
    ctx.globalAlpha = .05;
    ctx.fillStyle = col(l.c);
    ctx.fillRect(provLeft - 30/cam.k, l.y0 - 13/cam.k,
                 (provYears.length? provYears[provYears.length-1].x - provLeft : 400) + 70/cam.k,
                 l.h + 12/cam.k);
    ctx.globalAlpha = .9;
    ctx.fillText(LABEL[l.c] + `  (${l.n})`, provLeft - 26/cam.k, l.y0 - 19/cam.k);
  }
  // year ruler along the top
  ctx.globalAlpha = .55;
  ctx.fillStyle = col('dim');
  ctx.textAlign = 'center';
  ctx.font = `${11/cam.k}px ui-sans-serif,sans-serif`;
  provYears.forEach((t,i) => {
    if (i % step && i !== provYears.length-1) return;
    ctx.fillText(t.y, t.x, provTop - 40/cam.k);
    ctx.globalAlpha = .12;
    ctx.strokeStyle = col('dim');
    ctx.lineWidth = .6/cam.k;
    ctx.beginPath();
    ctx.moveTo(t.x, provTop - 33/cam.k);
    ctx.lineTo(t.x, -provTop + 10/cam.k);
    ctx.stroke();
    ctx.globalAlpha = .55;
  });
  ctx.restore();
  ctx.globalAlpha = 1;
}

// ---- render
function draw(){
  ctx.setTransform(1,0,0,1,0,0);
  ctx.clearRect(0,0,W,H);
  ctx.translate(W/2+cam.x, H/2+cam.y); ctx.scale(cam.k,cam.k);

  // In provenance mode a selection lights its whole transitive ancestry and
  // descent, not just immediate neighbours -- that is the point of the view.
  let hi = null, anc = null, desc = null;
  if (sel){
    if (mode === 'prov'){
      anc = ancestors(sel.i); desc = descendants(sel.i);
      hi = new Set([sel.i, ...anc, ...desc]);
    } else {
      hi = new Set([sel.i]);
      for (const e of E){
        if (N[e.a].i===sel.i) hi.add(N[e.b].i);
        if (N[e.b].i===sel.i) hi.add(N[e.a].i);
      }
    }
  }

  if (mode === 'prov') drawProvChrome();

  ctx.lineWidth = .7/cam.k;
  for (const e of E){
    const a=N[e.a], b=N[e.b];          // a cites b, so b is the older end
    const lit = hi && (mode==='prov' ? (hi.has(a.i) && hi.has(b.i))
                                     : (a.i===sel.i || b.i===sel.i));
    ctx.strokeStyle = lit ? (mode==='prov' ? col(b.c) : col('ink')) : col('line');
    ctx.globalAlpha = lit ? .8 : (hi ? .1 : (mode==='prov' ? .3 : .5));
    ctx.beginPath();
    if (mode === 'prov'){
      const mx = (b.x + a.x)/2;         // S-curve from ancestor to descendant
      ctx.moveTo(b.x, b.y);
      ctx.bezierCurveTo(mx, b.y, mx, a.y, a.x, a.y);
    } else {
      ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y);
    }
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  const q = query.toLowerCase();
  for (const n of N){
    const match = q && ((n.t||'').toLowerCase().includes(q) || (n.a||'').toLowerCase().includes(q));
    ctx.globalAlpha = hi ? (hi.has(n.i)?1:.2) : (q ? (match?1:.22) : 1);
    ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,7);
    ctx.fillStyle = col(n.c); ctx.fill();
    if (n===sel || match){
      ctx.lineWidth=2/cam.k; ctx.strokeStyle=col('ink'); ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;

  // labels only where they will not pile up
  const lim = cam.k > 1.4 ? 0 : (cam.k > .8 ? 9 : 15);
  ctx.font = `${11/cam.k}px ui-sans-serif,sans-serif`;
  ctx.textAlign='center'; ctx.fillStyle=col('ink');
  for (const n of N){
    const match = q && ((n.t||'').toLowerCase().includes(q) || (n.a||'').toLowerCase().includes(q));
    if (!(n===sel || match || n.i===D.seed || n.g>=lim && lim)) continue;
    const s = (n.a ? n.a.split(/[,&]/)[0] : n.t).slice(0,26) + (n.yr?` ${n.yr}`:'');
    ctx.globalAlpha = .95;
    ctx.fillText(s, n.x, n.y - n.r - 5/cam.k);
  }
  ctx.globalAlpha = 1;
}

function loop(){ tick(); draw(); requestAnimationFrame(loop); }

// ---- side panel
function show(n){
  const s = document.getElementById('side');
  if (!n){ s.innerHTML = '<p class="hint">Click a node.</p>'; return; }
  const cites = D.ctx.filter(c=>c.t===n.i);
  const fromSeed = cites.filter(c=>c.f===D.seed);
  const fromOther = cites.filter(c=>c.f!==D.seed);
  const outDeg = D.edges.filter(e=>e.f===n.i).length;

  let h = `<h2>${esc(n.t)}</h2><div class="meta">${esc(n.a||'')}${n.yr?' · '+n.yr:''}</div>`;
  if (n.u) h += `<a class="open" href="${esc(n.u)}" target="_blank" rel="noopener noreferrer">`
              + `${n.uh==='search'?'search for this paper':'open paper'}`
              + `<span class="host">${esc(n.uh)}</span><span class="arr">&#8599;</span></a>`;
  h += `<span class="tag" style="color:${col(n.c)}">${LABEL[n.c]}</span>`;
  if (n.s && n.i!==D.seed) h += `<span class="tag" style="color:var(--dim)">cited by J-space</span>`;
  h += `<div style="margin-top:10px">
    <div class="k"><span>cited by, in this crawl</span><span>${n.g}</span></div>
    <div class="k"><span>its own references parsed</span><span>${outDeg||'—'}</span></div>`;
  if (adjOut.has(n.i)){
    const a = ancestors(n.i).size, d = descendants(n.i).size;
    h += `<div class="k"><span>ancestry, transitive</span><span>${a}</span></div>
          <div class="k"><span>descendants, transitive</span><span>${d}</span></div>`;
  }
  if (n.ax) h += `<div class="k"><span>arXiv</span><span>${n.ax}</span></div>`;
  h += `</div>`;

  if (fromSeed.length){
    h += `<hr><div class="meta">Cited by the J-space paper in ${fromSeed.length} place${fromSeed.length>1?'s':''}</div>`;
    for (const c of fromSeed)
      h += `<div class="ctx"><div class="sec">${esc(c.s||'—')}</div><p>…${esc(c.c)}…</p></div>`;
  }
  if (fromOther.length){
    h += `<hr><div class="meta">Cited elsewhere in the crawl</div>`;
    for (const c of fromOther.slice(0,6)){
      const f = byId.get(c.f);
      h += `<div class="ctx"><div class="sec">${esc((f&&f.a||c.f).split(',')[0])} — ${esc(c.s||'')}</div><p>…${esc(c.c)}…</p></div>`;
    }
  }
  if (!cites.length) h += `<hr><p class="hint">No citation context captured — this paper was reached as a reference but its citing sentence was not parsed.</p>`;
  s.innerHTML = h;
  s.scrollTop = 0;
}
const esc = t => String(t??'').replace(/[&<>"]/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));

// ---- legend
function drawLegend(){
  const counts = {};
  for (const n of N) counts[n.c] = (counts[n.c]||0)+1;
  document.getElementById('legend').innerHTML = CL.map(c=>
    `<div class="lg ${on.has(c)?'on':''}" data-c="${c}">
       <span class="sw" style="background:${col(c)}"></span>
       <b>${LABEL[c]}</b><i>${counts[c]||0}</i></div>`).join('');
  document.querySelectorAll('.lg').forEach(el=>el.onclick=()=>{
    const c = el.dataset.c;
    on.has(c) ? on.delete(c) : on.add(c);
    sel = null; show(null); rebuild();
  });
}

// ---- interaction
let dragging=null, panning=false, last={x:0,y:0};
const toWorld = (px,py) => ({x:(px-W/2-cam.x)/cam.k, y:(py-H/2-cam.y)/cam.k});
function hit(px,py){
  const p = toWorld(px,py);
  let best=null, bd=Infinity;
  for (const n of N){
    const d = Math.hypot(n.x-p.x, n.y-p.y);
    if (d < n.r+7 && d < bd){ bd=d; best=n; }
  }
  return best;
}
cv.onmousedown = ev => {
  const n = hit(ev.offsetX, ev.offsetY);
  if (n){ dragging=n; sel=n; show(n); }
  else { panning=true; cv.classList.add('drag'); }
  last={x:ev.offsetX,y:ev.offsetY};
};
cv.onmousemove = ev => {
  if (dragging){
    const p = toWorld(ev.offsetX, ev.offsetY);
    dragging.x=p.x; dragging.y=p.y; dragging.vx=0; dragging.vy=0; alpha=Math.max(alpha,.25);
  } else if (panning){
    cam.x += ev.offsetX-last.x; cam.y += ev.offsetY-last.y;
    last={x:ev.offsetX,y:ev.offsetY};
  } else {
    cv.style.cursor = hit(ev.offsetX,ev.offsetY) ? 'pointer' : 'grab';
  }
};
addEventListener('mouseup', ()=>{ dragging=null; panning=false; cv.classList.remove('drag'); });
cv.onwheel = ev => {
  ev.preventDefault();
  const f = ev.deltaY<0 ? 1.12 : 1/1.12;
  const p = toWorld(ev.offsetX, ev.offsetY);
  cam.k = Math.min(4, Math.max(.15, cam.k*f));
  const q = toWorld(ev.offsetX, ev.offsetY);
  cam.x += (q.x-p.x)*cam.k; cam.y += (q.y-p.y)*cam.k;
};

document.getElementById('q').oninput = e => { query = e.target.value.trim(); };
document.getElementById('mode').onclick = e => {
  mode = mode === 'force' ? 'prov' : 'force';
  e.target.classList.toggle('on', mode === 'prov');
  e.target.textContent = mode === 'prov' ? 'force view' : 'provenance view';
  cam = {x:0, y:0, k: mode === 'prov' ? .5 : 1};
  if (mode === 'prov') layoutProv(); else alpha = .9;
  if (sel) show(sel);
};
document.getElementById('expand').onclick = e => {
  depth2 = !depth2; e.target.classList.toggle('on', depth2);
  e.target.textContent = depth2 ? '– depth 2' : '+ depth 2';
  rebuild();
};
document.getElementById('reset').onclick = ()=>{
  cam={x:0,y:0,k: mode==='prov' ? .5 : 1}; sel=null; show(null);
  document.getElementById('q').value=''; query='';
  document.getElementById('sec').value=''; section='';
  depth2 = false;
  const ex = document.getElementById('expand');
  ex.classList.remove('on'); ex.textContent = '+ depth 2';
  on = new Set(CL); rebuild();
};
const sec = document.getElementById('sec');
for (const s of D.sections){
  const o=document.createElement('option'); o.value=s; o.textContent=s.slice(0,60); sec.append(o);
}
sec.onchange = e => { section=e.target.value; sel=null; show(null); rebuild(); };

function resize(){
  const dpr = devicePixelRatio||1, r = cv.getBoundingClientRect();
  if (!r.width || !r.height) return;          // pane hidden; retry when shown
  W=r.width; H=r.height;
  cv.width=W*dpr; cv.height=H*dpr;
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
addEventListener('resize', resize);
// The window 'resize' event does not fire when a hidden pane is revealed, which
// leaves the canvas at zero size. Observe the element itself instead.
new ResizeObserver(()=>{ resize(); alpha=Math.max(alpha,.12); }).observe(cv);
resize(); rebuild(); loop();
</script>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HTML.replace("__DATA__", blob), encoding="utf-8")

kb = OUT.stat().st_size / 1024
print(f"wrote {OUT}  ({kb:,.0f} KB)")
print(f"  nodes {len(nodes)}  edges {len(edges)}")
print(f"  contexts inlined: {len(seed_ctx)} from seed + {len(other_ctx)} others")
print(f"  sections: {len(sections)}")
from collections import Counter
print("  clusters:", dict(Counter(n["c"] for n in nodes).most_common()))
print("  clusters among the 171 seed refs:",
      dict(Counter(n["c"] for n in nodes if n["s"] and n["i"] != SEED).most_common()))
