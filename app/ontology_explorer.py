"""Mythological Ontology Explorer — Streamlit App"""
import json, sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from engine.ontology import MythologicalOntology
from engine.schema import ARCHETYPES, PANTHEON_COLORS

st.set_page_config(page_title="Mythological Ontology", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
:root{
    --app-bg:#f4f6f8;
    --sidebar-bg:#e8edf3;
    --surface:#ffffff;
    --surface-border:#d2d9e3;
    --text-on-bg:#111111;
    --text-muted:#4a5568;
    --text-on-surface:#111111;
    --accent:#2458a6;
    --title-start:#111111;
    --title-mid:#2a2a2a;
    --title-end:#111111;
    --brand-bg:#ffffff;
    --brand-text:#000000;
}
html,[class*="css"]{font-family:'Crimson Text',serif;color:var(--text-on-bg)}
[data-testid="stAppViewContainer"]{background:var(--app-bg)}
.main-title{font-family:'Cinzel',serif;font-size:2.6rem;font-weight:700;letter-spacing:.05em;
    background:linear-gradient(135deg,var(--title-start) 0%,var(--title-mid) 45%,var(--title-end) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1}
.subtitle{font-family:'Crimson Text',serif;font-style:italic;font-size:1.1rem;color:var(--text-muted);margin-top:.2rem;letter-spacing:.02em}
.metric-box{background:var(--surface);border:1px solid var(--surface-border);border-radius:10px;padding:1rem;text-align:center}
.metric-val{font-family:'Cinzel',serif;font-size:2.1rem;font-weight:700;color:var(--text-on-surface);line-height:1}
.metric-lbl{font-size:.78rem;color:var(--text-on-surface);text-transform:uppercase;letter-spacing:.1em;margin-top:.3rem}
.tag{display:inline-block;background:var(--surface);border:1px solid var(--surface-border);border-radius:20px;padding:1px 10px;font-size:.78rem;color:var(--text-on-surface);margin:2px}
.entity-card{background:var(--surface);border:1px solid var(--surface-border);border-radius:10px;padding:1rem 1.2rem;margin-bottom:.6rem;min-height:260px}
.entity-name{font-family:'Cinzel',serif;font-size:1rem;font-weight:600;color:var(--text-on-surface);margin-bottom:.2rem}
.entity-type{font-size:.75rem;color:var(--text-on-surface);text-transform:uppercase;letter-spacing:.08em}
.entity-desc{font-size:.86rem;color:var(--text-on-surface);font-style:italic;margin-top:.4rem;line-height:1.6}
.rel-row{display:flex;align-items:center;gap:.5rem;padding:.35rem 0;border-bottom:1px solid var(--surface-border);font-size:.9rem}
.rel-type{color:var(--text-on-surface);font-style:italic;font-size:.82rem}
.rel-target{color:var(--text-on-surface)}
.path-step{display:inline-block;background:var(--surface);border:1px solid var(--surface-border);border-radius:6px;padding:2px 10px;color:var(--text-on-surface);font-family:'Cinzel',serif;font-size:.82rem;margin:2px}
div[data-testid="stSidebar"]{background:var(--sidebar-bg);border-right:1px solid #222222}
.sidebar-brand{font-family:'Cinzel',serif;font-size:1.3rem;font-weight:700;color:var(--brand-text);background:var(--brand-bg);text-align:center;padding:.5rem 0 1rem;letter-spacing:.08em;border-radius:8px}
span[style*="color:#5a4a2a"],span[style*="color:#7a6a4a"],span[style*="color:#9a8a6a"],span[style*="color:#b0a080"],div[style*="color:#5a4a2a"],div[style*="color:#7a6a4a"],div[style*="color:#9a8a6a"],div[style*="color:#b0a080"]{color:var(--text-on-bg)!important}
div[style*="background:rgba(20,16,10"],div[style*="background:linear-gradient(135deg,rgba(20,16,10"],div[style*="background:rgba(10,8,6"]{background:var(--surface)!important;border-color:var(--surface-border)!important;color:var(--text-on-surface)!important}
div[style*="background:rgba(20,16,10"] span,div[style*="background:linear-gradient(135deg,rgba(20,16,10"] span,div[style*="background:rgba(10,8,6"] span{color:var(--text-on-surface)!important}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_onto():
    onto = MythologicalOntology()
    p = ROOT/"knowledge_graph"/"mythology_graph.json"
    if p.exists(): onto.load(str(p))
    return onto

@st.cache_data
def load_entities():
    p = ROOT/"data"/"entities"/"all_entities.json"
    if p.exists():
        with open(p, encoding="utf-8") as f: return json.load(f)
    from engine.scraper import SEED_ENTITIES
    from engine.archetype_mapper import ArchetypeMapper
    ents = list(SEED_ENTITIES)
    ArchetypeMapper().enrich_entities(ents)
    return ents

onto    = load_onto()
entities = load_entities()

# Bootstrap graph from entities if empty
if onto.graph.number_of_nodes() == 0 and entities:
    from engine.archetype_mapper import ArchetypeMapper
    from engine.relation_extractor import RelationExtractor, CURATED_RELATIONS
    ArchetypeMapper().enrich_entities(entities)
    for e in entities: onto.add_entity(e)
    ex = RelationExtractor(); ex.extracted = list(CURATED_RELATIONS)
    onto.add_relations_bulk(ex.to_records())

entity_names = sorted(e["name"] for e in entities)
stats = onto.stats()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">MYTHICA</div>', unsafe_allow_html=True)
    st.markdown("---")
    theme_mode = "Light"
    mode = st.radio("Navigate", ["Overview","Entity Explorer","Archetypes","Graph Visualizer","Path Finder","Analysis"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f'<div style="font-family:\'Crimson Text\',serif;font-size:.82rem;color:var(--text-on-bg);line-height:2">Entities: <span style="color:var(--text-on-bg)">{stats["nodes"]}</span><br>Relations: <span style="color:var(--text-on-bg)">{stats["edges"]}</span><br>Density: <span style="color:var(--text-on-bg)">{stats["density"]}</span><br>Avg Degree: <span style="color:var(--text-on-bg)">{stats["avg_degree"]}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="main-title">Mythological Ontology</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A Jungian Knowledge Graph of World Mythology</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ══ OVERVIEW ══════════════════════════════════════════════════════════════════
if mode == "Overview":
    c1,c2,c3,c4 = st.columns(4)
    for col,lbl,val in [(c1,"Entities",stats["nodes"]),(c2,"Relations",stats["edges"]),
                        (c3,"Archetypes",len(ARCHETYPES)),(c4,"Pantheons",len(set(e.get("pantheon","?") for e in entities)))]:
        with col:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Most Connected Entities")
        for name, score in onto.top_nodes(10):
            node = onto.entity_node(name)
            pa = (node or {}).get("primary_archetype","")
            ai = ARCHETYPES.get(pa,{}); color=ai.get("color","#95A5A6")
            bw = int(score*200)
            st.markdown(f'<div style="display:flex;align-items:center;gap:.6rem;padding:.3rem 0;border-bottom:1px solid rgba(201,169,110,.08)"><span style="font-family:\'Cinzel\',serif;font-size:.88rem;color:#c9a96e;min-width:130px">{name}</span><div style="height:6px;width:{bw}px;background:{color};border-radius:3px;opacity:.7"></div><span style="font-size:.72rem;color:#5a4a2a">{score:.3f}</span></div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("#### Archetype Distribution")
        dist = {}
        for e in entities:
            for a in e.get("archetypes",[]): dist[a]=dist.get(a,0)+1
        total = max(sum(dist.values()),1)
        for arch, count in sorted(dist.items(),key=lambda x:x[1],reverse=True):
            if not count: continue
            ai = ARCHETYPES.get(arch,{}); color=ai.get("color","#95A5A6")
            bw = int(count/total*220)
            st.markdown(f'<div style="display:flex;align-items:center;gap:.6rem;padding:.3rem 0;border-bottom:1px solid rgba(201,169,110,.08)"><span style="font-size:.86rem;color:#9a8a6a;min-width:155px">{arch}</span><div style="height:6px;width:{bw}px;background:{color};border-radius:3px;opacity:.75"></div><span style="font-size:.78rem;color:#5a4a2a">{count}</span></div>', unsafe_allow_html=True)

# ══ ENTITY EXPLORER ═══════════════════════════════════════════════════════════
elif mode == "Entity Explorer":
    st.markdown("### Entity Explorer")
    col_s,col_f = st.columns([2,1])
    with col_s: query = st.text_input("Search", placeholder="e.g. Zeus, hero, underworld…")
    with col_f: pfilter = st.selectbox("Pantheon",["All"]+sorted(set(e.get("pantheon","Unknown") for e in entities)))
    filtered = entities
    if query:
        q=query.lower()
        filtered=[e for e in filtered if q in e["name"].lower() or q in e.get("description","").lower() or any(q in a.lower() for a in e.get("archetypes",[]))]
    if pfilter != "All": filtered=[e for e in filtered if e.get("pantheon")==pfilter]
    st.markdown(f'<div style="color:#5a4a2a;font-size:.82rem;margin-bottom:.5rem">{len(filtered)} entities</div>', unsafe_allow_html=True)

    if filtered:
        sel = st.selectbox("Select entity",[e["name"] for e in filtered])
        entity = next((e for e in entities if e["name"]==sel), None)
        if entity:
            st.markdown("---")
            cl,cr = st.columns([3,2])
            with cl:
                st.markdown(f'<div style="margin-bottom:.5rem"><span style="font-family:\'Cinzel\',serif;font-size:1.7rem;font-weight:700;color:#e8d5a0">{entity["name"]}</span></div><div style="font-size:.78rem;color:#7a6a4a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.8rem">{entity.get("type","").upper()} &bull; {entity.get("pantheon","?")} Pantheon</div>', unsafe_allow_html=True)
                desc = entity.get("description","")
                if desc:
                    st.markdown(f'<div style="font-style:italic;font-size:.97rem;color:#b0a080;line-height:1.7;border-left:2px solid rgba(201,169,110,.3);padding-left:1rem;margin-bottom:1rem">{desc}</div>', unsafe_allow_html=True)
                archs = entity.get("archetypes",[])
                if archs:
                    st.markdown("**Jungian Archetypes**")
                    st.markdown("".join(f'<span class="tag">{a}</span>' for a in archs), unsafe_allow_html=True)
                aliases = entity.get("aliases",[])
                if aliases:
                    st.markdown("<br>**Also known as**", unsafe_allow_html=True)
                    st.markdown("".join(f'<span class="tag">{a}</span>' for a in aliases), unsafe_allow_html=True)
                scores = entity.get("archetype_scores",{})
                if scores:
                    with st.expander("Archetype Score Breakdown"):
                        for arch,score in sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]:
                            ai2=ARCHETYPES.get(arch,{}); col2=ai2.get("color","#95A5A6"); bw2=int(score*300)
                            st.markdown(f'<div style="display:flex;align-items:center;gap:.5rem;padding:.2rem 0"><span style="font-size:.83rem;min-width:175px;color:#9a8a6a">{arch}</span><div style="height:4px;width:{bw2}px;background:{col2};border-radius:3px"></div><span style="font-size:.73rem;color:#5a4a2a">{score:.3f}</span></div>', unsafe_allow_html=True)
                ib = entity.get("infobox",{})
                if ib:
                    with st.expander("Infobox"):
                        for k,v in list(ib.items())[:8]:
                            st.markdown(f'<div style="display:flex;gap:1rem;padding:.25rem 0;border-bottom:1px solid rgba(201,169,110,.08);font-size:.88rem"><span style="color:#7a6a4a;min-width:110px">{k}</span><span style="color:#b0a080">{v}</span></div>', unsafe_allow_html=True)
            with cr:
                st.markdown("**Relations**")
                rels = onto.get_relations(entity["name"])
                if rels:
                    for rel in rels[:16]:
                        arrow = "→" if rel["direction"]=="out" else "←"
                        other = rel["target"] if rel["direction"]=="out" else rel["source"]
                        st.markdown(f'<div class="rel-row"><span style="color:#5a4a2a">{arrow}</span><span class="rel-type">{(rel["relation"] or "").replace("_"," ")}</span><span class="rel-target">{other}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#5a4a2a;font-style:italic;font-size:.85rem">No relations found</div>', unsafe_allow_html=True)

# ══ ARCHETYPES ════════════════════════════════════════════════════════════════
elif mode == "Archetypes":
    st.markdown("### Jungian Archetype Gallery")
    sel_arch = st.selectbox("Select Archetype", list(ARCHETYPES.keys()))
    ad = ARCHETYPES[sel_arch]; color=ad.get("color","#c9a96e")
    keyword_tags = "".join(f'<span class="tag">{kw}</span>' for kw in ad["keywords"])
    archetype_card_html = (
        f'<div style="background:linear-gradient(135deg,rgba(20,16,10,.95),rgba(30,24,14,.98));'
        f'border:1px solid {color}40;border-radius:14px;padding:1.5rem 2rem;margin-bottom:1.5rem">'
        f'<div style="font-family:\'Cinzel\',serif;font-size:1.5rem;font-weight:700;color:{color};margin-bottom:.5rem">'
        f'{sel_arch}</div>'
        f'<div style="font-style:italic;font-size:1rem;color:#9a8a6a;margin-bottom:.8rem">{ad["description"]}</div>'
        f'<div style="font-size:.8rem;color:#5a4a2a;margin-bottom:.5rem">'
        f'Shadow archetype: <span style="color:#8a7a5a">{ad.get("shadow") or "—"}</span></div>'
        f'{keyword_tags}</div>'
    )
    st.markdown(archetype_card_html, unsafe_allow_html=True)
    members = [e for e in entities if sel_arch in e.get("archetypes",[])]
    st.markdown(f"**{len(members)} entities**")
    if members:
        cols = st.columns(3)
        for i,e in enumerate(members[:12]):
            with cols[i%3]:
                pc = PANTHEON_COLORS.get(e.get("pantheon","Unknown"),"#95A5A6"); desc=e.get("description","")
                st.markdown(f'<div class="entity-card"><div class="entity-name">{e["name"]}</div><div class="entity-type">{e.get("type","")} &bull; <span style="color:{pc}">{e.get("pantheon","?")}</span></div><div class="entity-desc">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Cross-Archetype Overlap")
    ca1,ca2 = st.columns(2)
    with ca1: a1=st.selectbox("Archetype A",list(ARCHETYPES.keys()),key="ca1")
    with ca2: a2=st.selectbox("Archetype B",list(ARCHETYPES.keys()),index=1,key="ca2")
    m1={e["name"] for e in entities if a1 in e.get("archetypes",[])}
    m2={e["name"] for e in entities if a2 in e.get("archetypes",[])}
    overlap=m1&m2
    if overlap: st.markdown(f'**Shared ({len(overlap)}):** '+" ".join(f'`{n}`' for n in sorted(overlap)))
    else: st.markdown("*No shared entities.*")

# ══ GRAPH VISUALIZER ══════════════════════════════════════════════════════════
elif mode == "Graph Visualizer":
    st.markdown("### Interactive Knowledge Graph")
    color_mode = st.radio("Color nodes by", ["Archetype","Pantheon"], horizontal=True)
    color_key = "color" if color_mode=="Archetype" else "pantheon_color"
    d3_json = json.dumps(onto.to_d3())
    graph_bg = "#f4f6f8"
    graph_link = "rgba(25,35,50,.18)"
    graph_label = "#101828"
    tip_bg = "rgba(255,255,255,.98)"
    tip_border = "rgba(36,88,166,.35)"
    tip_name = "#0f172a"
    tip_body = "#334155"
    tip_meta = "#475569"
    node_border = "#ffffff"

    entity_desc_map = {e.get("name", ""): e.get("description", "") for e in entities if e.get("name")}
    archetype_desc_map = {k: v.get("description", "") for k, v in ARCHETYPES.items()}
    pantheon_desc_map = {
        "Greek": "Greek mythology centers on the Olympian gods, heroic epics, fate, and moral conflict between order and chaos.",
        "Norse": "Norse mythology emphasizes honor, prophecy, cosmic struggle, and the world cycle culminating in Ragnarok.",
        "Egyptian": "Egyptian mythology focuses on divine kingship, cosmic balance, afterlife judgment, and cycles of death and rebirth.",
        "Hindu": "Hindu mythology presents cosmic order, avatars, dharma, and interconnected divine roles of creation, preservation, and transformation.",
        "Celtic": "Celtic mythology highlights sovereignty, nature symbolism, warrior traditions, and the boundary between mortal and otherworld realms.",
        "Sumerian": "Sumerian mythology explores early kingship, mortality, divine authority, and foundational epic narratives.",
        "Roman": "Roman mythology adapts divine archetypes to civic identity, duty, and state order.",
        "Unknown": "This node is connected through mythic relations, but its pantheon context is not explicitly identified in the dataset.",
    }
    entity_desc_json = json.dumps(entity_desc_map)
    archetype_desc_json = json.dumps(archetype_desc_map)
    pantheon_desc_json = json.dumps(pantheon_desc_map)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Crimson+Text:ital@1&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{graph_bg};overflow:hidden}}
canvas{{display:block}}
#tip{{position:absolute;pointer-events:none;display:none;background:rgba(10,8,6,.96);border:1px solid rgba(201,169,110,.4);border-radius:8px;padding:8px 12px;color:#c9a96e;font-family:'Crimson Text',serif;font-size:13px;max-width:230px;line-height:1.5}}
#tip{{position:absolute;pointer-events:none;display:none;background:{tip_bg};border:1px solid {tip_border};border-radius:8px;padding:10px 12px;color:{tip_body};font-family:'Crimson Text',serif;font-size:13px;max-width:420px;max-height:62vh;overflow:auto;line-height:1.55;white-space:normal;box-shadow:0 8px 24px rgba(0,0,0,.12)}}
#tip .nm{{font-family:'Cinzel',serif;font-size:14px;font-weight:600;color:{tip_name}}}
#tip .ar{{font-style:italic;color:{tip_meta};font-size:12px}}
#tip .de{{font-size:12px;color:{tip_body};margin-top:6px}}
#inf{{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);color:{graph_label};font-size:11px;font-family:'Crimson Text',serif;letter-spacing:.04em}}
</style></head><body>
<canvas id="c"></canvas>
<div id="tip"><div class="nm" id="tn"></div><div class="ar" id="ta"></div><div class="de" id="td"></div></div>
<div id="inf">drag to pan &nbsp;·&nbsp; scroll to zoom &nbsp;·&nbsp; hover to inspect</div>
<script>
const DATA=__DATA_JSON__;const CK="{color_key}";
const ENTITY_DESC=__ENTITY_DESC_JSON__;
const ARCHETYPE_DESC=__ARCHETYPE_DESC_JSON__;
const PANTHEON_DESC=__PANTHEON_DESC_JSON__;
const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
const tip=document.getElementById('tip');
let W,H;
function norm(s){{
    return (s||'').toLowerCase().replace(/^the\\s+/, '').trim();
}}
const ARCHETYPE_BY_NORM = Object.fromEntries(
    Object.entries(ARCHETYPE_DESC).map(([k,v])=>[norm(k), {{name:k, desc:v}}])
);
function hexToRgb(hex){{
    const h=(hex||'').replace('#','');
    if(h.length!==6)return {{r:149,g:165,b:166}};
    return {{r:parseInt(h.slice(0,2),16),g:parseInt(h.slice(2,4),16),b:parseInt(h.slice(4,6),16)}};
}}
function rgbToHex(r,g,b){{
    const toHex=v=>Math.max(0,Math.min(255,Math.round(v))).toString(16).padStart(2,'0');
    return `#${{toHex(r)}}${{toHex(g)}}${{toHex(b)}}`;
}}
function luminance(hex){{
    const c=hexToRgb(hex);
    return (0.2126*c.r+0.7152*c.g+0.0722*c.b)/255;
}}
function mix(hexA,hexB,t){{
    const a=hexToRgb(hexA),b=hexToRgb(hexB);
    return rgbToHex(a.r+(b.r-a.r)*t,a.g+(b.g-a.g)*t,a.b+(b.b-a.b)*t);
}}
function ensureNodeColor(hex){{
    const base = /^#[0-9a-fA-F]{{6}}$/.test(hex||'') ? hex : '#95A5A6';
    const l=luminance(base);
    if(l>0.8)return mix(base,'#111111',0.4);
    if(l<0.18)return mix(base,'#4b5563',0.35);
    return base;
}}
function buildDescription(n){{
    const nodeName=(n.id||'').trim();
    const nodeType=(n.type||'').toString().toLowerCase();
    const nodeNorm=norm(nodeName);
    const archetypeMatch = ARCHETYPE_BY_NORM[nodeNorm] || null;
    if (archetypeMatch) {{
        return `${{archetypeMatch.name}} is a Jungian archetype. ${{archetypeMatch.desc}}`;
    }}

    const entityDesc=(ENTITY_DESC[n.id]||'').trim();
    if(entityDesc) return entityDesc;

    if (nodeType === 'archetype') {{
        const pa = n.primary_archetype || '';
        const paText = pa && ARCHETYPE_DESC[pa] ? ARCHETYPE_DESC[pa] : '';
        if (paText) return `${{nodeName}} is represented through Jungian analysis as ${{pa}}. ${{paText}}`;
        return `${{nodeName}} is represented in the graph as a Jungian archetypal construct linked to mythic roles and symbols.`;
    }}

    const direct=(n.description||'').trim();
    if(direct) return direct;
    const pantheon = n.pantheon || 'Unknown';
    const pantheonText = PANTHEON_DESC[pantheon] || PANTHEON_DESC['Unknown'];
    const arch = n.primary_archetype || '';
    const archText = arch && ARCHETYPE_DESC[arch] ? ARCHETYPE_DESC[arch] : '';
    const role = (n.type || 'entity').toString().replace('_', ' ');

    const isDeityLike = /deit|god|goddess/i.test(nodeType);
    if (!isDeityLike) {{
        if (archText) {{
            return `${{nodeName}} is a mythological ${{role}} interpreted through the Jungian lens of ${{arch}}. ${{archText}}`;
        }}
        return `${{nodeName}} is a mythological ${{role}} connected to symbolic and narrative structures in this ontology.`;
    }}

    if(archText){{
        if (pantheon && pantheon !== 'Unknown') {{
            return `${{nodeName}} is a ${{role}} associated with the ${{pantheon}} pantheon. Archetypally, it maps to ${{arch}}: ${{archText}} ${{pantheonText}}`;
        }}
        return `${{nodeName}} is a ${{role}} interpreted through the Jungian archetype ${{arch}}: ${{archText}}`;
    }}
    if (pantheon && pantheon !== 'Unknown') {{
        return `${{nodeName}} is a ${{role}} associated with the ${{pantheon}} pantheon. ${{pantheonText}}`;
    }}
    return `${{nodeName}} is a ${{role}} represented in this mythological knowledge graph.`;
}}
function positionTip(clientX, clientY){{
    const pad = 12;
    const w = tip.offsetWidth;
    const h = tip.offsetHeight;
    let left = clientX + 16;
    let top = clientY - 12;
    if (left + w + pad > window.innerWidth) left = clientX - w - 16;
    if (left < pad) left = pad;
    if (top + h + pad > window.innerHeight) top = window.innerHeight - h - pad;
    if (top < pad) top = pad;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
}}
function resize(){{W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight}}
resize();window.addEventListener('resize',()=>{{resize();draw()}});
const nodes=DATA.nodes.map(n=>({{...n,x:W/2+(Math.random()-.5)*500,y:H/2+(Math.random()-.5)*400,vx:0,vy:0}}));
const links=DATA.links;
const nm=Object.fromEntries(nodes.map(n=>[n.id,n]));
let frame=0,pan={{x:0,y:0}},zoom=1,drag=null,lastM=null;
function sim(){{
  for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){{
    const a=nodes[i],b=nodes[j],dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+1,d=Math.sqrt(d2),f=5500/d2;
    a.vx-=f*dx/d;a.vy-=f*dy/d;b.vx+=f*dx/d;b.vy+=f*dy/d;
  }}
  for(const l of links){{
    const a=nm[l.source],b=nm[l.target];if(!a||!b)continue;
    const dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)+.01,f=(d-90)*.007*(l.weight||1);
    a.vx+=f*dx/d;a.vy+=f*dy/d;b.vx-=f*dx/d;b.vy-=f*dy/d;
  }}
  for(const n of nodes){{
    n.vx+=(W/2-n.x)*.0004;n.vy+=(H/2-n.y)*.0004;
    n.vx*=.86;n.vy*=.86;n.x+=n.vx;n.y+=n.vy;
  }}
}}
function draw(){{
  ctx.clearRect(0,0,W,H);
  ctx.save();ctx.translate(pan.x,pan.y);ctx.translate(W/2,H/2);ctx.scale(zoom,zoom);ctx.translate(-W/2,-H/2);
  for(const l of links){{
    const a=nm[l.source],b=nm[l.target];if(!a||!b)continue;
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
        ctx.strokeStyle='{graph_link}';ctx.lineWidth=.8;ctx.stroke();
  }}
  for(const n of nodes){{
        const r=n.size||10,col=ensureNodeColor(n[CK]||'#95A5A6');
    ctx.beginPath();ctx.arc(n.x,n.y,r,0,Math.PI*2);ctx.fillStyle=col+'cc';ctx.fill();
        ctx.strokeStyle='{node_border}';ctx.lineWidth=1.2;ctx.stroke();
    if(r>12||zoom>1.5){{
            ctx.fillStyle='{graph_label}';ctx.font=`${{Math.max(9,Math.min(12,r*.9))}}px Cinzel`;
      ctx.textAlign='center';ctx.textBaseline='middle';
      const lbl=n.id.length>13?n.id.slice(0,12)+'…':n.id;
      ctx.fillText(lbl,n.x,n.y+r+9);
    }}
  }}
  ctx.restore();
}}
canvas.addEventListener('mousedown',e=>{{
  const p=tw(e.clientX,e.clientY);
  for(const n of nodes){{if(Math.hypot(n.x-p.x,n.y-p.y)<n.size+5){{drag=n;return}}}}
  lastM={{x:e.clientX,y:e.clientY}};
}});
canvas.addEventListener('mousemove',e=>{{
  if(drag){{const p=tw(e.clientX,e.clientY);drag.x=p.x;drag.y=p.y;drag.vx=0;drag.vy=0;return}}
  if(lastM){{pan.x+=e.clientX-lastM.x;pan.y+=e.clientY-lastM.y;lastM={{x:e.clientX,y:e.clientY}};return}}
  const p=tw(e.clientX,e.clientY);let found=null;
  for(const n of nodes){{if(Math.hypot(n.x-p.x,n.y-p.y)<n.size+7){{found=n;break}}}}
  if(found){{
    document.getElementById('tn').textContent=found.id;
        const meta=[found.type||'', found.pantheon||'', found.primary_archetype||''].filter(Boolean).join(' • ');
        document.getElementById('ta').textContent=meta;
        document.getElementById('td').textContent=buildDescription(found);
        tip.style.display='block';
        positionTip(e.clientX, e.clientY);
  }}else tip.style.display='none';
}});
canvas.addEventListener('mouseup',()=>{{drag=null;lastM=null}});
canvas.addEventListener('wheel',e=>{{zoom*=e.deltaY>0?.93:1.07;zoom=Math.max(.12,Math.min(4,zoom))}},{{passive:true}});
function tw(cx,cy){{return{{x:(cx-pan.x-W/2)/zoom+W/2,y:(cy-pan.y-H/2)/zoom+H/2}}}}
function loop(){{if(frame++<350)sim();draw();requestAnimationFrame(loop)}}
loop();
</script></body></html>"""\
    .replace("__DATA_JSON__", d3_json)\
    .replace("__ENTITY_DESC_JSON__", entity_desc_json)\
    .replace("__ARCHETYPE_DESC_JSON__", archetype_desc_json)\
    .replace("__PANTHEON_DESC_JSON__", pantheon_desc_json)

    components.html(html, height=600)

# ══ PATH FINDER ═══════════════════════════════════════════════════════════════
elif mode == "Path Finder":
    st.markdown("### Mythological Path Finder")
    st.markdown('<div style="font-style:italic;color:#7a6a4a;margin-bottom:1.5rem;font-size:.95rem">Trace the mythological thread connecting any two entities.</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: src=st.selectbox("From",entity_names,key="src")
    with c2:
        default=entity_names[min(6,len(entity_names)-1)]
        tgt=st.selectbox("To",entity_names,index=entity_names.index(default) if default in entity_names else 0,key="tgt")
    if st.button("Find Path", use_container_width=True):
        path = onto.find_path(src, tgt)
        if path:
            steps = "".join(f'<span class="path-step">{n}</span><span style="color:#5a4a2a;margin:0 2px">→</span>' if i<len(path)-1 else f'<span class="path-step">{n}</span>' for i,n in enumerate(path))
            st.markdown(f'<div style="background:rgba(20,16,10,.9);border:1px solid rgba(201,169,110,.25);border-radius:12px;padding:1.5rem;margin:1rem 0"><div style="font-family:\'Cinzel\',serif;font-size:.75rem;color:#5a4a2a;letter-spacing:.1em;margin-bottom:.8rem">PATH LENGTH: {len(path)-1} HOPS</div><div style="line-height:2.5">{steps}</div></div>', unsafe_allow_html=True)
            st.markdown("**Relation chain**")
            for i in range(len(path)-1):
                a,b=path[i],path[i+1]
                rels=onto.get_relations(a,direction="out")
                rel_lbl=next((r["relation"].replace("_"," ") for r in rels if r["target"]==b),"connected to")
                st.markdown(f'<div class="rel-row"><span style="color:#c9a96e;font-family:\'Cinzel\',serif;font-size:.85rem">{a}</span><span style="color:#5a4a2a">→</span><span class="rel-type">{rel_lbl}</span><span style="color:#5a4a2a">→</span><span class="rel-target">{b}</span></div>', unsafe_allow_html=True)
        else:
            st.warning(f"No path found between **{src}** and **{tgt}**.")
    st.markdown("---")
    st.markdown("#### Cross-Archetype Bridges")
    bridges = onto.cross_archetype_bridges()
    if bridges:
        st.dataframe(pd.DataFrame(bridges[:25]),use_container_width=True,hide_index=True)

# ══ ANALYSIS ══════════════════════════════════════════════════════════════════
elif mode == "Analysis":
    st.markdown("### Graph Analysis")
    cols = st.columns(5)
    for col,lbl,val in zip(cols,["Nodes","Edges","Density","Components","Avg Degree"],
                           [stats["nodes"],stats["edges"],stats["density"],stats["components"],stats["avg_degree"]]):
        with col:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.5rem">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cl,cr = st.columns(2)
    with cl:
        st.markdown("#### Pantheon Breakdown")
        pc={}
        for e in entities: p=e.get("pantheon","Unknown"); pc[p]=pc.get(p,0)+1
        total=max(sum(pc.values()),1)
        for p,c in sorted(pc.items(),key=lambda x:x[1],reverse=True):
            col2=PANTHEON_COLORS.get(p,"#95A5A6"); bw=int(c/total*260)
            st.markdown(f'<div style="display:flex;align-items:center;gap:.6rem;padding:.3rem 0;border-bottom:1px solid rgba(201,169,110,.08)"><span style="font-size:.88rem;color:#9a8a6a;min-width:80px">{p}</span><div style="height:6px;width:{bw}px;background:{col2};border-radius:3px;opacity:.75"></div><span style="font-size:.78rem;color:#5a4a2a">{c}</span></div>', unsafe_allow_html=True)
    with cr:
        st.markdown("#### Top Relation Types")
        rc={}
        for _,_,d in onto.graph.edges(data=True): r=d.get("relation","?"); rc[r]=rc.get(r,0)+1
        total_r=max(sum(rc.values()),1)
        for rel,count in sorted(rc.items(),key=lambda x:x[1],reverse=True)[:10]:
            bw=int(count/total_r*260)
            st.markdown(f'<div style="display:flex;align-items:center;gap:.6rem;padding:.28rem 0;border-bottom:1px solid rgba(201,169,110,.08)"><span style="font-style:italic;font-size:.86rem;color:#9a8a6a;min-width:125px">{rel.replace("_"," ")}</span><div style="height:5px;width:{bw}px;background:#c9a96e;border-radius:3px;opacity:.6"></div><span style="font-size:.76rem;color:#5a4a2a">{count}</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Full Entity Table")
    centrality=onto.centrality()
    rows=[{"Name":e["name"],"Type":e.get("type",""),"Pantheon":e.get("pantheon",""),
           "Primary Archetype":e.get("primary_archetype",""),
           "Centrality":round(centrality.get(e["name"],0),4),
           "Relations":len(onto.get_relations(e["name"]))} for e in entities]
    st.dataframe(pd.DataFrame(rows).sort_values("Centrality",ascending=False),use_container_width=True,hide_index=True)
