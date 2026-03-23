# 🏛️ Mythological Ontology Engine

> A machine-readable Jungian knowledge graph of world mythology.

## Quick Start

```bash
python -m venv venv
# Windows (PowerShell): .\\venv\\Scripts\\Activate.ps1
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
# Offline/local build (no network):
python -c "import pipeline; pipeline.run_pipeline(use_network=False)"
# Optional network-enriched build:
# python pipeline.py
streamlit run app/ontology_explorer.py
```

## Storage Model

This project uses no external database.

- Input/output data is stored as JSON files under `data/`, `knowledge_graph/`, and `output/`.
- Runtime state is in-memory dictionaries and a NetworkX graph object.
- Rebuilding the project regenerates local files from seed data and/or scraped data.

## Architecture

```
myth/
├── engine/
│   ├── schema.py              # 8 archetypes, 18 relation types, scrape sources
│   ├── scraper.py             # Wikipedia scraper + 32-entity offline seed dataset
│   ├── archetype_mapper.py    # Jungian scoring via keyword + name lookup + infobox
│   ├── relation_extractor.py  # 50 curated relations + regex extraction
│   └── ontology.py            # NetworkX MultiDiGraph + D3 export
├── app/
│   └── ontology_explorer.py   # Streamlit explorer (6 views, gold ancient theme)
├── pipeline.py                # One-command orchestrator
└── requirements.txt
```

## The 6 App Views

| View | What it shows |
|------|--------------|
| ⚡ Overview | Stats, top entities by centrality, archetype distribution |
| 🔍 Entity Explorer | Search + full entity detail with relations |
| 🎭 Archetypes | Gallery of all 8 Jungian archetypes + cross-archetype overlap |
| 🕸️ Graph Visualizer | Live D3 force-directed graph, color by archetype or pantheon |
| 🔗 Path Finder | Shortest path between any two entities + relation chain |
| 📊 Analysis | Pantheon breakdown, relation types, full sortable entity table |

## Archetypes Modeled

| | Archetype | Example entities |
|-|-----------|-----------------|
| ⚔️ | The Hero | Hercules, Perseus, Gilgamesh, Achilles |
| 🌑 | The Shadow | Hades, Loki, Set, Typhon |
| 🦉 | The Wise Old Man | Zeus, Odin, Chiron, Thoth |
| 🌙 | The Great Mother | Gaia, Demeter, Isis, Kali |
| 🎭 | The Trickster | Hermes, Loki, Coyote, Anansi |
| 🦋 | The Anima | Persephone, Psyche, Aphrodite |
| 🌅 | The Child | Dionysus, Horus, Apollo |
| ☀️ | The Self | Ra, Vishnu, Brahman |

## Extending

- Add pantheons: edit `SCRAPE_SOURCES` in `engine/schema.py`
- Add entities: extend `SEED_ENTITIES` in `engine/scraper.py`
- Add relations: extend `CURATED_RELATIONS` in `engine/relation_extractor.py`
- Bridge to Breaking Bad: run any character's text through `ArchetypeMapper().classify()`
