#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from inventory import inventory_from_source  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


class InventoryTests(unittest.TestCase):
    def test_mermaid_flowchart(self):
        src = (FIXTURES / "flowchart.mmd").read_text(encoding="utf-8")
        inv = inventory_from_source(src)
        self.assertEqual(inv.language, "mermaid")
        self.assertEqual(inv.kind, "flowchart")
        self.assertFalse(inv.salt)
        labels = {n.label for n in inv.nodes}
        self.assertIn("Diagram source", labels)
        self.assertIn("Fidelity judge", labels)
        self.assertGreaterEqual(len(inv.edges), 6)

    def test_plantuml_sequence(self):
        src = (FIXTURES / "sequence.puml").read_text(encoding="utf-8")
        inv = inventory_from_source(src)
        self.assertEqual(inv.language, "plantuml")
        self.assertEqual(inv.kind, "sequence")
        labels = {n.label for n in inv.nodes}
        self.assertIn("Agent", labels)
        self.assertIn("imagen-diagrams", labels)

    def test_salt_is_flagged(self):
        src = "@startsalt\n{+\n  Login\n+}\n@enduml\n"
        inv = inventory_from_source(src)
        self.assertTrue(inv.salt)


if __name__ == "__main__":
    unittest.main()
