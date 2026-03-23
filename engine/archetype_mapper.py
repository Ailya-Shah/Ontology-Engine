"""Mythological Ontology Engine — Archetype Mapper"""
from typing import Dict, List
from engine.schema import ARCHETYPES

class ArchetypeMapper:
    def __init__(self):
        self.archetypes = ARCHETYPES
        self._name_to_archetypes: Dict[str, List[str]] = {}
        for archetype, data in self.archetypes.items():
            for entity in data["entities"]:
                self._name_to_archetypes.setdefault(entity, []).append(archetype)

    def score_entity(self, name: str, description: str = "", infobox: Dict = None) -> Dict[str, float]:
        infobox = infobox or {}
        scores: Dict[str, float] = {a: 0.0 for a in self.archetypes}
        if name in self._name_to_archetypes:
            for arch in self._name_to_archetypes[name]:
                scores[arch] += 3.0
        desc_lower = description.lower()
        for archetype, data in self.archetypes.items():
            for keyword in data["keywords"]:
                count = desc_lower.count(keyword.lower())
                if count: scores[archetype] += min(count * 0.4, 1.2)
        ib_text = " ".join(str(v) for v in infobox.values()).lower()
        for archetype, data in self.archetypes.items():
            for keyword in data["keywords"]:
                if keyword.lower() in ib_text: scores[archetype] += 0.3
        for archetype, data in self.archetypes.items():
            for known in data["entities"]:
                if known.lower() in desc_lower: scores[archetype] += 0.5
        total = sum(scores.values()) or 1.0
        return {a: round(s / total, 4) for a, s in scores.items()}

    def classify(self, name: str, description: str = "", infobox: Dict = None, threshold: float = 0.08) -> List[str]:
        scores = self.score_entity(name, description, infobox)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [a for a, s in ranked if s >= threshold]

    def primary_archetype(self, name: str, description: str = "", infobox: Dict = None) -> str:
        scores = self.score_entity(name, description, infobox)
        return max(scores, key=lambda a: scores[a])

    def enrich_entities(self, entities: List[Dict]) -> List[Dict]:
        for entity in entities:
            name = entity.get("name", "")
            desc = entity.get("description", "")
            ib   = entity.get("infobox", {})
            entity["archetype_scores"]   = self.score_entity(name, desc, ib)
            entity["archetypes"]         = self.classify(name, desc, ib)
            entity["primary_archetype"]  = self.primary_archetype(name, desc, ib)
        return entities

    def archetype_entities(self, archetype: str, entities: List[Dict]) -> List[Dict]:
        return [e for e in entities if archetype in e.get("archetypes", [])]

    def distribution(self, entities: List[Dict]) -> Dict[str, int]:
        counts: Dict[str, int] = {a: 0 for a in self.archetypes}
        for e in entities:
            for a in e.get("archetypes", []):
                if a in counts: counts[a] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def archetype_info(self, archetype: str) -> Dict:
        return self.archetypes.get(archetype, {})
