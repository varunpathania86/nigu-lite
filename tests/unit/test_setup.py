import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SETUP_DIR = Path(__file__).resolve().parents[2] / "scripts/setup"
SETUP = SETUP_DIR / "setup.sh"

# A fake step: ready when its marker file exists; install creates the marker unless it is "broken".
STEP = """\
step_describe() {{ echo "{name}"; }}
step_check() {{ [[ -e "$WORK/{name}.ready" ]]; }}
step_install() {{ echo {name} >> "$WORK/installed"; {fix}; }}
"""


class SetupRunnerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.work = Path(self._tmp.name)
        self.steps = self.work / "steps"
        self.steps.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def step(self, file_name, ready=False, broken=False):
        name = file_name.removesuffix(".sh")
        fix = "true" if broken else f'touch "$WORK/{name}.ready"'
        (self.steps / file_name).write_text(STEP.format(name=name, fix=fix))
        if ready:
            (self.work / f"{name}.ready").touch()

    def run_setup(self, *args):
        env = {**os.environ, "SETUP_STEPS_DIR": str(self.steps), "WORK": str(self.work)}
        bash = shutil.which("bash")
        # noqa reason: fixed argv built from the repo and a temp dir, no external input
        return subprocess.run([bash, str(SETUP), *args], env=env, capture_output=True, text=True, check=False)  # noqa: S603

    def installed(self):
        path = self.work / "installed"
        return path.read_text().split() if path.exists() else []

    def test_installs_only_missing_steps_in_order(self):
        self.step("20-b.sh")
        self.step("10-a.sh", ready=True)
        self.step("30-c.sh")
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.installed(), ["20-b", "30-c"])
        self.assertEqual(self.run_setup().returncode, 0)
        self.assertEqual(self.installed(), ["20-b", "30-c"], "re-run must be idempotent")

    def test_check_mode_reports_all_missing_and_changes_nothing(self):
        self.step("10-a.sh")
        self.step("20-b.sh", ready=True)
        self.step("30-c.sh")
        result = self.run_setup("--check")
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r"missing\s+10-a")
        self.assertRegex(result.stdout, r"ok\s+20-b")
        self.assertRegex(result.stdout, r"missing\s+30-c")
        self.assertEqual(self.installed(), [])

    def test_stops_when_install_does_not_satisfy_check(self):
        self.step("10-a.sh", broken=True)
        self.step("20-b.sh")
        result = self.run_setup()
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r"failed\s+10-a")
        self.assertEqual(self.installed(), ["10-a"], "later steps must not run after a failure")

    def test_step_without_required_function_fails(self):
        (self.steps / "10-a.sh").write_text("step_describe() { echo a; }\nstep_check() { false; }\n")
        result = self.run_setup()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing function step_install", result.stderr)


class HomebrewStepTests(unittest.TestCase):
    """05-homebrew.sh, with uname and brew stubbed so no network or real macOS is needed."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.bin = self.home / "bin"
        self.bin.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def stub(self, name, body):
        path = self.bin / name
        path.write_text(f"#!/usr/bin/env bash\n{body}\n")
        path.chmod(0o755)

    def run_step(self, function):
        script = f'source "{SETUP_DIR}/lib.sh"; source "{SETUP_DIR}/steps/05-homebrew.sh"; {function}'
        env = {**os.environ, "HOME": str(self.home), "SHELL": "/bin/zsh", "PATH": f"{self.bin}:{os.environ['PATH']}"}
        bash = shutil.which("bash")
        # noqa reason: fixed argv built from the repo and a temp dir, no external input
        return subprocess.run([bash, "-c", script], env=env, capture_output=True, text=True, check=False)  # noqa: S603

    def test_is_a_no_op_outside_macos(self):
        self.stub("uname", "echo Linux")
        self.assertEqual(self.run_step("step_check").returncode, 0)

    def test_macos_adds_brew_shellenv_once(self):
        self.stub("uname", "echo Darwin")
        self.stub("brew", "true")
        self.assertNotEqual(self.run_step("step_check").returncode, 0, "brew not yet in ~/.zshrc")
        result = self.run_step("step_install && step_install && step_check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / ".zshrc").read_text().count("shellenv"), 1, "install must be idempotent")


if __name__ == "__main__":
    unittest.main()
