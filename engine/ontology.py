"""Mythological Ontology Engine — Knowledge Graph"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx
from engine.schema import ARCHETYPES, PANTHEON_COLORS

class MythologicalOntology:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._entities: Dict[str, Dict] = {}

    def add_entity(self, entity: Dict):
        name = entity.get("name", "").strip()
        if not name or "[z]" in name.lower(): return
        self._entities[name] = entity
        self.graph.add_node(name,
            type=entity.get("type","unknown"),
            pantheon=entity.get("pantheon","Unknown"),
            description=entity.get("description","")[:300],
            archetypes=entity.get("archetypes",[]),
            primary_archetype=entity.get("primary_archetype",""),
            archetype_scores=entity.get("archetype_scores",{}),
            aliases=entity.get("aliases",[]),
        )

    def add_relation(self, source: str, relation: str, target: str, weight: int=1, category: str=""):
        for n in (source, target):
            if n not in self.graph:
                self.graph.add_node(n,type="unknown",pantheon="Unknown",description="",
                                    archetypes=[],primary_archetype="",archetype_scores={},aliases=[])
        self.graph.add_edge(source, target, relation=relation, weight=weight, category=category)

    def add_relations_bulk(self, records: List[Dict]):
        for r in records:
            self.add_relation(r["source"],r["relation"],r["target"],r.get("weight",1),r.get("category",""))

    def entity(self, name: str) -> Optional[Dict]: return self._entities.get(name)
    def entity_node(self, name: str) -> Optional[Dict]:
        return dict(self.graph.nodes[name]) if name in self.graph else None

    def get_relations(self, name: str, direction: str="both") -> List[Dict]:
        result = []
        if name not in self.graph: return result
        if direction in ("out","both"):
            for _,t,data in self.graph.out_edges(name,data=True):
                result.append({"source":name,"relation":data.get("relation"),"target":t,"direction":"out"})
        if direction in ("in","both"):
            for s,_,data in self.graph.in_edges(name,data=True):
                result.append({"source":s,"relation":data.get("relation"),"target":name,"direction":"in"})
        return result

    def get_neighborhood(self, name: str, depth: int=2) -> nx.MultiDiGraph:
        return nx.ego_graph(self.graph, name, radius=depth)

    def find_path(self, source: str, target: str) -> List[str]:
        try: return nx.shortest_path(self.graph.to_undirected(), source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound): return []

    def archetype_members(self, archetype: str) -> List[str]:
        return [n for n,d in self.graph.nodes(data=True) if archetype in d.get("archetypes",[])]

    def pantheon_members(self, pantheon: str) -> List[str]:
        return [n for n,d in self.graph.nodes(data=True) if d.get("pantheon")==pantheon]

    def search(self, query: str) -> List[str]:
        q = query.lower()
        return sorted([n for n,d in self.graph.nodes(data=True)
                       if q in n.lower() or q in d.get("description","").lower()])

    def centrality(self) -> Dict[str, float]:
        return nx.degree_centrality(self.graph.to_undirected())

    def top_nodes(self, n: int=10) -> List[Tuple[str, float]]:
        c = self.centrality()
        return sorted(c.items(), key=lambda x: x[1], reverse=True)[:n]

    def cross_archetype_bridges(self) -> List[Dict]:
        bridges = []
        for s,t,data in self.graph.edges(data=True):
            sa = self.graph.nodes[s].get("primary_archetype","")
            ta = self.graph.nodes[t].get("primary_archetype","")
            if sa and ta and sa != ta:
                bridges.append({"source":s,"source_arch":sa,"target":t,"target_arch":ta,"relation":data.get("relation")})
        return bridges

    def stats(self) -> Dict[str, Any]:
        g = self.graph
        return {
            "nodes": g.number_of_nodes(), "edges": g.number_of_edges(),
            "density": round(nx.density(g.to_undirected()),4),
            "components": nx.number_weakly_connected_components(g),
            "avg_degree": round(sum(d for _,d in g.to_undirected().degree())/max(g.number_of_nodes(),1),2),
        }

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = {"nodes":[(n,dict(d)) for n,d in self.graph.nodes(data=True)],
                "edges":[(s,t,dict(d)) for s,t,d in self.graph.edges(data=True)]}
        with open(path,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False)
        print(f"  ✓ Graph saved → {path}")

    def load(self, path: str):
        with open(path,"r",encoding="utf-8") as f: data = json.load(f)
        self.graph = nx.MultiDiGraph()
        for name,attrs in data["nodes"]: self.graph.add_node(name,**attrs)
        for s,t,attrs in data["edges"]: self.graph.add_edge(s,t,**attrs)

    def to_d3(self) -> Dict:
        arch_colors = {a: d["color"] for a,d in ARCHETYPES.items()}
        centrality = self.centrality()
        nodes = []
        for n,d in self.graph.nodes(data=True):
            pa = d.get("primary_archetype","")
            nodes.append({
                "id":n, "type":d.get("type","unknown"), "pantheon":d.get("pantheon","Unknown"),
                "primary_archetype":pa, "archetypes":d.get("archetypes",[]),
                "description":d.get("description","")[:200],
                "color":arch_colors.get(pa,"#95A5A6"),
                "pantheon_color":PANTHEON_COLORS.get(d.get("pantheon","Unknown"),"#95A5A6"),
                "size":max(8,min(28,8+centrality.get(n,0)*120)),
            })
        links = [{"source":s,"target":t,"relation":d.get("relation","unknown"),
                  "category":d.get("category",""),"weight":d.get("weight",1)}
                 for s,t,d in self.graph.edges(data=True)]
        return {"nodes":nodes,"links":links}
