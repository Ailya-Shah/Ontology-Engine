"""Mythological Ontology Engine — Schema & Constants"""
from typing import Dict, List

ENTITY_TYPES = {
    "DEITY": "Gods and goddesses across all pantheons",
    "HERO": "Mortal or semi-divine heroes on quests",
    "MONSTER": "Creatures, beasts, and adversaries",
    "SYMBOL": "Archetypal objects and motifs",
    "STORY": "Mythological narratives and cycles",
    "ARCHETYPE": "Jungian psychological archetypes",
    "CONCEPT": "Abstract mythological concepts",
}

ARCHETYPES: Dict[str, Dict] = {
    "The Hero": {
        "description": "The champion who undertakes a transformative journey, faces trials, and returns changed.",
        "shadow": "The Destroyer",
        "keywords": ["hero","champion","savior","quest","labors","journey","warrior","courage","trial","strength","valor","glory","noble"],
        "entities": ["Hercules","Perseus","Theseus","Gilgamesh","Achilles","Beowulf","Rama","Cu Chulainn","Odysseus","Jason","Siegfried","Arthur","Arjuna"],
        "symbols": ["sword","shield","armor","crown","laurel"],
        "color": "#E8593C", "emoji": "⚔️",
    },
    "The Shadow": {
        "description": "The dark mirror — repressed forces, chaos, and death that give the hero meaning.",
        "shadow": "The Hero",
        "keywords": ["dark","underworld","death","chaos","fear","abyss","void","dread","shadow","night","doom","destruction"],
        "entities": ["Hades","Loki","Set","Chernobog","Apep","Fenrir","Typhon","Erebus","Nyx","Thanatos","Pluto","Hel"],
        "symbols": ["darkness","serpent","abyss","void","night"],
        "color": "#6B7280", "emoji": "🌑",
    },
    "The Wise Old Man": {
        "description": "The sage who holds ancient knowledge and guides the seeker with wisdom.",
        "shadow": "The Trickster",
        "keywords": ["wisdom","teacher","guide","elder","knowledge","counselor","sage","oracle","prophet","mentor","ancient","divine"],
        "entities": ["Zeus","Odin","Chiron","Merlin","Tiresias","Nestor","Brahma","Ra","Thoth","Mimir","Enlil"],
        "symbols": ["staff","scroll","lightning","eye","mountain"],
        "color": "#4ECDC4", "emoji": "🦉",
    },
    "The Great Mother": {
        "description": "The primal feminine — creator and destroyer, nurturer and devourer.",
        "shadow": "The Terrible Mother",
        "keywords": ["mother","earth","fertility","nurture","creation","birth","harvest","womb","nature","abundance","life","goddess"],
        "entities": ["Gaia","Demeter","Rhea","Isis","Kali","Cybele","Nut","Frigg","Parvati","Coatlicue","Inanna","Tiamat"],
        "symbols": ["earth","moon","grain","spiral","serpent"],
        "color": "#96CEB4", "emoji": "🌙",
    },
    "The Trickster": {
        "description": "The boundary-crosser who subverts order, reveals truth through deception.",
        "shadow": "The Wise Old Man",
        "keywords": ["trick","deceive","shape-shift","clever","thief","cunning","paradox","chaos","wit","mischief","liminal","transgress"],
        "entities": ["Hermes","Loki","Coyote","Anansi","Eris","Kokopelli","Puck","Raven","Eshu","Narada","Pan","Dionysus"],
        "symbols": ["mask","wand","crossroads","fire","coin"],
        "color": "#F7DC6F", "emoji": "🎭",
    },
    "The Anima": {
        "description": "The inner soul-image — the feminine within, mystery, beauty, and yearning.",
        "shadow": "The Femme Fatale",
        "keywords": ["soul","inner","feminine","spirit","dream","beloved","muse","mystery","beauty","yearning","eternal","sacred"],
        "entities": ["Persephone","Psyche","Eurydice","Kore","Aphrodite","Helen","Ariadne","Selene","Eos","Circe"],
        "symbols": ["mirror","butterfly","veil","rose","moon"],
        "color": "#DDA0DD", "emoji": "🦋",
    },
    "The Child": {
        "description": "Innocence and potential — the divine child who signals transformation and new beginning.",
        "shadow": "The Orphan",
        "keywords": ["child","infant","born","young","innocent","new","dawn","spring","seed","pure","divine","origin","nascent"],
        "entities": ["Dionysus","Horus","Apollo","Hermes","Eros","Krishna","Romulus","Remus","Lugh","Maui","Quetzalcoatl"],
        "symbols": ["cradle","sun","egg","spring","seed"],
        "color": "#87CEEB", "emoji": "🌅",
    },
    "The Self": {
        "description": "The totality of the psyche — unity of conscious and unconscious, the cosmic whole.",
        "shadow": None,
        "keywords": ["cosmic","universe","unity","all","infinite","eternal","totality","absolute","logos","divine","ultimate"],
        "entities": ["Ra","Brahman","Vishnu","Zeus","El","Ahura Mazda","Atum","Marduk","Wakan Tanka","Tengri"],
        "symbols": ["sun","mandala","ouroboros","axis mundi","tree of life"],
        "color": "#FFD700", "emoji": "☀️",
    },
}

RELATION_TYPES = {
    "father_of":   {"label":"father of",   "category":"family",   "weight":3},
    "mother_of":   {"label":"mother of",   "category":"family",   "weight":3},
    "son_of":      {"label":"son of",      "category":"family",   "weight":3},
    "daughter_of": {"label":"daughter of", "category":"family",   "weight":3},
    "sibling_of":  {"label":"sibling of",  "category":"family",   "weight":2},
    "married":     {"label":"married",     "category":"family",   "weight":2},
    "fought":      {"label":"fought",      "category":"conflict", "weight":2},
    "killed":      {"label":"killed",      "category":"conflict", "weight":3},
    "battled":     {"label":"battled",     "category":"conflict", "weight":2},
    "defeated":    {"label":"defeated",    "category":"conflict", "weight":2},
    "created":     {"label":"created",     "category":"creation", "weight":2},
    "rules_over":  {"label":"rules over",  "category":"role",     "weight":2},
    "guards":      {"label":"guards",      "category":"role",     "weight":1},
    "guides":      {"label":"guides",      "category":"role",     "weight":1},
    "transformed": {"label":"transformed", "category":"role",     "weight":1},
    "symbolizes":  {"label":"symbolizes",  "category":"symbolic", "weight":1},
    "represents":  {"label":"represents",  "category":"symbolic", "weight":1},
    "embodies":    {"label":"embodies",    "category":"symbolic", "weight":2},
}

SCRAPE_SOURCES = [
    {"url":"https://en.wikipedia.org/wiki/Category:Greek_gods",                "entity_type":"deities", "pantheon":"Greek",    "max_items":40},
    {"url":"https://en.wikipedia.org/wiki/Category:Greek_mythological_heroes", "entity_type":"heroes",  "pantheon":"Greek",    "max_items":30},
    {"url":"https://en.wikipedia.org/wiki/Category:Greek_mythological_creatures","entity_type":"monsters","pantheon":"Greek",  "max_items":25},
    {"url":"https://en.wikipedia.org/wiki/Category:Norse_gods",                "entity_type":"deities", "pantheon":"Norse",    "max_items":30},
    {"url":"https://en.wikipedia.org/wiki/Category:Norse_mythology",           "entity_type":"stories", "pantheon":"Norse",    "max_items":20},
    {"url":"https://en.wikipedia.org/wiki/Category:Egyptian_gods",             "entity_type":"deities", "pantheon":"Egyptian", "max_items":25},
    {"url":"https://en.wikipedia.org/wiki/Category:Hindu_gods",                "entity_type":"deities", "pantheon":"Hindu",    "max_items":25},
]

RELATION_PATTERNS = [
    (r'\b(\w+)\s+is the son of\s+(\w+)',      "son_of"),
    (r'\b(\w+)\s+is the daughter of\s+(\w+)', "daughter_of"),
    (r'\b(\w+)\s+is the father of\s+(\w+)',   "father_of"),
    (r'\b(\w+)\s+is the mother of\s+(\w+)',   "mother_of"),
    (r'\b(\w+)\s+fought\s+(\w+)',              "fought"),
    (r'\b(\w+)\s+killed\s+(\w+)',              "killed"),
    (r'\b(\w+)\s+defeated\s+(\w+)',            "defeated"),
    (r'\b(\w+)\s+battled\s+(\w+)',             "battled"),
    (r'\b(\w+)\s+married\s+(\w+)',             "married"),
    (r'\b(\w+)\s+created\s+(\w+)',             "created"),
    (r'\b(\w+)\s+rules over\s+(\w+)',          "rules_over"),
    (r'\b(\w+)\s+guards\s+(\w+)',              "guards"),
    (r'\b(\w+)\s+transformed\s+(\w+)',         "transformed"),
]

PANTHEON_COLORS = {
    "Greek":    "#4A90D9",
    "Norse":    "#7B68EE",
    "Egyptian": "#F5A623",
    "Hindu":    "#E8593C",
    "Celtic":   "#50C878",
    "Sumerian": "#D4A017",
    "Roman":    "#C0C0C0",
    "Unknown":  "#95A5A6",
}
