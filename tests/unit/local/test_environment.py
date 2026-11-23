import json
import unittest
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from scripts.ci.catalog import build_catalog
from scripts.manifests.validator import validate

ROOT = Path(__file__).resolve().parents[3]
ROLE = ROOT / "local/ansible/roles/local_stack"


class LocalCatalogTests(unittest.TestCase):
    def test_local_images_are_catalogued(self):
        modules = {item["id"]: item for item in build_catalog(ROOT)["modules"]}
        self.assertEqual(modules["image-local-vps"]["path"], "local")
        self.assertEqual(modules["image-local-operations"]["path"], "local/operations")

    def test_local_manifest_validates_with_synthetic_tenants(self):
        self.assertEqual(validate(ROOT), [])
        manifest = yaml.safe_load((ROOT / "deployments/local.yml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["environment"], "local")
        self.assertEqual(manifest["tls"]["mode"], "selfsigned")
        self.assertEqual(manifest["products"]["erp"]["tenants"], ["test-company-a", "test-company-b"])


class LocalTemplateTests(unittest.TestCase):
    def setUp(self):
        values = yaml.safe_load((ROOT / "local/ansible/group_vars/local.yml").read_text(encoding="utf-8"))
        self.environment = Environment(
            loader=FileSystemLoader(ROLE / "templates"),
            undefined=StrictUndefined,
            autoescape=True,
        )
        self.values = values

    def test_compose_has_only_local_edge_port_and_pinned_images(self):
        rendered = self.environment.get_template("compose.yml.j2").render(**self.values)
        document = yaml.safe_load(rendered)
        services = document["services"]
        self.assertEqual(services["traefik"]["ports"], ["443:443"])
        self.assertIn("@sha256:", services["traefik"]["image"])
        self.assertIn("@sha256:", services["garage"]["image"])
        self.assertNotIn("ports", services["garage"])
        for service in services.values():
            self.assertIn("healthcheck", service)
            self.assertIn("mem_limit", service)
            self.assertIn("cpus", service)

    def test_dynamic_route_has_tls_and_expected_test_host(self):
        rendered = self.environment.get_template("traefik-dynamic.yml.j2").render(**self.values)
        document = yaml.safe_load(rendered)
        router = document["http"]["routers"]["local-test"]
        self.assertEqual(router["rule"], "Host(`test-school-a.localhost`)")
        self.assertEqual(router["tls"], {})

    def test_image_pins_match_versions_file(self):
        versions = yaml.safe_load((ROOT / "versions.yml").read_text(encoding="utf-8"))["local"]
        for image in ("traefik", "test_web", "garage"):
            expected = image
            pin = self.values[f"{image}_image"]
            self.assertTrue(pin.endswith(versions[image]["digest"]), (expected, pin))

    def test_simulator_generates_host_keys_at_runtime(self):
        containerfile = (ROOT / "local/Containerfile").read_text(encoding="utf-8")
        entrypoint = (ROOT / "local/entrypoint.sh").read_text(encoding="utf-8")
        self.assertIn("rm -f /etc/ssh/ssh_host_*_key", containerfile)
        self.assertIn("ssh-keygen -A", entrypoint)
        self.assertIn("USER 1000:1000", containerfile)

    def test_nested_docker_uses_vfs_storage(self):
        self.assertEqual(self.values["local_docker_storage_driver"], "vfs")
        template = (ROOT / "local/ansible/templates/docker-daemon.json.j2").read_text(encoding="utf-8")
        self.assertEqual(
            json.loads(
                Environment(undefined=StrictUndefined, autoescape=True).from_string(template).render(**self.values)
            ),
            {"storage-driver": "vfs"},
        )


class LocalLifecycleTests(unittest.TestCase):
    def test_start_refreshes_host_key_before_waiting_for_ssh(self):
        script = (ROOT / "local/scripts/up.sh").read_text(encoding="utf-8")
        self.assertLess(script.index('rm -f "$known_hosts"'), script.index("ssh -i"))

    def test_systemd_runtime_override_is_explicit(self):
        script = (ROOT / "local/scripts/up.sh").read_text(encoding="utf-8")
        self.assertIn("--user 0:0", script)
        self.assertIn("--privileged", script)


class LocalDocsTests(unittest.TestCase):
    def test_schema_route_fixture_is_json_serializable(self):
        manifest = yaml.safe_load((ROOT / "deployments/local.yml").read_text(encoding="utf-8"))
        json.dumps(manifest)
        self.assertEqual(manifest["public_ip"], "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
