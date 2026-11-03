import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "profile_public_benchmark.py"
spec = importlib.util.spec_from_file_location("profile_public_benchmark", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicBenchmarkTests(unittest.TestCase):
    def test_jsonl_fields_and_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "user_cases.jsonl"
            p.write_text('{"User Tool":"FakeSearch","User Instruction":"summarize"}\n'
                         '{"User Tool":"FakeRead"}\n')
            data = module.profile(p)
            self.assertEqual(data["record_count"], 2)
            self.assertEqual(data["field_coverage"]["User Tool"]["fraction"], 1.0)
            self.assertEqual(data["field_coverage"]["User Instruction"]["present"], 1)
            self.assertEqual(len(data["sha256"]), 64)

    def test_json_array(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "cases.json"
            p.write_text(json.dumps([{"Tool Response": "untrusted data"}]))
            self.assertEqual(module.profile(p)["record_count"], 1)

    def test_reject_bad_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "oops.json"
            p.write_text('{"Tool Response": "not a list"}')
            with self.assertRaises(ValueError):
                module.profile(p)

    def test_reject_other_extensions(self):
        with self.assertRaises(ValueError):
            module.load_records("dataset.py")
