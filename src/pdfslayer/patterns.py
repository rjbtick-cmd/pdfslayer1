"""Pattern and framework utilities.

The pattern graph is intentionally lightweight: patterns capture recurring
motifs, frameworks provide reusable scaffolding, and overlaps describe how
patterns or inference nodes align. The ``weave_theoretical_indexing`` helper
interleaves a theoretical indexing framework with an ``InferenceGraph`` to
surface where claims, assumptions, and implications land within the theory stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .inference import InferenceGraph, Node, NodeType


@dataclass
class Pattern:
    name: str
    description: str
    anchors: List[int] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "anchors": self.anchors,
            "metadata": self.metadata,
        }


@dataclass
class Framework:
    name: str
    steps: List[str]
    intent: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "steps": self.steps,
            "intent": self.intent,
            "metadata": self.metadata,
        }


@dataclass
class PatternGraph:
    patterns: List[Pattern] = field(default_factory=list)
    frameworks: List[Framework] = field(default_factory=list)
    overlaps: List[Dict[str, object]] = field(default_factory=list)

    def add_pattern(self, pattern: Pattern) -> Pattern:
        self.patterns.append(pattern)
        return pattern

    def add_framework(self, framework: Framework) -> Framework:
        self.frameworks.append(framework)
        return framework

    def to_dict(self) -> Dict[str, object]:
        return {
            "patterns": [pattern.to_dict() for pattern in self.patterns],
            "frameworks": [framework.to_dict() for framework in self.frameworks],
            "overlaps": self.overlaps,
        }


THEORETICAL_INDEXING_STEPS = [
    "Phenomena",
    "Constructs and definitions",
    "Hypotheses and propositions",
    "Evidence base",
    "Methods and measurements",
    "Implications and boundary conditions",
]


def weave_theoretical_indexing(graph: InferenceGraph) -> Dict[str, List[Node]]:
    """Attach inference nodes to the theoretical indexing scaffold.

    The returned mapping helps highlight where a given inference graph is dense
    (or sparse) along the research pipeline. The heuristic is keyword-driven to
    stay simple and auditable.
    """

    buckets: Dict[str, List[Node]] = {step: [] for step in THEORETICAL_INDEXING_STEPS}

    for node in graph.nodes:
        lower = node.content.lower()
        if node.kind is NodeType.CLAIM and any(word in lower for word in ["evidence", "dataset", "experiment"]):
            buckets["Evidence base"].append(node)
        elif node.kind is NodeType.CLAIM:
            buckets["Hypotheses and propositions"].append(node)
        elif node.kind is NodeType.ASSUMPTION:
            buckets["Constructs and definitions"].append(node)
        elif node.kind is NodeType.IMPLICATION:
            buckets["Implications and boundary conditions"].append(node)
        elif node.kind is NodeType.ANALOGY:
            buckets["Phenomena"].append(node)
        elif node.kind is NodeType.TENSION:
            buckets["Methods and measurements"].append(node)
        else:
            buckets["Phenomena"].append(node)

    return buckets


def build_theoretical_indexing_framework(intent: Optional[str] = None) -> Framework:
    return Framework(
        name="Theoretical indexing",
        steps=THEORETICAL_INDEXING_STEPS,
        intent=intent or "Map claims to their position in the theory-building pipeline.",
    )
