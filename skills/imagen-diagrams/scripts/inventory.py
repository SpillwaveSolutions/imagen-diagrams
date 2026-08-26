#!/usr/bin/env python3
"""Parse Mermaid and PlantUML into a node/edge inventory."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

DiagramKind = Literal[
    "flowchart", "sequence", "class", "state", "activity", "c4", "other"
]
Language = Literal["mermaid", "plantuml", "unknown"]

KIND_FROM_HEADER: list[tuple[re.Pattern[str], DiagramKind]] = [
    (re.compile(r"sequenceDiagram|@startsequence|\bsequence\b", re.I), "sequence"),
    (re.compile(r"@startuml[\s\S]*\b(actor|participant)\b", re.I), "sequence"),
    (re.compile(r"stateDiagram|@startstate", re.I), "state"),
    (re.compile(r"classDiagram|@startclass", re.I), "class"),
    (re.compile(r"C4Context|C4Container|C4Component", re.I), "c4"),
    (re.compile(r"flowchart|graph\s+(TB|BT|LR|RL|TD)", re.I), "flowchart"),
    (re.compile(r"activityDiagram|@startuml[\s\S]*\nstart\b", re.I), "activity"),
]


@dataclass
class NodeRecord:
    id: str
    label: str


@dataclass
class EdgeRecord:
    frm: str
    to: str
    label: str | None = None


@dataclass
class Inventory:
    kind: DiagramKind
    language: Language
    nodes: list[NodeRecord] = field(default_factory=list)
    edges: list[EdgeRecord] = field(default_factory=list)
    salt: bool = False

    def labels(self) -> list[str]:
        return [n.label for n in self.nodes]


def unquote(s: str) -> str:
    return re.sub(r"^[\s\"'`\[{(\(<]+|[\"'\]})>]+$", "", s).strip()


def detect_kind(source: str) -> DiagramKind:
    for pattern, kind in KIND_FROM_HEADER:
        if pattern.search(source):
            return kind
    return "other"


def detect_language(source: str) -> Language:
    if re.search(r"@startuml|@startmindmap|@startsalt", source, re.I):
        return "plantuml"
    if re.search(
        r"flowchart|graph\s+|sequenceDiagram|classDiagram|stateDiagram|erDiagram|C4",
        source,
        re.I,
    ):
        return "mermaid"
    return "unknown"


def inventory_from_source(source: str) -> Inventory:
    language = detect_language(source)
    kind = detect_kind(source)
    salt = bool(
        re.search(r"@startsalt|\bsalt\b", source, re.I) and language == "plantuml"
    )
    nodes: dict[str, NodeRecord] = {}
    edges: list[EdgeRecord] = []

    def add_node(nid: str, label: str | None = None) -> None:
        clean_id = nid.strip()
        if not clean_id:
            return
        clean_label = unquote(label) if label else clean_id
        existing = nodes.get(clean_id)
        if not existing:
            nodes[clean_id] = NodeRecord(clean_id, clean_label)
        elif label and existing.label == existing.id:
            existing.label = clean_label

    if language == "plantuml":
        for m in re.finditer(
            r'(?:participant|actor|component|class|entity|object|node|database|queue)\s+(?:as\s+)?(?:"([^"]+)"|([A-Za-z_][\w]*))(?:\s+as\s+"?([^"\n]+)"?)?',
            source,
            re.I,
        ):
            quoted, ident, alias = m.group(1), m.group(2), m.group(3)
            nid = ident or quoted or ""
            label = (alias or quoted or ident or "").strip().strip('"')
            add_node(nid, label)
        for m in re.finditer(
            r"([A-Za-z_][\w]*)\s*(?:-+>|-->|\.\.>|<\|--)\s*([A-Za-z_][\w]*)(?:\s*:\s*(.+))?",
            source,
        ):
            add_node(m.group(1))
            add_node(m.group(2))
            edges.append(
                EdgeRecord(m.group(1), m.group(2), (m.group(3) or "").strip() or None)
            )
    else:
        for m in re.finditer(
            r"([A-Za-z_][\w]*)\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\})",
            source,
        ):
            inner = m.group(0)[len(m.group(1)) :].strip()
            add_node(m.group(1), unquote(inner))
        for m in re.finditer(
            r"([A-Za-z_][\w]*)[^\n]*?(-->|---|-.->|==>|==)\s*(?:\|([^|]+)\|)?\s*([A-Za-z_][\w]*)",
            source,
        ):
            add_node(m.group(1))
            add_node(m.group(4))
            edges.append(
                EdgeRecord(m.group(1), m.group(4), (m.group(3) or "").strip() or None)
            )
        for m in re.finditer(
            r"([A-Za-z_][\w]*)\s*->>?\s*([A-Za-z_][\w]*)\s*:\s*(.+)",
            source,
        ):
            add_node(m.group(1))
            add_node(m.group(2))
            edges.append(EdgeRecord(m.group(1), m.group(2), m.group(3).strip()))

    return Inventory(
        kind=kind,
        language=language,
        nodes=list(nodes.values()),
        edges=edges,
        salt=salt,
    )


if __name__ == "__main__":
    import json
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1], encoding="utf-8").read()
    inv = inventory_from_source(src)
    print(
        json.dumps(
            {
                "kind": inv.kind,
                "language": inv.language,
                "salt": inv.salt,
                "nodes": [n.__dict__ for n in inv.nodes],
                "edges": [{"from": e.frm, "to": e.to, "label": e.label} for e in inv.edges],
            },
            indent=2,
        )
    )
