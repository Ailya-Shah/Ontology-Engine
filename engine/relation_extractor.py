"""Mythological Ontology Engine — Relation Extractor"""
import re, json
from pathlib import Path
from typing import Dict, List, Tuple
from engine.schema import RELATION_PATTERNS, RELATION_TYPES

CURATED_RELATIONS: List[Tuple[str, str, str]] = [
    # Greek family tree
    ("Zeus","father_of","Athena"), ("Zeus","father_of","Apollo"), ("Zeus","father_of","Artemis"),
    ("Zeus","father_of","Ares"), ("Zeus","father_of","Hephaestus"), ("Zeus","father_of","Hermes"),
    ("Zeus","father_of","Dionysus"), ("Zeus","father_of","Perseus"), ("Zeus","father_of","Hercules"),
    ("Zeus","father_of","Persephone"), ("Zeus","married","Hera"),
    ("Hera","mother_of","Ares"), ("Hera","mother_of","Hephaestus"),
    ("Cronus","father_of","Zeus"), ("Cronus","father_of","Hera"), ("Cronus","father_of","Poseidon"),
    ("Cronus","father_of","Hades"), ("Cronus","father_of","Demeter"),
    ("Gaia","mother_of","Cronus"), ("Demeter","mother_of","Persephone"),
    ("Poseidon","father_of","Theseus"),
    # Greek conflict
    ("Perseus","killed","Medusa"), ("Theseus","defeated","Minotaur"),
    ("Hercules","fought","Hydra"), ("Hercules","defeated","Cerberus"),
    ("Odysseus","battled","Cyclops"), ("Apollo","killed","Python"),
    ("Zeus","defeated","Cronus"), ("Zeus","battled","Typhon"),
    # Greek roles
    ("Hades","rules_over","Underworld"), ("Poseidon","rules_over","Sea"),
    ("Zeus","rules_over","Sky"), ("Demeter","rules_over","Harvest"),
    ("Cerberus","guards","Underworld"), ("Hermes","guides","Dead"),
    ("Aphrodite","embodies","Love"), ("Athena","embodies","Wisdom"),
    ("Persephone","rules_over","Underworld"), ("Hades","married","Persephone"),
    ("Aphrodite","guides","Psyche"),
    # Norse
    ("Odin","father_of","Thor"), ("Odin","father_of","Loki"), ("Odin","father_of","Baldr"),
    ("Loki","father_of","Fenrir"), ("Loki","father_of","Hel"),
    ("Loki","killed","Baldr"), ("Thor","battled","Jormungandr"),
    ("Odin","rules_over","Asgard"), ("Freya","rules_over","Folkvangr"),
    # Egyptian
    ("Ra","rules_over","Sun"), ("Isis","mother_of","Horus"),
    ("Set","killed","Osiris"), ("Horus","defeated","Set"),
    # Celtic
    ("Lugh","killed","Balor"),
    # Archetype symbolism
    ("Hermes","symbolizes","Trickster"), ("Loki","symbolizes","Trickster"),
    ("Odin","symbolizes","Wise Old Man"), ("Zeus","symbolizes","Wise Old Man"),
    ("Hercules","symbolizes","The Hero"), ("Perseus","symbolizes","The Hero"),
    ("Gilgamesh","symbolizes","The Hero"), ("Achilles","symbolizes","The Hero"),
    ("Hades","symbolizes","The Shadow"), ("Set","symbolizes","The Shadow"),
    ("Gaia","symbolizes","Great Mother"), ("Demeter","symbolizes","Great Mother"),
    ("Isis","symbolizes","Great Mother"), ("Kali","symbolizes","Great Mother"),
    ("Persephone","symbolizes","Anima"), ("Psyche","symbolizes","Anima"),
    ("Dionysus","symbolizes","The Child"), ("Apollo","symbolizes","The Child"),
    ("Ra","symbolizes","The Self"), ("Vishnu","symbolizes","The Self"),
]

class RelationExtractor:
    def __init__(self, entity_names: List[str] = None):
        self.entity_names = set(entity_names or [])
        self.extracted: List[Tuple[str, str, str]] = []

    def extract_from_text(self, text: str) -> List[Tuple[str, str, str]]:
        found = []
        for pattern, rel_type in RELATION_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                groups = m.groups()
                if len(groups) == 2:
                    s, o = groups[0].strip(), groups[1].strip()
                    if self.entity_names and s not in self.entity_names and o not in self.entity_names:
                        continue
                    if s and o and s != o:
                        found.append((s, rel_type, o))
        return found

    def extract_all(self, entities: List[Dict]) -> List[Tuple[str, str, str]]:
        self.entity_names = {e["name"] for e in entities}
        self.extracted = list(CURATED_RELATIONS)
        for entity in entities:
            for rel in self.extract_from_text(entity.get("description", "")):
                if rel not in self.extracted:
                    self.extracted.append(rel)
        return self.extracted

    def to_records(self) -> List[Dict]:
        return [
            {"source": s, "relation": r, "target": t,
             "category": RELATION_TYPES.get(r, {}).get("category", "unknown"),
             "weight": RELATION_TYPES.get(r, {}).get("weight", 1)}
            for s, r, t in self.extracted
        ]

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_records(), f, indent=2)
        print(f"  ✓ Relations saved → {path}  ({len(self.extracted)} total)")
