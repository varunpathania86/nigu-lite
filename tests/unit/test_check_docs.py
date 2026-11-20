import tempfile
import unittest
from pathlib import Path

from scripts import check_docs

INSTRUCTION = "---\ndescription: Example\n---\n" + "line\n" * 20


class CheckDocsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".github/instructions").mkdir(parents=True)
        for template in check_docs.REQUIRED_TEMPLATES:
            path = self.root / "docs/templates" / template
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n")

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_consistent_repo_passes(self):
        self.write(".github/instructions/git.instructions.md", INSTRUCTION)
        self.write("AGENTS.md", "| Git | `.github/instructions/git.instructions.md` |\n")
        self.assertEqual(check_docs.run(self.root), [])

    def test_index_mismatch_both_ways(self):
        self.write(".github/instructions/git.instructions.md", INSTRUCTION)
        self.write("AGENTS.md", "`tests.instructions.md`\n")
        errors = check_docs.run(self.root)
        self.assertIn("AGENTS.md indexes missing file tests.instructions.md", errors)
        self.assertIn("git.instructions.md is not indexed in AGENTS.md", errors)

    def test_instruction_size_and_front_matter(self):
        self.write(".github/instructions/a.instructions.md", "no front matter\n")
        self.write("AGENTS.md", "`a.instructions.md`\n")
        errors = " ".join(check_docs.run(self.root))
        self.assertIn("expected 20-30", errors)
        self.assertIn("lacks YAML front matter", errors)

    def test_agents_line_limit(self):
        self.write("AGENTS.md", "x\n" * 61)
        self.assertIn("AGENTS.md has more than 60 lines", check_docs.run(self.root))

    def test_missing_template(self):
        (self.root / "docs/templates/ADR.template.md").unlink()
        self.write("AGENTS.md", "x\n")
        self.assertIn("Missing template docs/templates/ADR.template.md", check_docs.run(self.root))

    def test_mermaid_rules(self):
        self.write("AGENTS.md", "x\n")
        self.write("ok.md", "```mermaid\nflowchart LR\n  A --> B\n```\n")
        self.write("nested.md", "````markdown\n```mermaid\nnonsense\n```\n````\n")
        self.write("bad.md", "```mermaid\nflowchat LR\n```\n")
        self.write("open.md", "```mermaid\nflowchart LR\n")
        errors = " ".join(check_docs.run(self.root))
        self.assertNotIn("ok.md", errors)
        self.assertNotIn("nested.md", errors)
        self.assertIn("bad.md:2: unknown mermaid diagram type 'flowchat'", errors)
        self.assertIn("open.md:1: code block is never closed", errors)

    def test_mermaid_palette(self):
        self.write("AGENTS.md", "x\n")
        ok_def = f"  classDef app {check_docs.PALETTE['app']}\n"
        self.write("ok.md", f"```mermaid\nflowchart LR\n  A --> B:::app\n  class A app\n{ok_def}```\n")
        self.write("colour.md", "```mermaid\nflowchart LR\n  A:::app\n  classDef app fill:#000\n```\n")
        self.write("unknown.md", "```mermaid\nflowchart LR\n  class A,B pink\n```\n")
        self.write("undefined.md", f"```mermaid\nflowchart LR\n  A:::app\n  B:::data\n{ok_def}```\n")
        errors = " ".join(check_docs.run(self.root))
        self.assertNotIn("ok.md", errors)
        self.assertIn("colour.md:4: classDef app must be", errors)
        self.assertIn("unknown.md:3: mermaid class 'pink' is not in the palette", errors)
        self.assertIn("undefined.md:1: mermaid class 'data' is used but has no classDef", errors)
        self.assertNotIn("'app' is used but", errors)

    def mermaid(self, name, body, classes=()):
        defs = "".join(f"  classDef {c} {check_docs.PALETTE[c]}\n" for c in classes)
        self.write(name, f"```mermaid\n{body}{defs}```\n")

    def test_change_markers(self):
        self.write("AGENTS.md", "x\n")
        border = check_docs.STYLE.added_node
        self.mermaid(
            "ok.md",
            'flowchart LR\n  A --> N["[+] New"] --> S["[+] step"]:::new\n  A -.-> X["[-] Old"]:::removed\n'
            f'  Y["[-] Gone"]\n  class Y removed\n  class N core\n  style N {border}\n',
            ("core", "new", "removed"),
        )
        self.mermaid("unmarked.md", 'flowchart LR\n  A --> N["New"]:::new\n  X:::removed\n', ("new", "removed"))
        self.mermaid(
            "added.md",
            'flowchart LR\n  A --> N["[+] Typed"]:::new\n  B["[+] Bare"]\n  C["[+] No border"]\n'
            f"  class N,C core\n  style A {border}\n",
            ("core", "new"),
        )
        errors = " ".join(check_docs.run(self.root))
        self.assertNotIn("ok.md", errors)
        self.assertIn("unmarked.md:1: 'N' is new; start its quoted label with '[+]'", errors)
        self.assertIn("unmarked.md:1: 'X': a '[-]' label and the 'removed' class go together", errors)
        self.assertIn("added.md:1: 'N' has a component class; drop ':::new'", errors)
        self.assertIn("added.md:1: added node 'B' needs its component class", errors)
        self.assertIn("added.md:1: added node 'C' needs its green border style", errors)
        self.assertIn("added.md:7: 'style' is only for subgraphs and added '[+]' nodes", errors)

    def test_uncoloured_decisions_and_sequences(self):
        self.write("AGENTS.md", "x\n")
        self.mermaid("ok.md", 'flowchart LR\n  D{"ok?"} --> H{{"hexagon"}}\n  class H app\n', ("app",))
        self.mermaid("decision.md", 'flowchart LR\n  D{"ok?"} --> A\n  class D,A app\n', ("app",))
        self.mermaid("sequence.md", "sequenceDiagram\n  rect rgb(200, 0, 0)\n  A->>B: hi\n  end\n")
        errors = " ".join(check_docs.run(self.root))
        self.assertNotIn("ok.md", errors)
        self.assertIn("decision.md:1: decision node 'D' must stay uncoloured", errors)
        self.assertNotIn("node 'A'", errors)
        self.assertIn("sequence.md:3: sequence diagrams stay uncoloured", errors)

    def test_subgraph_and_link_styles(self):
        self.write("AGENTS.md", "x\n")
        sg, add, rm = check_docs.STYLE.subgraph, check_docs.STYLE.added_link, check_docs.STYLE.removed_link
        self.mermaid(
            "ok.md",
            f'flowchart LR\n  subgraph VPS-1["vps"]\n    subgraph NET\n'
            f'    A & B --> C -->|"x -> y"| D\n    end\n  end\n'
            f"  C -.-> E\n  C -. label .-> F\n  linkStyle 0,1,2 {add}\n  linkStyle 3,4 {rm}\n"
            f"  style VPS-1 {sg}\n  style NET {sg}\n",
        )
        self.mermaid("missing.md", "flowchart LR\n  subgraph VPS\n  A\n  end\n")
        self.mermaid(
            "wrong.md",
            "flowchart LR\n  subgraph VPS\n  A --> B\n  end\n  style VPS fill:#fff\n  style A fill:#f00\n"
            f"  linkStyle 0 stroke:#f00\n  linkStyle 0 {rm}\n  linkStyle 1 {add}\n",
        )
        errors = " ".join(check_docs.run(self.root))
        self.assertNotIn("ok.md", errors)
        self.assertIn("missing.md:1: subgraph 'VPS' needs 'style VPS", errors)
        self.assertIn("wrong.md:6: subgraph style must be", errors)
        self.assertIn("wrong.md:7: 'style' is only for subgraphs", errors)
        self.assertIn("wrong.md:8: linkStyle must be", errors)
        self.assertIn("wrong.md:9: linkStyle 0 is styled as removed (dotted -.->) but link 0 is not", errors)
        self.assertIn("wrong.md:10: linkStyle index 1 does not exist (1 links", errors)

    def test_link_indexes_ignore_ampersands_inside_labels(self):
        self.write("AGENTS.md", "x\n")
        add = check_docs.STYLE.added_link
        self.mermaid(
            "valid.md",
            'flowchart LR\n  A[ERP & school] --> B["Course & attendance"] --> C[Results]\n'
            '  C -->|"students & staff"| D[Timetable]\n  A & B --> D\n'
            f"  linkStyle 4 {add}\n",
        )
        self.mermaid(
            "invalid.md",
            f"flowchart LR\n  A[ERP & school] --> B[App]\n  linkStyle 1 {add}\n",
        )
        errors = check_docs.run(self.root)
        self.assertFalse(any(error.startswith("valid.md:") for error in errors))
        self.assertTrue(
            any(error.startswith("invalid.md:4: linkStyle index 1 does not exist (1 links") for error in errors)
        )

    def test_load_style_reads_source_file(self):
        self.write(
            "style.md",
            "```mermaid\nflowchart LR\n  subgraph S\n  A\n  end\n  linkStyle 0 stroke:#0f0\n"
            "  linkStyle 1 stroke:#999,stroke-dasharray:5\n  style S fill:none\n  style A stroke:#0f0\n"
            "  classDef app fill:#123\n```\n```mermaid\nflowchart LR\n  classDef app fill:#999\n```\n",
        )
        style = check_docs.load_style(self.root / "style.md")
        self.assertEqual(
            style, ({"app": "fill:#123"}, "fill:none", "stroke:#0f0", "stroke:#0f0", "stroke:#999,stroke-dasharray:5")
        )
        self.write("empty.md", "```mermaid\nflowchart LR\n  A\n```\n")
        with self.assertRaises(ValueError):
            check_docs.load_style(self.root / "empty.md")

    def test_fix_mermaid_adds_corrects_and_removes_styles(self):
        body = (
            'flowchart LR\n  subgraph VPS\n    A[App] --> N["[+] New"]:::new --> M["[+] Typed"]\n  end\n'
            "  class A app\n  class M data\n  style A fill:#000\n  style VPS fill:#fff\n"
            "  classDef app fill:#f00\n  classDef core fill:#0f0\n  classDef local fill:#ccc\n"
        )
        self.write("diagram.md", f"Text\n```mermaid\n{body}```\n\n```mermaid\nsequenceDiagram\n  A->>B: hi\n```\n")
        path = self.root / "diagram.md"
        self.assertTrue(check_docs.fix_mermaid(path))
        text = path.read_text()
        self.assertIn(f"  style VPS {check_docs.STYLE.subgraph}\n", text)
        self.assertIn(f"  style M {check_docs.STYLE.added_node}\n", text)
        self.assertNotIn("style A", text)
        self.assertIn(f"  classDef app {check_docs.PALETTE['app']}\n", text)
        self.assertIn(f"  classDef new {check_docs.PALETTE['new']}\n", text)
        self.assertNotIn("classDef core", text)
        self.assertIn("classDef local fill:#ccc", text)
        self.assertIn("sequenceDiagram\n  A->>B: hi\n```\n", text)
        self.assertFalse(check_docs.fix_mermaid(path))


if __name__ == "__main__":
    unittest.main()
