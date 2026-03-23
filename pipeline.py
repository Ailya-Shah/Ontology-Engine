"""Mythological Ontology Engine — Pipeline Orchestrator"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine.scraper import MythologyScraper, SEED_ENTITIES
from engine.archetype_mapper import ArchetypeMapper
from engine.relation_extractor import RelationExtractor
from engine.ontology import MythologicalOntology
from engine.schema import SCRAPE_SOURCES

def run_pipeline(use_network=True, max_scrape=25, output_dir=".", force_network=False):
    print("\n" + "="*60)
    print("  MYTHOLOGICAL ONTOLOGY ENGINE  v2.0")
    print("="*60)

    entities = []
    if use_network:
        try:
            scraper = MythologyScraper(output_dir=f"{output_dir}/data/raw")
            sources = [{**s,"max_items":min(s["max_items"],max_scrape)} for s in SCRAPE_SOURCES]
            entities = scraper.run(sources=sources, delay=0.4, force_network=force_network)
            if len(entities) < 10:
                print("\n  ⚠ Limited results from Wikipedia, supplementing with seed data...")
                names = {e["name"] for e in entities}
                entities += [e for e in SEED_ENTITIES if e["name"] not in names]
        except Exception as ex:
            print(f"\n  ✗ Scraping failed: {ex}\n  ↳ Using seed data")
            entities = []
            use_network = False

    if not use_network or not entities:
        print("\n[1/5]  Loading seed entities...")
        entities = list(SEED_ENTITIES)
        print(f"  ✓ {len(entities)} seed entities loaded")
    else:
        print("\n[1/5]  Entities from Wikipedia + seed")
        print(f"  ✓ {len(entities)} total entities")

    print("\n[2/5]  Classifying archetypes...")
    mapper = ArchetypeMapper()
    mapper.enrich_entities(entities)
    for arch, count in mapper.distribution(entities).items():
        if count:
            print(f"  {mapper.archetype_info(arch).get('emoji','▪')}  {arch}: {count}")

    print("\n[3/5]  Extracting relations...")
    extractor = RelationExtractor()
    extractor.extract_all(entities)
    Path(f"{output_dir}/data/relations").mkdir(parents=True, exist_ok=True)
    extractor.save(f"{output_dir}/data/relations/relations.json")

    print("\n[4/5]  Building knowledge graph...")
    onto = MythologicalOntology()
    for e in entities: onto.add_entity(e)
    onto.add_relations_bulk(extractor.to_records())

    print("\n[5/5]  Saving outputs...")
    for d in ["knowledge_graph","output","data/entities"]:
        Path(f"{output_dir}/{d}").mkdir(parents=True, exist_ok=True)

    with open(f"{output_dir}/data/entities/all_entities.json","w",encoding="utf-8") as f:
        json.dump(entities,f,indent=2,ensure_ascii=False)
    onto.save(f"{output_dir}/knowledge_graph/mythology_graph.json")
    with open(f"{output_dir}/output/graph_d3.json","w",encoding="utf-8") as f:
        json.dump(onto.to_d3(),f,indent=2,ensure_ascii=False)

    stats = onto.stats()
    print("\n" + "="*60)
    print("  BUILD COMPLETE")
    print("="*60)
    print(f"  Entities : {stats['nodes']}")
    print(f"  Relations: {stats['edges']}")
    print(f"  Density  : {stats['density']}")
    print(f"  Avg Deg  : {stats['avg_degree']}")
    print(f"\n  Top 5 by centrality:")
    for name, score in onto.top_nodes(5):
        pa = onto.graph.nodes[name].get("primary_archetype","?")
        from engine.schema import ARCHETYPES
        emoji = ARCHETYPES.get(pa,{}).get("emoji","▪")
        print(f"    {emoji} {name:<20} {pa} ({score:.3f})")
    return onto

if __name__ == "__main__":
    import sys
    force_network = "--force-network" in sys.argv or "--wikipedia" in sys.argv
    
    if force_network:
        print("  (Wikipedia scraping enabled)\n")
    else:
        from engine.scraper import check_network
        if not check_network():
            print("\n  ⚠ No network detected. Using seed data.")
            print("  → To enable Wikipedia scraping: python pipeline.py --force-network\n")
    
    onto = run_pipeline(use_network=True, max_scrape=25, force_network=force_network)
