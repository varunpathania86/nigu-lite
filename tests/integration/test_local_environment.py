import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKER = shutil.which("docker")
CURL = shutil.which("curl")


class LocalEnvironmentIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DOCKER or not CURL:
            raise unittest.SkipTest("Docker and curl are required")
        running = subprocess.run(  # noqa: S603  # fixed Docker command for the dedicated simulator
            [DOCKER, "inspect", "-f", "{{.State.Running}}", "nigu-local-vps"],
            check=False,
            capture_output=True,
            text=True,
        )
        if running.returncode != 0 or running.stdout.strip() != "true":
            raise unittest.SkipTest("run make local-deploy before this suite")

    def test_inner_docker_and_ssh_services_are_active(self):
        for service in ("ssh", "docker"):
            with self.subTest(service=service):
                subprocess.run(  # noqa: S603  # fixed Docker command for the dedicated simulator
                    [DOCKER, "exec", "nigu-local-vps", "systemctl", "is-active", service],
                    check=True,
                    capture_output=True,
                    text=True,
                )

    def test_traefik_route_returns_whoami(self):
        body = subprocess.run(  # noqa: S603  # fixed local curl target and self-signed local certificate
            [
                CURL,
                "--fail",
                "--silent",
                "--show-error",
                "--insecure",
                "--resolve",
                "test-school-a.localhost:8443:127.0.0.1",
                "https://test-school-a.localhost:8443/",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("Welcome to nginx!", body)

    def test_traefik_and_garage_are_healthy(self):
        for service in ("nigu-local-traefik-1", "nigu-local-garage-1"):
            with self.subTest(service=service):
                health = subprocess.run(  # noqa: S603  # fixed Docker command and local service allow-list
                    [
                        DOCKER,
                        "exec",
                        "nigu-local-vps",
                        "docker",
                        "inspect",
                        "-f",
                        "{{.State.Health.Status}}",
                        service,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                self.assertEqual(health, "healthy")

    def test_garage_status_is_healthy(self):
        subprocess.run(  # noqa: S603  # fixed Docker command for the dedicated local object store
            [DOCKER, "exec", "nigu-local-vps", "docker", "exec", "nigu-local-garage-1", "/garage", "status"],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
