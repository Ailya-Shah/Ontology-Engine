# Mythological Ontology Engine

A machine-readable Jungian knowledge graph of world mythology, built on Jungian archetypal psychology theory and powered by semantic entity extraction, relationship inference, and interactive graph visualization.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Features](#features)
- [The Ontology](#the-ontology)
  - [Jungian Archetypes](#jungian-archetypes)
  - [Entities](#entities)
  - [Relations](#relations)
- [Installation](#installation)
- [Usage](#usage)
  - [Building the Knowledge Graph](#building-the-knowledge-graph)
  - [Running the Explorer](#running-the-explorer)
- [Application Views](#application-views)
- [Data Model](#data-model)
- [Technical Specifications](#technical-specifications)
- [Development](#development)
- [Extending the Ontology](#extending-the-ontology)
- [Performance Considerations](#performance-considerations)
- [Dependencies](#dependencies)

---

## Overview

The Mythological Ontology Engine transforms unstructured mythological narratives from multiple world traditions (Greek, Norse, Egyptian, Indian, Mesoamerican, etc.) into a structured, machine-readable knowledge graph. The system uses Jungian archetypal psychology as the organizing principle, classifying mythological entities into eight universal psychological patterns identified by Carl Jung.

The knowledge graph is queryable, traversable, and visualizable through an interactive Streamlit application featuring real-time graph rendering, semantic search, pathway analysis, and network metrics.

## Core Concepts

### Jungian Archetypes

Archetypes are universal, primordial prototypes of human behavior and psychology. Jung proposed that these patterns exist in the collective unconscious and appear across all human cultures. The system models eight core archetypes, each representing a distinct psychological dimension:

- **The Hero**: The warrior, the courageous protagonist, the overcomer of obstacles
- **The Shadow**: The repressed, the dangerous, the embodiment of what society rejects
- **The Wise Old Man**: The mentor, the sage, the source of wisdom and guidance
- **The Great Mother**: The caregiver, the nurturer, the source of life
- **The Trickster**: The boundary-crosser, the chaos-bringer, the rule-breaker
- **The Anima**: The feminine principle, the soulmate, the romantic ideal
- **The Child**: The innocent, the vulnerable, the promise of renewal
- **The Self**: The totality, the ultimate archetype, the goal of individuation

Each mythological entity is scored against these archetypes based on narrative role, attributes, relationships, and etymology.

### Ontology Structure

The ontology is a heterogeneous information network consisting of:

1. **Entities**: Mythological beings (gods, heroes, creatures, mythological objects)
2. **Attributes**: Properties tied to entities (archetype scores, origin pantheon, domain/domain)
3. **Relations**: Semantic connections between entities (parent_of, enemy_of, lover_of, etc.)

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation & Run

```bash
# Clone or navigate to project
cd Ontology-Engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build the knowledge graph (offline mode - no network required)
python -c "import pipeline; pipeline.run_pipeline(use_network=False)"

# Launch the explorer
streamlit run app/ontology_explorer.py
```

The application will be available at `http://127.0.0.1:8501`.

---

## Project Structure

```
Ontology-Engine/
├── engine/
│   ├── __init__.py
│   ├── schema.py                 # Core definitions: archetypes, relations, data sources
│   ├── scraper.py                # Entity extraction, Wikipedia integration, seed dataset
│   ├── archetype_mapper.py       # Jungian scoring engine
│   ├── relation_extractor.py     # Semantic relationship extraction
│   ├── ontology.py               # NetworkX graph construction and D3 export
│   └── connection_manager.py     # Optional database layer (placeholder)
│
├── app/
│   ├── __init__.py
│   └── ontology_explorer.py      # Streamlit interactive application
│
├── data/
│   ├── raw/                      # Raw scraped or imported data
│   ├── entities/                 # Processed entity JSON files
│   └── relations/                # Extracted relationship data
│
├── knowledge_graph/
│   ├── graph.json                # Serialized graph structure
│   ├── entities_full.json        # Complete entity registry
│   └── relations_full.json       # Complete relation registry
│
├── output/
│   ├── d3_graph.json             # D3-formatted graph for visualization
│   └── analysis_stats.json       # Computed network statistics
│
├── pipeline.py                   # Main orchestrator: execution, building, caching
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## System Architecture

### Pipeline Architecture

```
Pipeline Orchestrator (pipeline.py)
│
├─→ Scraper (scraper.py)
│   ├─ Loads seed dataset (32 curated entities)
│   ├─ [Optional] Wikipedia scraper
│   └─ Outputs: entities/
│
├─→ Archetype Mapper (archetype_mapper.py)
│   ├─ Keyword matching analysis
│   ├─ Name-etymology scoring
│   ├─ Infobox attributes parsing
│   └─ Outputs: scored entities
│
├─→ Relation Extractor (relation_extractor.py)
│   ├─ Curated relation registry
│   ├─ Pattern-based extraction
│   ├─ Infobox link parsing
│   └─ Outputs: relations/
│
└─→ Ontology Builder (ontology.py)
    ├─ Constructs NetworkX MultiDiGraph
    ├─ Computes network metrics
    ├─ Exports to D3 JSON format
    └─ Outputs: knowledge_graph/ + output/
```

### Application Architecture

```
Streamlit App (ontology_explorer.py)
│
├─ Session State Management
│   ├─ Graph instance caching
│   └─ User interaction history
│
├─ Six Interactive Views
│   ├─ Overview Dashboard
│   ├─ Entity Explorer
│   ├─ Archetype Gallery
│   ├─ Graph Visualizer (D3.js embedded)
│   ├─ Path Finder
│   └─ Analytics Dashboard
│
└─ Backend Interfaces
    ├─ Query engine (shortest paths, filters)
    ├─ Search (entity lookup, archetype search)
    └─ Visualization (D3 rendering, color schemes)
```

---

## Features

### Core Engine Features

- **Intelligent Archetype Classification**: Multi-factor scoring using keyword relevance, etymological analysis, and narrative attributes
- **Relationship Extraction**: 18+ semantic relationship types extracted from curated definitions and infobox data
- **Network Analysis**: Centrality metrics (degree, betweenness, closeness), clustering analysis, shortest path computation
- **Multi-Source Integration**: Support for Wikipedia scraping and offline seed data
- **Caching**: Efficient in-memory caching of compiled graphs and computation results

### Application Features

- **Real-time Graph Visualization**: D3.js force-directed graph with interactive node exploration
- **Semantic Search**: Full-text entity search with fuzzy matching
- **Navigation**: Breadth-first path finding between any two entities
- **Multi-Criteria Filtering**: Filter by archetype, pantheon, relation type
- **Detailed Entity Profiles**: Rich metadata including descriptions, relations, archetype scores
- **Network Metrics**: Centrality rankings, clustering coefficients, density analysis
- **Export Capabilities**: JSON export of filtered subgraphs, entity lists, relation chains

---

## The Ontology

### Jungian Archetypes

| Archetype | Psychological Dimension | Core Traits | Example Entities |
|-----------|------------------------|------------|------------------|
| The Hero | Courage, Will, Action | Warrior, Overcomer, Sacrifice | Hercules, Perseus, Gilgamesh, Achilles, Beowulf |
| The Shadow | Repression, Darkness, Taboo | Feared Power, Enemy, Destruction | Hades, Loki, Set, Typhon, Jormungandr |
| The Wise Old Man | Wisdom, Mentorship, Reflection | Guide, Sage, Knowledge-Keeper | Zeus, Odin, Chiron, Thoth, Merlin |
| The Great Mother | Nurturing, Cycles, Fertility | Creator, Protector, Devourer | Gaia, Demeter, Isis, Kali, Coatlicue |
| The Trickster | Cunning, Transformation, Chaos | Boundary-Crosser, Fool, Shapeshifter | Hermes, Loki, Coyote, Anansi, Eshu |
| The Anima | Feminine Principle, Soul, Desire | Lover, Muse, Inspiration | Persephone, Psyche, Aphrodite, Isolde |
| The Child | Innocence, Renewal, Vulnerability | Divine Child, Orphan, Lover | Dionysus, Horus, Apollo, Krishna |
| The Self | Totality, Individuation, Transcendence | Ultimate Goal, Cosmic Principle, Unity | Ra, Vishnu, Brahman, Atman |

### Entities

Current dataset includes **32+ base entities** spanning:

- **Greek Pantheon**: Zeus, Hera, Aphrodite, Ares, Athena, Apollo, Artemis, Hades, Poseidon, etc.
- **Norse Pantheon**: Odin, Thor, Loki, Frigg, Heimdall, etc.
- **Egyptian Pantheon**: Ra, Osiris, Isis, Set, Thoth, etc.
- **Indian Pantheon**: Brahman, Vishnu, Shiva, Kali, Durga, etc.
- **Mesoamerican Pantheon**: Quetzalcoatl, Tezcatlipoca, Xbalanque, etc.
- **Heroes & Legendary Figures**: Hercules, Perseus, Gilgamesh, Achilles, Arthur, Merlin

Each entity stores:
- **Core attributes**: Name, pantheon, domain
- **Archetype scores**: Dictionary of archetype → confidence (0.0–1.0)
- **Relations**: Incoming and outgoing edges with relation type
- **Metadata**: Description, Wikipedia URL, key attributes

### Relations

**18+ Semantic Relation Types**:

- **Kinship**: parent_of, child_of, sibling_of, spouse_of
- **Conflict**: enemy_of, opposes, defeats, conflicts_with
- **Support**: allies_with, mentors, guides, protects
- **Romantic**: lover_of, beloved_by
- **Domain**: associated_with (domain/domain)
- **Mythological**: embodies, counterpart_of, predecessor_of
- **Transformation**: transforms_into, reborn_as
- **Creation**: creates, manifests_from

Relations are directional and support multi-edges (MultiDiGraph).

---

## Installation

### System Requirements

- Python 3.8 or higher
- 100 MB disk space
- Internet connection (optional, for Wikipedia scraping)

### Step-by-Step Installation (Chronological)

```bash
# 1) Clone the repository
git clone https://github.com/Ailya-Shah/Ontology-Engine.git

# 2) Enter the project directory
cd Ontology-Engine

# 3) Create a virtual environment (choose ONE option)

# Option A: venv (recommended)
python -m venv venv

# Option B: conda
# conda create -n ontology-engine python=3.10 -y
# conda activate ontology-engine

# 4) Activate the virtual environment (venv only)
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt):
venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate

# 5) Install dependencies
pip install -r requirements.txt

# 6) Verify installation
python -c "import streamlit, networkx, pandas; print('All dependencies installed.')"
```

---

## Usage

### Building the Knowledge Graph

#### Offline Mode (No Network Required)

```python
import pipeline

# Build from seed data only
pipeline.run_pipeline(use_network=False)
```

This creates:
- `data/entities/` — Processed entity files
- `knowledge_graph/graph.json` — Full graph structure
- `output/d3_graph.json` — Visualization format

#### Online Mode (With Wikipedia Scraping)

```python
import pipeline

# Build with Wikipedia enrichment
pipeline.run_pipeline(use_network=True, max_wiki_calls=50)
```

**Note**: This requires internet and may take 2-5 minutes depending on network speed.

### Running the Explorer

```bash
streamlit run app/ontology_explorer.py
```

## Application Views

### 1. Overview Dashboard

High-level statistics and key metrics:
- Total entities, relationships, archetypes
- Top entities by network centrality
- Archetype distribution across pantheons
- Quick stats (graph density, clustering coefficient, average path length)

### 2. Entity Explorer

Entity search and detailed profile view:
- Full-text search with entity cards
- Detailed profile: description, archetype scores, pantheon, domain
- Incoming/outgoing relations with clickable navigation
- Related entities by archetype or pantheon

### 3. Archetype Gallery

Archetype-centric view:
- All 8 archetypes with detailed psychological descriptions
- Entities mapped to each archetype with archetype confidence scores
- Overlap visualization: entities that embody multiple archetypes
- Archetype comparison matrix

### 4. Graph Visualizer

Interactive D3.js force-directed graph:
- Real-time node/edge interaction
- Color coding by archetype or pantheon
- Node size = network centrality
- Tooltip hover with entity details
- Zoom, pan, and node dragging
- Filter by archetype, pantheon, relation type

### 5. Path Finder

Shortest path analysis:
- Select source and destination entities
- Compute and visualize the shortest path
- Display complete relation chain
- Show alternate paths if available

### 6. Analytics Dashboard

Network analysis and statistics:
- Pantheon breakdown with entity counts
- Relation type frequency distribution
- Top entities by various centrality metrics
- Full sortable table of all entities with metadata
- Export filtered data as JSON

---

## Data Model

### Storage Strategy

**No external database required.** All data is stored as JSON files:

- **Entities**: `knowledge_graph/entities_full.json` — Complete entity registry
- **Relations**: `knowledge_graph/relations_full.json` — Relationship data
- **Graph**: `knowledge_graph/graph.json` — Serialized graph structure
- **Visualization**: `output/d3_graph.json` — D3-formatted graph

### Runtime State

During execution:
- Entities and relations are loaded into Python dictionaries
- Full graph is constructed as a NetworkX `MultiDiGraph`
- Network metrics are computed and cached in session state
- Visualization data is generated on-demand or cached

### Data Rebuilding

```bash
# Complete rebuild from source
python -c "import pipeline; pipeline.run_pipeline(use_network=False, force_rebuild=True)"
```

---

## Technical Specifications

### Archetype Scoring Algorithm

Each entity receives archetype scores via multi-factor analysis:

```
Total Score = w1 * keyword_score + w2 * etymology_score + w3 * infobox_score

where:
  keyword_score    = relevance of entity description to archetype keywords
  etymology_score  = name-based archetype correlation
  infobox_score    = attribute parsing from structured data
  w1, w2, w3       = learned/tuned weights (currently equal 1/3 each)
```

Final scores are normalized to 0.0–1.0 range.

### Relation Extraction

Relations are extracted via:

1. **Curated Registry**: Hand-defined relation triples (e.g., Zeus parent_of Aphrodite)
2. **Pattern Matching**: Regex patterns on entity descriptions
3. **Infobox Parsing**: Structured data from Wikipedia infoboxes
4. **Inference**: Optional rule-based relationship inference (disabled by default)

### Network Metrics

Computed for each entity:

- **Degree Centrality**: Number of direct connections
- **Betweenness Centrality**: How often entity lies on shortest paths
- **Closeness Centrality**: Average distance to all other entities
- **Clustering Coefficient**: How interconnected the entity's neighbors are
- **PageRank**: Importance score based on incoming connections

---

## Development

### Project Organization

- **Pipeline Layer** (`pipeline.py`): Orchestrates all processing steps
- **Engine Layer** (`engine/`): Core algorithms and graph construction
- **Application Layer** (`app/`): User interface and visualization
- **Data Layer** (`data/`, `knowledge_graph/`, `output/`): Persistent storage

### Adding New Functionality

1. **Add Entities**: Extend `SEED_ENTITIES` in `engine/scraper.py`
2. **Add Archetypes**: Modify archetype definitions and keywords in `engine/schema.py`
3. **Add Relations**: Extend `CURATED_RELATIONS` in `engine/relation_extractor.py`
4. **Add Pantheons**: Update `SCRAPE_SOURCES` in `engine/schema.py`
5. **Add Views**: Create new tabs in `app/ontology_explorer.py`

### Code Style

- Follows PEP 8 conventions
- Minimal comments; code is self-documenting
- Clear function and variable names
- Professional logging messages

---

## Extending the Ontology

### Add a New Pantheon

Edit `engine/schema.py`:

```python
SCRAPE_SOURCES = {
    "Greek": "Category:Greek_deities",
    "Norse": "Category:Norse_gods",
    "MyNewPantheon": "Category:My_New_Pantheon",  # Add here
}
```

### Add New Entities

Edit `engine/scraper.py` in the `SEED_ENTITIES` dictionary:

```python
SEED_ENTITIES = {
    "NewEntity": {
        "pantheon": "MyNewPantheon",
        "domain": "Domain of the entity",
        "description": "Detailed description...",
        "wikipedia_url": "Optional Wikipedia link",
    },
    # ... existing entities
}
```

### Add New Relations

Edit `engine/relation_extractor.py` in `CURATED_RELATIONS`:

```python
CURATED_RELATIONS = [
    ("Entity1", "relation_type", "Entity2"),
    # ... existing relations
    ("NewEntity1", "new_relation_type", "NewEntity2"),
]
```

### Add New Relation Types

Update `RELATION_TYPES` in `engine/schema.py`.

### Create Custom Analysis Views

Add new tabs to `app/ontology_explorer.py` using Streamlit's tab API:

```python
with st.tabs(["Overview", "Explorer", "YourNewView"]):
    with st.tabs()[2]:  # YourNewView
        # Your custom visualization/analysis here
        pass
```

---

## Performance Considerations

### Current Limitations

- **Scalability**: Tested up to ~200 entities. Full graph rendering may slow with >500 entities.
- **Wikipedia Scraping**: Network calls are synchronous; large scraping jobs take 2-5 minutes.
- **Memory**: Full graph + metrics consume ~10-20 MB for base dataset.

### Optimization Opportunities

1. **Async Scraping**: Use `aiohttp` for parallel Wikipedia calls
2. **Graph Caching**: Serialize compiled graph to avoid re-computation
3. **Incremental Updates**: Add only new entities/relations instead of full rebuild
4. **Database Backend**: Optional PostgreSQL layer for large-scale deployments
5. **Distributing Computation**: Use Dask or Ray for multi-threaded processing

### Profiling

```python
import cProfile
import pipeline

profiler = cProfile.Profile()
profiler.enable()

pipeline.run_pipeline()

profiler.disable()
profiler.print_stats()
```

---

## Dependencies

Core dependencies specified in `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| networkx | ^2.8 | Graph data structure and algorithms |
| streamlit | ^1.28 | Interactive web application framework |
| pandas | ^2.0 | Data manipulation and analysis |
| requests | ^2.31 | HTTP library for Wikipedia scraping |
| beautifulsoup4 | ^4.12 | HTML parsing for Wikipedia |
| lxml | ^4.9 | XML/HTML processing |

Install all at once:

```bash
pip install -r requirements.txt
```

---

## Future Roadmap

- **Enhanced Archetype Scoring**: ML-based archetype classification using embeddings
- **temporal_relations**: Timeline support for mythological chronology
- **Narrative Chains**: Story arc extraction and visualization
- **Multi-Language Support**: Non-English mythological sources
- **REST API**: GraphQL/REST endpoints for external integrations
- **Database Backend**: PostgreSQL with Alembic migrations
- **Advanced Visualization**: 3D graph rendering, VR support
- **Recommendation Engine**: Suggest similar entities based on archetype patterns

---

## Contributing

Enhancements welcome. Consider extending with:

- New pantheons from underrepresented cultures
- Improved archetype classification algorithms
- Advanced network analysis (community detection, influence propagation)
- Domain-specific relation types

---

## Contact

For questions, issues, or contributions, please open an issue on the [GitHub repository](https://github.com/ailya-shah/Ontology-Engine).

---

## Acknowledgments

**Author**: [Ailya Shah](https://www.linkedin.com/in/ailya-shah/) — BS Data Science, SEECS, NUST

**Framework Credits**:
- **Jungian Psychology**: Carl Jung's work on archetypes and the collective unconscious
- **Wikipedia**: Data source for mythological entity information
- **NetworkX**: Graph analysis library for network science
- **Streamlit**: Interactive web application framework
- **D3.js**: Web-based graph visualization library
- **Pandas**: Data manipulation and analysis
- **BeautifulSoup4**: HTML/XML parsing for web scraping

---

**Last Updated**: 2026-03-23 13:30:20