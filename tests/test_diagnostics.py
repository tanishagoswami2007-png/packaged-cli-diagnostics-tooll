import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from machine_diagnostics.config import ConfigError, load_config
from machine_diagnostics.diagnostics import check_tool, collect_diagnostics, render_text


class DiagnosticsTests(unittest.TestCase):
    def test_success_with_all_tools_available(self):
        with patch("machine_diagnostics.diagnostics.shutil.which", return_value="/usr/bin/tool"):
            report = collect_diagnostics(["git", "python"])
        self.assertEqual(report["summary"]["tools_missing"], 0)
        self.assertEqual(report["summary"]["tools_available"], 2)

    def test_missing_dependency_is_reported(self):
        with patch(
            "machine_diagnostics.diagnostics.shutil.which",
            side_effect=lambda name: None if name == "docker" else "/usr/bin/" + name,
        ):
            report = collect_diagnostics(["python", "docker"])
        self.assertEqual(report["summary"]["tools_missing"], 1)
        docker = next(x for x in report["developer_tools"] if x["name"] == "docker")
        self.assertFalse(docker["available"])

    def test_malformed_configuration_path(self):
        with self.assertRaises(ConfigError):
            load_config("definitely-missing-config.json")

    def test_malformed_json_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{bad json", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(str(path))

    def test_configuration_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"developer_tools": ["git"]}), encoding="utf-8")
            config = load_config(str(path))
        self.assertEqual(config["developer_tools"], ["git"])

    def test_human_readable_report(self):
        with patch("machine_diagnostics.diagnostics.shutil.which", return_value="/usr/bin/python"):
            report = collect_diagnostics(["python"])
        text = render_text(report)
        self.assertIn("MACHINE DIAGNOSTICS REPORT", text)
        self.assertIn("PYTHON", text)
        self.assertIn("DEVELOPER TOOLS", text)


if __name__ == "__main__":
    unittest.main()
