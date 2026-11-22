import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.manifests.validator import validate

ROOT = Path(__file__).resolve().parents[3]


def copy_schema(root: Path) -> None:
    (root / "deployments").mkdir(parents=True)
    shutil.copy(ROOT / "deployments/schema.json", root / "deployments/schema.json")
    shutil.copy(ROOT / "deployments/tenant.schema.json", root / "deployments/tenant.schema.json")
    shutil.copy(ROOT / "versions.yml", root / "versions.yml")


class ValidatorRejectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        copy_schema(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def write_manifest(self, document):
        (self.root / "deployments/vps-01.yml").write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    def base_manifest(self):
        return {
            "schema_version": 1,
            "host": "vps-01",
            "environment": "production",
            "public_ip": "203.0.113.10",
            "node_record": "vps01.nigu.in",
            "control_plane": True,
            "dns": {"provider": "cloudflare"},
            "tls": {"mode": "letsencrypt"},
            "wireguard": {"subnet": "10.10.0.0/24", "address": "10.10.0.1", "port": 51820},
            "upgrade_day": "saturday",
            "core_services": ["edge", "data"],
            "products": {"erp": {"tenants": []}, "edu": {"tenants": {}}},
        }

    def test_valid_manifest_has_no_findings(self):
        self.write_manifest(self.base_manifest())
        self.assertEqual(validate(self.root), [])

    def test_missing_vps_fails_schema(self):
        manifest = self.base_manifest()
        del manifest["public_ip"]
        self.write_manifest(manifest)
        codes = {item.code for item in validate(self.root)}
        self.assertIn("schema", codes)

    def test_production_rejects_insecure_tls(self):
        manifest = self.base_manifest()
        manifest["tls"]["mode"] = "selfsigned"
        self.write_manifest(manifest)
        codes = {item.code for item in validate(self.root)}
        self.assertIn("production-tls", codes)

    def test_duplicate_host_fails(self):
        self.write_manifest(self.base_manifest())
        second = self.base_manifest()
        second["host"] = "vps-01"
        second["node_record"] = "vps02.nigu.in"
        (self.root / "deployments/vps-02.yml").write_text(yaml.safe_dump(second, sort_keys=False), encoding="utf-8")
        codes = {item.code for item in validate(self.root)}
        self.assertIn("duplicate-host", codes)
        self.assertIn("manifest-host", codes)

    def test_plaintext_vault_fails(self):
        tenant = self.root / "tests/tenants/erp/test-company-a"
        shutil.copytree(ROOT / "tests/tenants/erp/test-company-a", tenant)
        (tenant / "vault.yml").write_text("password: cleartext\n", encoding="utf-8")
        codes = {item.code for item in validate(self.root)}
        self.assertIn("vault-encryption", codes)


if __name__ == "__main__":
    unittest.main()
