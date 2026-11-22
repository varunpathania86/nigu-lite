import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.ci.catalog import catalog
from scripts.ci.lock import build_lock
from scripts.ci.package import MAX_PACKAGE_BYTES, package_tenant
from scripts.ci.plan import plan
from scripts.ci.report import final_status, html_report, markdown_report
from scripts.ci.retention import retention_plan
from scripts.ci.snapshot import create_snapshot
from scripts.manifests.validator import validate

ROOT = Path(__file__).resolve().parents[3]
GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("git executable is required")


class ManifestTests(unittest.TestCase):
    def test_repository_manifests_are_valid(self):
        self.assertEqual(validate(ROOT), [])

    def test_catalog_contains_test_tenants(self):
        result = catalog(ROOT)
        ids = {module["id"] for module in result["modules"]}
        self.assertTrue(result["valid"])
        self.assertIn("tenant-erp-test-company-a", ids)
        self.assertIn("tenant-edu-test-school-b", ids)


class PlanTests(unittest.TestCase):
    def test_docs_only_plan_has_no_modules(self):
        result = plan(catalog(ROOT), ["docs/developer/getting-started.md"])
        self.assertFalse(result["any"])
        self.assertEqual(result["modules"], [])

    def test_tenant_path_selects_only_that_package(self):
        path = "tests/tenants/erp/test-company-a/assets/logo.svg"
        result = plan(catalog(ROOT), [path])
        self.assertEqual([item["id"] for item in result["modules"]], ["tenant-erp-test-company-a"])

    def test_manual_all_selects_every_module(self):
        expected = catalog(ROOT)["modules"]
        result = plan(catalog(ROOT), [], "all")
        self.assertEqual(result["modules"], expected)


class PackageTests(unittest.TestCase):
    def test_tenant_package_is_deterministic_and_allow_listed(self):
        tenant = ROOT / "tests/tenants/erp/test-company-a"
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.tar.gz"
            second = Path(temporary) / "second.tar.gz"
            one = package_tenant(tenant, first)
            two = package_tenant(tenant, second)
            self.assertEqual(one["sha256"], two["sha256"])
            self.assertLess(one["size_bytes"], MAX_PACKAGE_BYTES)
            with tarfile.open(first) as archive:
                names = archive.getnames()
            self.assertNotIn("vault.yml", names)
            self.assertIn("tenant.yml", names)

    def test_package_rejects_non_allow_listed_file(self):
        source = ROOT / "tests/tenants/edu/test-school-a"
        with tempfile.TemporaryDirectory() as temporary:
            tenant = Path(temporary) / "tenant"
            shutil.copytree(source, tenant)
            (tenant / "unexpected.txt").write_text("do not package", encoding="utf-8")
            with self.assertRaises(ValueError):
                package_tenant(tenant, Path(temporary) / "tenant.tar.gz")


class SnapshotTests(unittest.TestCase):
    def test_commit_staged_and_worktree_trees_differ(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run([GIT, "init", "-q"], cwd=repo, check=True)  # noqa: S603
            subprocess.run(  # noqa: S603  # isolated test repository
                [GIT, "config", "user.email", "ci@example.invalid"], cwd=repo, check=True
            )
            subprocess.run([GIT, "config", "user.name", "CI"], cwd=repo, check=True)  # noqa: S603
            tracked = repo / "tracked.txt"
            tracked.write_text("committed\n", encoding="utf-8")
            subprocess.run([GIT, "add", "."], cwd=repo, check=True)  # noqa: S603
            subprocess.run([GIT, "commit", "-qm", "Initial"], cwd=repo, check=True)  # noqa: S603
            tracked.write_text("staged\n", encoding="utf-8")
            subprocess.run([GIT, "add", "tracked.txt"], cwd=repo, check=True)  # noqa: S603
            tracked.write_text("unstaged\n", encoding="utf-8")
            (repo / "untracked.txt").write_text("worktree\n", encoding="utf-8")

            objects_before = sorted((repo / ".git/objects").rglob("*"))
            commit = create_snapshot(repo, "commit", repo / "commit.tar")["tree"]
            staged = create_snapshot(repo, "staged", repo / "staged.tar")["tree"]
            worktree = create_snapshot(repo, "worktree", repo / "worktree.tar")["tree"]
            self.assertEqual(sorted((repo / ".git/objects").rglob("*")), objects_before)
            self.assertNotEqual(commit, staged)
            self.assertNotEqual(staged, worktree)
            staged_paths = subprocess.run(  # noqa: S603  # isolated test repository
                [GIT, "diff", "--cached", "--name-only"],
                cwd=repo,
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
            self.assertEqual(staged_paths, "tracked.txt")


class ReportTests(unittest.TestCase):
    def test_report_records_failures_and_is_self_contained(self):
        fragments = [
            {"job": "lint", "status": "success", "duration_seconds": 2},
            {"job": "scan", "status": "failure", "duration_seconds": 3},
        ]
        markdown = markdown_report("Build", fragments)
        self.assertEqual(final_status(fragments), "failure")
        self.assertIn("**Final status:** failure", markdown)
        self.assertIn("<style>", html_report("Build", markdown))
        self.assertNotIn("https://", html_report("Build", markdown))


class LockTests(unittest.TestCase):
    def test_lock_rejects_unverified_signatures(self):
        artifact = {
            "kind": "image",
            "name": "fixture",
            "digest": "sha256:1234",
            "signature": {"verified": False},
            "sbom": "fixture.cdx.json",
        }
        with self.assertRaises(ValueError):
            build_lock("vps-01", "commit", [artifact])

    def test_lock_accepts_verified_digest(self):
        artifact = {
            "kind": "tenant",
            "name": "test-company-a",
            "digest": "sha256:1234",
            "signature": {"verified": True},
            "sbom": "package.json",
        }
        lock = build_lock("vps-01", "commit", [artifact])
        self.assertEqual(lock["artifacts"], [artifact])


class RetentionTests(unittest.TestCase):
    def test_retention_preserves_recent_and_versioned_artifacts(self):
        metadata = [
            {"package": "app", "digest": "sha256:1", "created_at": "2026-01-01", "tags": ["sha-1"]},
            {"package": "app", "digest": "sha256:2", "created_at": "2026-01-02", "tags": ["sha-2"]},
            {
                "package": "app",
                "digest": "sha256:3",
                "created_at": "2025-01-01",
                "tags": ["sha-3", "v1.0.0"],
            },
        ]
        result = retention_plan(metadata, keep=1)
        self.assertEqual({item["digest"] for item in result["retain"]}, {"sha256:2", "sha256:3"})
        self.assertEqual([item["digest"] for item in result["candidates"]], ["sha256:1"])


if __name__ == "__main__":
    unittest.main()
