"""Mythological Ontology Engine — Scraper + Seed Dataset"""
import requests, json, time, re, socket
from pathlib import Path
from typing import Dict, List, Optional
from engine.schema import SCRAPE_SOURCES

def check_network(host="8.8.8.8", port=53, timeout=3):
    """Check if network is reachable."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect((host, port))
        return True
    except OSError:
        return False

class MythologyScraper:
    BASE = "https://en.wikipedia.org"
    def __init__(self, output_dir="data/raw"):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.entities: List[Dict] = []
        self._seen: set = set()
        self.cache_dir = self.output_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, url):
        """Generate cache file path for a URL."""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"

    def load_cache(self, url):
        """Load response from cache."""
        cache_file = self.get_cache_path(url)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_cache(self, url, data):
        """Save response to cache."""
        try:
            cache_file = self.get_cache_path(url)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except:
            pass

    def scrape_category(self, url, entity_type, pantheon="Unknown", max_items=30):
        print(f"  [{pantheon}] {entity_type} ← {url.split('/')[-1]}")
        
        # Try cache first
        cached = self.load_cache(url)
        if cached is not None:
            print(f"    ⟳ From cache: {len(cached)} stubs")
            return cached
        
        # Retry logic with backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                r = self.session.get(url, timeout=15)
                r.raise_for_status()
                links = re.findall(r'href="(/wiki/[^":]+)"[^>]*title="([^"]+)"', r.text)
                stubs, seen = [], set()
                for href, title in links:
                    if len(stubs) >= max_items: break
                    if href in self._seen or href in seen: continue
                    if any(x in href for x in ["Category:","Wikipedia:","Help:","File:","Template:"]): continue
                    if any(x in title for x in ["disambiguation","List of","Category:"]): continue
                    seen.add(href)
                    stubs.append({"name":title,"url":self.BASE+href,"type":entity_type,"pantheon":pantheon})
                print(f"    ✓ {len(stubs)} stubs")
                self.save_cache(url, stubs)
                return stubs
            except requests.exceptions.ConnectionError as e:
                wait = 2 ** attempt
                if attempt < max_retries - 1:
                    print(f"    ⟳ Retry {attempt + 1}/{max_retries} (wait {wait}s)...")
                    time.sleep(wait)
                else:
                    print(f"    ✗ Connection failed after {max_retries} retries")
                    return []
            except Exception as e:
                print(f"    ✗ {type(e).__name__}: {str(e)[:60]}")
                return []
        links = re.findall(r'href="(/wiki/[^":]+)"[^>]*title="([^"]+)"', r.text)
        stubs, seen = [], set()
        for href, title in links:
            if len(stubs) >= max_items: break
            if href in self._seen or href in seen: continue
            if any(x in href for x in ["Category:","Wikipedia:","Help:","File:","Template:"]): continue
            if any(x in title for x in ["disambiguation","List of","Category:"]): continue
            seen.add(href)
            stubs.append({"name":title,"url":self.BASE+href,"type":entity_type,"pantheon":pantheon})
        print(f"    ✓ {len(stubs)} stubs"); return stubs

    def scrape_entity(self, stub):
        url = stub["url"]
        if url in self._seen: return None
        self._seen.add(url)
        
        # Try cache first
        cache_data = self.load_cache(url)
        if cache_data is not None:
            return cache_data
        
        # Retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                r = self.session.get(url, timeout=15)
                r.raise_for_status()
                
                paras = re.findall(r'<p[^>]*>(.*?)</p>', r.text, re.DOTALL)
                description = ""
                for p in paras:
                    clean = re.sub(r'<[^>]+>','',p).strip()
                    clean = re.sub(r'\[[\d]+\]','',clean)
                    clean = re.sub(r'\s+',' ',clean)
                    if len(clean) > 80: description = clean[:600]; break
                infobox = {}
                ib = re.search(r'<table[^>]*infobox[^>]*>(.*?)</table>', r.text, re.DOTALL|re.IGNORECASE)
                if ib:
                    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', ib.group(1), re.DOTALL):
                        th = re.search(r'<th[^>]*>(.*?)</th>', row, re.DOTALL)
                        td = re.search(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                        if th and td:
                            k = re.sub(r'<[^>]+>','',th.group(1)).strip()
                            v = re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',td.group(1))).strip()
                            if k and v and len(k)<60: infobox[k]=v[:200]
                aliases = []
                m = re.search(r'also known as ([^.]+)\.', description, re.IGNORECASE)
                if m:
                    aliases = [a.strip().strip('"') for a in re.split(r',|and', m.group(1)) if len(a.strip())>1]
                
                entity = {**stub,"description":description,"infobox":infobox,"aliases":aliases,"archetypes":[],"archetype_scores":{}}
                self.save_cache(url, entity)
                return entity
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except Exception:
                return None

    def run(self, sources=None, delay=0.2, force_network=False, max_entities=60):
        if sources is None: sources = SCRAPE_SOURCES
        
        # Check network availability
        has_network = check_network()
        print(f"\n--- Network: {'OK' if has_network else 'UNAVAILABLE'} ---")
        
        if not has_network and not force_network:
            print("  ! Skipping Wikipedia scrape (use force_network=True to retry)")
            return []
        
        print("--- Collecting stubs ---")
        stubs = []
        for src in sources:
            result = self.scrape_category(src["url"],src["entity_type"],src.get("pantheon","Unknown"),src.get("max_items",30))
            stubs += result
            time.sleep(delay)
        
        seen, unique = set(), []
        for s in stubs:
            if s["url"] not in seen: seen.add(s["url"]); unique.append(s)
        print(f"\n  {len(unique)} unique stubs (limiting to {max_entities} for performance)")
        unique = unique[:max_entities]  # Limit for performance
        
        print(f"\n--- Fetching details (1/{len(unique)}) ---")
        self.entities = []
        for idx, stub in enumerate(unique, 1):
            e = self.scrape_entity(stub)
            if e and e.get("description"): self.entities.append(e)
            if idx % 10 == 0:
                print(f"  ✓ {len(self.entities)}/{idx} processed")
            time.sleep(delay)
        print(f"\n  ✓ {len(self.entities)} entities with descriptions")
        out = self.output_dir / "entities_raw.json"
        with open(out,"w",encoding="utf-8") as f: json.dump(self.entities,f,indent=2,ensure_ascii=False)
        print(f"  ✓ Saved → {out}")
        return self.entities

SEED_ENTITIES = [
    {"name":"Zeus","type":"deities","pantheon":"Greek","description":"Zeus is the god of the sky and thunder in ancient Greek religion, who rules as king of the gods on Mount Olympus. He is the child of the Titans Cronus and Rhea, the youngest of his siblings. In most traditions he is married to Hera, by whom he is usually said to have fathered Ares, Hebe, and Hephaestus. He is known for his wisdom, authority, and divine justice. His symbol is the thunderbolt.","infobox":{"Abode":"Mount Olympus","Symbol":"Thunderbolt, eagle, oak, bull"},"aliases":["Jupiter","Jove"],"archetypes":[],"archetype_scores":{}},
    {"name":"Hera","type":"deities","pantheon":"Greek","description":"Hera is the goddess of marriage, women, childbirth, and family in ancient Greek religion. She is daughter of the Titans Cronus and Rhea. She is the wife and one of three sisters of Zeus, and thus queen of the Olympian gods. Her chief function in myth is as the jealous and vengeful wife of Zeus.","infobox":{"Abode":"Mount Olympus","Symbol":"Peacock, cuckoo, pomegranate, cow"},"aliases":["Juno"],"archetypes":[],"archetype_scores":{}},
    {"name":"Athena","type":"deities","pantheon":"Greek","description":"Athena is the goddess of wisdom, warfare, and craftsmanship in ancient Greek religion. She is a virgin deity and the patron goddess of Athens. Born from the head of her father Zeus, fully grown and armored, she embodies strategic wisdom over brute strength.","infobox":{"Abode":"Mount Olympus","Symbol":"Owl, olive tree, snake, armor, spear"},"aliases":["Minerva","Pallas Athena"],"archetypes":[],"archetype_scores":{}},
    {"name":"Poseidon","type":"deities","pantheon":"Greek","description":"Poseidon is one of the Twelve Olympians in ancient Greek religion, god of the sea, storms, earthquakes, and horses. He was also called Earth-Shaker due to his role in causing earthquakes. He is a son of the Titans Cronus and Rhea, and brother to Zeus and Hades.","infobox":{"Abode":"Mount Olympus or Sea","Symbol":"Trident, horse, bull, dolphin"},"aliases":["Neptune"],"archetypes":[],"archetype_scores":{}},
    {"name":"Hades","type":"deities","pantheon":"Greek","description":"Hades was the god of the dead and king of the underworld in ancient Greek religion. He was the eldest son of Cronus and Rhea, and brother of Zeus and Poseidon. He ruled the realm of the dead and the shadow world with dark authority. His domain represents death, inevitability, and the hidden unconscious.","infobox":{"Abode":"The Underworld","Symbol":"Cerberus, helm of darkness, bident"},"aliases":["Pluto","Dis Pater"],"archetypes":[],"archetype_scores":{}},
    {"name":"Hermes","type":"deities","pantheon":"Greek","description":"Hermes is an Olympian deity considered the herald of the gods, protector of travelers, thieves, merchants, and orators. He moves freely between the worlds of mortal and divine, and is believed to bring dreams to mortals. He is cunning, clever, and a trickster who crosses all boundaries.","infobox":{"Abode":"Mount Olympus","Symbol":"Caduceus, winged sandals, herald's staff, tortoise"},"aliases":["Mercury"],"archetypes":[],"archetype_scores":{}},
    {"name":"Apollo","type":"deities","pantheon":"Greek","description":"Apollo is one of the Olympian deities, god of the sun, light, music, poetry, art, prophecy, truth, archery, plague, and healing. He is the son of Zeus and Leto, and has a twin sister, Artemis. Born young and radiant, he is both destroyer and healer, a child of divine power.","infobox":{"Abode":"Mount Olympus or Delphi","Symbol":"Lyre, laurel wreath, raven, bow and arrow, sun"},"aliases":["Phoebus"],"archetypes":[],"archetype_scores":{}},
    {"name":"Artemis","type":"deities","pantheon":"Greek","description":"Artemis is the goddess of the hunt, wilderness, animals, the Moon, and chastity. She hunts with silver arrows and is accompanied by hunting dogs. As goddess of the Moon she rules the night, the wild, and the liminal spaces between civilization and nature.","infobox":{"Abode":"Mount Olympus or the wilderness","Symbol":"Moon, bow and arrow, hunting dog, deer"},"aliases":["Diana"],"archetypes":[],"archetype_scores":{}},
    {"name":"Aphrodite","type":"deities","pantheon":"Greek","description":"Aphrodite is an ancient Greek goddess associated with love, lust, pleasure, passion, procreation, and beauty. She was born from sea-foam near Paphos, Cyprus, emerging fully formed from the waves. She embodies the animating soul of love and desire that drives all creation.","infobox":{"Abode":"Mount Olympus","Symbol":"Dove, myrtle, apple, rose, swan, sparrow"},"aliases":["Venus","Cytherea"],"archetypes":[],"archetype_scores":{}},
    {"name":"Dionysus","type":"deities","pantheon":"Greek","description":"Dionysus is the god of the grape harvest, winemaking, fertility, insanity, ritual madness, religious ecstasy, festivity, and theatre. Born twice — first from Semele, then from Zeus's thigh — he is the eternal divine child of transformation, ecstasy, and dissolution of ego boundaries.","infobox":{"Abode":"Mount Olympus","Symbol":"Thyrsus, grapevine, bull, panther, ivy"},"aliases":["Bacchus","Liber"],"archetypes":[],"archetype_scores":{}},
    {"name":"Ares","type":"deities","pantheon":"Greek","description":"Ares is the Greek god of war, courage, and violence. He is one of the Twelve Olympians, the son of Zeus and Hera. He represents the physical, violent, and untamed aspect of war — pure martial fury rather than strategy.","infobox":{"Abode":"Mount Olympus or Thrace","Symbol":"Spear, helmet, dog, vulture, pig"},"aliases":["Mars"],"archetypes":[],"archetype_scores":{}},
    {"name":"Hephaestus","type":"deities","pantheon":"Greek","description":"Hephaestus is the god of fire, metalworking, stone masonry, forges, the art of sculpture, technology, and blacksmiths. He was cast off Olympus by his mother Hera due to his deformity. The divine craftsman who creates the tools and weapons of the gods.","infobox":{"Abode":"Mount Olympus or Lemnos","Symbol":"Hammer, anvil, tongs, fire"},"aliases":["Vulcan"],"archetypes":[],"archetype_scores":{}},
    {"name":"Persephone","type":"deities","pantheon":"Greek","description":"Persephone is the queen of the underworld and goddess of spring growth. She is the daughter of Zeus and the harvest goddess Demeter. Her abduction by Hades and time spent in the underworld represents the soul's descent into darkness, the death of innocence, and rebirth.","infobox":{"Abode":"The Underworld (part-time), Mount Olympus","Symbol":"Pomegranate, torch, grain, deer, flowers"},"aliases":["Proserpina","Kore"],"archetypes":[],"archetype_scores":{}},
    {"name":"Demeter","type":"deities","pantheon":"Greek","description":"Demeter is the goddess of the harvest and agriculture, presiding over grains and the fertility of the earth. She is a daughter of Cronus and Rhea. She searched desperately for her daughter Persephone who was abducted by Hades, causing the earth to wither during her grief.","infobox":{"Abode":"Mount Olympus","Symbol":"Cornucopia, wheat, torch, poppy"},"aliases":["Ceres"],"archetypes":[],"archetype_scores":{}},
    {"name":"Gaia","type":"deities","pantheon":"Greek","description":"Gaia is the personification of the Earth and one of the Greek primordial deities. She is the ancestral mother of all life: the primal Mother Earth goddess. She is the immediate parent of Uranus, from whose union she bore the Titans, the Cyclopes, and the Giants.","infobox":{"Abode":"Earth itself","Symbol":"Earth, serpents, animals, fruit"},"aliases":["Terra","Ge"],"archetypes":[],"archetype_scores":{}},
    {"name":"Hercules","type":"heroes","pantheon":"Greek","description":"Hercules is a Roman hero and god, the equivalent of the Greek divine hero Heracles. He was the son of the god Jupiter and the mortal Alcmene. He was famed for his strength and his twelve labors — impossible tasks imposed by King Eurystheus — which represent the hero's transformative journey through trials.","infobox":{"Father":"Zeus/Jupiter","Symbol":"Club, lion skin, bow and arrows"},"aliases":["Heracles","Alcides"],"archetypes":[],"archetype_scores":{}},
    {"name":"Perseus","type":"heroes","pantheon":"Greek","description":"Perseus is the legendary founder of Mycenae and the Perseid dynasty, son of Zeus and the mortal Danae. His heroic deeds include killing the Gorgon Medusa, rescuing Andromeda from a sea monster, and using the severed head of Medusa as a weapon. He is a quintessential champion who defeats the monstrous.","infobox":{"Father":"Zeus","Symbol":"Winged sandals, cap of invisibility, harpe"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Theseus","type":"heroes","pantheon":"Greek","description":"Theseus was the legendary hero of Athens, known for killing the Minotaur imprisoned in the Labyrinth of Crete. The son of Aegeus, King of Athens. With Ariadne's thread he navigated the maze, slew the monster within, and returned as a champion. He embodies the hero who brings order to chaos.","infobox":{"Father":"Aegeus (or Poseidon)","Symbol":"Sword, sandals, olive branch"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Achilles","type":"heroes","pantheon":"Greek","description":"Achilles is a hero of the Trojan War and the central character of Homer's Iliad, the greatest warrior of all the Greeks. The son of Nereid Thetis and Peleus, he was dipped in the River Styx as an infant to make him invulnerable except for his heel. He embodies glorious warrior heroism and tragic fate.","infobox":{"Father":"Peleus","Symbol":"Armor, spear, shield"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Odysseus","type":"heroes","pantheon":"Greek","description":"Odysseus is the legendary Greek king of Ithaca and hero of Homer's Odyssey. Famous for his intellectual brilliance, guile, and versatility — the hero of the mind rather than brute strength. His ten-year journey home embodies the transformative power of the quest and the cunning hero's triumph.","infobox":{"Father":"Laertes","Symbol":"Bow, ship, olive tree"},"aliases":["Ulysses"],"archetypes":[],"archetype_scores":{}},
    {"name":"Odin","type":"deities","pantheon":"Norse","description":"Odin is the chief god in Germanic paganism, the Allfather. He gave his eye to Mimir to gain wisdom, and hung himself on the world tree Yggdrasil for nine days to discover the runes. He is associated with wisdom, healing, death, royalty, knowledge, war, poetry, and magic. The supreme wise old sage of Norse myth.","infobox":{"Abode":"Asgard, Valhalla","Symbol":"Spear Gungnir, ravens Huginn and Muninn, wolves"},"aliases":["Woden","Wotan","Allfather"],"archetypes":[],"archetype_scores":{}},
    {"name":"Thor","type":"deities","pantheon":"Norse","description":"Thor is the son of Odin, associated with strength, storms, thunder, lightning, and the protection of mankind. His hammer Mjolnir is his iconic weapon. He is depicted as a red-bearded warrior riding a chariot pulled by two goats. He is the great defender and champion of Asgard against the giants.","infobox":{"Father":"Odin","Symbol":"Mjolnir, lightning bolt, oak tree"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Loki","type":"deities","pantheon":"Norse","description":"Loki is a shape-shifter and trickster god in Norse mythology. He appears in the form of a salmon, a mare, a fly, and an elderly woman. He is cunning and clever, causing mischief. He orchestrated the death of the beloved Baldr and was bound in chains as punishment, awaiting Ragnarok.","infobox":{"Abode":"Asgard (formerly)","Symbol":"Serpent, net, fire"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Freya","type":"deities","pantheon":"Norse","description":"Freya is a goddess associated with love, beauty, fertility, sex, war, gold, and seidr magic in Norse mythology. She owns the necklace Brisingamen, rides a chariot pulled by two cats, and possesses a cloak of falcon feathers. She is a leader of the Valkyries and receives half of those slain in battle.","infobox":{"Abode":"Folkvangr","Symbol":"Falcon feather cloak, Brisingamen necklace, cats"},"aliases":["Freyja"],"archetypes":[],"archetype_scores":{}},
    {"name":"Ra","type":"deities","pantheon":"Egyptian","description":"Ra or Re was the ancient Egyptian deity of the Sun. By the Fifth Dynasty he had become one of the most important gods in ancient Egyptian religion. Ra was believed to rule in all parts of the created world — the sky, the earth, and the underworld. He represents the totality of divine cosmic order and self.","infobox":{"Abode":"Solar barque","Symbol":"Sun disk, falcon head, ankh, was sceptre"},"aliases":["Re","Amun-Ra"],"archetypes":[],"archetype_scores":{}},
    {"name":"Isis","type":"deities","pantheon":"Egyptian","description":"Isis is a major goddess in ancient Egyptian religion whose worship spread throughout the Greco-Roman world. She was revered as the ideal mother and wife, and as the patroness of nature and magic. She reassembled the body of Osiris and brought him back to life, embodying the nurturing Great Mother.","infobox":{"Abode":"Egypt","Symbol":"Throne, ankh, falcon wings, stars"},"aliases":["Aset"],"archetypes":[],"archetype_scores":{}},
    {"name":"Medusa","type":"monsters","pantheon":"Greek","description":"Medusa was one of the three Gorgons in Greek mythology, a chthonic monster with living venomous snakes in place of hair. Gazing directly upon her would turn onlookers to stone. She was killed by Perseus, who used her severed head as a weapon — the shadow enemy the hero must face and overcome.","infobox":{"Type":"Gorgon","Symbol":"Snake hair, petrifying gaze"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Cerberus","type":"monsters","pantheon":"Greek","description":"Cerberus is a multi-headed dog in Greek and Roman mythology that guards the gates of the Underworld to prevent the dead from leaving. He was the offspring of the monsters Typhon and Echidna. He typically has three heads, a serpent for a tail, and snakes protruding from his body.","infobox":{"Father":"Typhon","Symbol":"Three heads, serpent tail"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Psyche","type":"heroes","pantheon":"Greek","description":"Psyche is a mortal woman whose great beauty caused Venus to become jealous of her. The tale of Cupid and Psyche describes the overcoming of obstacles placed in the way of love. She completed seemingly impossible tasks to be reunited with Eros, eventually becoming immortal — the human soul's journey toward the divine.","infobox":{"Symbol":"Butterfly, soul, wings"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Gilgamesh","type":"heroes","pantheon":"Sumerian","description":"Gilgamesh is the legendary hero and main character of the Epic of Gilgamesh, often regarded as the earliest great work of literature. He was likely a historical king of Uruk. After the death of his companion Enkidu, he journeys to find immortality, confronting mortality and the limits of the heroic will.","infobox":{"Symbol":"Lion, bull, tree of life"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Lugh","type":"deities","pantheon":"Celtic","description":"Lugh is a god in Irish mythology associated with craftsmanship, skill, the sun, and harvest. He is a member of the Tuatha De Danann and is known as the Long-Armed. He slew his grandfather Balor of the Evil Eye in battle, fulfilling a prophecy and becoming one of the great champion gods of the Celts.","infobox":{"Symbol":"Spear, sun, crow"},"aliases":["Lugus","Lleu"],"archetypes":[],"archetype_scores":{}},
    {"name":"Kali","type":"deities","pantheon":"Hindu","description":"Kali is the Hindu goddess associated with empowerment, time, death, violence, and doomsday. She is the fierce manifestation of the divine feminine, Shakti. She is dark, terrifying, and dancing on the body of Shiva — the destroyer of evil but also the mother who devours illusion and fear.","infobox":{"Symbol":"Skull necklace, sword, severed head"},"aliases":[],"archetypes":[],"archetype_scores":{}},
    {"name":"Vishnu","type":"deities","pantheon":"Hindu","description":"Vishnu is one of the principal deities of Hinduism, and the Supreme Being in Vaishnavism. He is the preserver and protector of the universe in the Hindu Trimurti alongside Brahma the creator and Shiva the destroyer. He maintains the cosmic order and is the totality of divine existence.","infobox":{"Symbol":"Lotus, chakra, conch, mace"},"aliases":["Narayana","Hari"],"archetypes":[],"archetype_scores":{}},
]
