import unittest

from scripts.git_rules import check_branch, check_message, check_subject


class BranchTests(unittest.TestCase):
    def test_allowed_branches(self):
        for name in ("main", "feature/42-tenant-manifest", "patch/gibbon-28.0.01", "docs/lld-ci"):
            self.assertEqual(check_branch(name), [], name)

    def test_rejected_branches(self):
        for name in ("master", "feat/x", "feature/", "feature/Upper", "random", "feature/a b"):
            self.assertTrue(check_branch(name), name)


class SubjectTests(unittest.TestCase):
    def test_plain_sentence_passes(self):
        self.assertEqual(check_subject("Stage 0 - Added repository foundation"), [])

    def test_type_prefixes_rejected(self):
        for subject in ("feat: add x", "fix(edu): broken upload", "(feat) Add x", "Feat!: Add x"):
            self.assertTrue(check_subject(subject), subject)

    def test_lowercase_start_and_period_rejected(self):
        self.assertTrue(check_subject("added x"))
        self.assertTrue(check_subject("Added x."))

    def test_length_limit(self):
        self.assertEqual(check_subject("A" * 72), [])
        self.assertTrue(check_subject("A" * 73))


class MessageTests(unittest.TestCase):
    def test_comments_and_body(self):
        message = "# git comment\nAdded tenant validator\n\nWhy: schema drift.\n"
        self.assertEqual(check_message(message), [])

    def test_body_needs_blank_line(self):
        self.assertTrue(check_message("Added tenant validator\nBody without gap\n"))

    def test_ai_coauthor_rejected_human_allowed(self):
        human = "Added x\n\nCo-authored-by: Asha Rao <asha@example.org>\n"
        ai = "Added x\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\n"
        self.assertEqual(check_message(human), [])
        self.assertTrue(check_message(ai))

    def test_empty_message(self):
        self.assertTrue(check_message("# only comments\n\n"))


if __name__ == "__main__":
    unittest.main()
