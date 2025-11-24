"""Inference graph primitives.

This module provides a small, JSON-friendly graph structure for reasoning
about claims. It stays deliberately lightweight so it can be embedded in
LLM-oriented workflows or exported alongside pattern graphs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class NodeType(str, Enum):
    CLAIM = "claim"
    ASSUMPTION = "assumption"
    IMPLICATION = "implication"
    ANALOGY = "analogy"
    TENSION = "tension"
    OPEN_QUESTION = "openQuestion"


class EdgeType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFINES = "refines"
    PARALLELS = "parallels"
    GENERALIZES = "generalizes"
    BRIDGE = "bridge"


@dataclass
class Node:
    id: int
    kind: NodeType
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "content": self.content,
            "metadata": self.metadata,
        }


@dataclass
class Edge:
    id: int
    src: int
    dst: int
    kind: EdgeType
    rationale: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "src": self.src,
            "dst": self.dst,
            "kind": self.kind.value,
            "rationale": self.rationale,
        }


class InferenceGraph:
    """A small directed multigraph with typed nodes and edges."""

    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self._next_node_id = 1
        self._next_edge_id = 1

    def add_node(self, kind: NodeType, content: str, metadata: Optional[Dict[str, str]] = None) -> Node:
        node = Node(id=self._next_node_id, kind=kind, content=content, metadata=metadata or {})
        self.nodes.append(node)
        self._next_node_id += 1
        return node

    def add_edge(
        self,
        src: int,
        dst: int,
        kind: EdgeType,
        rationale: Optional[str] = None,
    ) -> Edge:
        edge = Edge(id=self._next_edge_id, src=src, dst=dst, kind=kind, rationale=rationale)
        self.edges.append(edge)
        self._next_edge_id += 1
        return edge

    def to_dict(self) -> Dict[str, object]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    def summarize(self) -> str:
        counts: Dict[NodeType, int] = {}
        for node in self.nodes:
            counts[node.kind] = counts.get(node.kind, 0) + 1
        parts = [f"{kind.value}:{counts.get(kind,0)}" for kind in NodeType]
        return "InferenceGraph(" + ", ".join(parts) + ")"
