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


if __name__ == "__main__":
    unittest.main()
