"""Behavioral checks for deduplication, provenance, and conservative discovery."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "model-pr-optimization-history/scripts/mechanisms.py"
spec = importlib.util.spec_from_file_location("mechanisms", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class MechanismIndexTests(unittest.TestCase):
    def write_card(self, root, framework, model, number, title, generated=False):
        path = root / framework / model / "README.en.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# History\n\n### PR #{number} - {title}\n\n"
                        f"- Link: https://github.com/{mod.REPOS[framework]}/pull/{number}\n"
                        "- Status/date: merged / 2026-01-01\n"
                        + ("- Extracted diff scope (not a manual audit): inventory\n" if generated else ""))
        return path

    def test_dedup_retains_all_model_provenance_and_separates_repositories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_card(root, "sglang", "a", 1, "Fuse norm")
            self.write_card(root, "sglang", "b", 1, "Fuse norm", True)
            self.write_card(root, "vllm", "a", 1, "Fix radix cache")
            rows, manifest = mod.collect(root)
            self.assertEqual((manifest["unique_prs"], manifest["source_cards"]), (2, 3))
            row = next(row for row in rows if row["id"] == "sglang:1")
            self.assertEqual(row["model_dossiers"], ["a", "b"])
            self.assertEqual(len(row["sources"]), 2)
            self.assertEqual(row["sources"][0]["line"], 3)
            self.assertEqual(row["evidence"]["measurement"], "not_assessed")
            self.assertEqual(row["sources"][1]["card_type"], "generated_inventory")

    def test_ambiguous_words_do_not_become_request_scheduling_or_host_work(self):
        for title in ("Persistent TopK scheduler kernel", "Fix diffusion scheduler", "Fix CI scheduler"):
            self.assertNotIn("scheduling", mod.hints([title], mod.RULES))
        self.assertNotIn("host", mod.hints(["[CPU] Add FP8 Bmm support"], mod.RULES))
        self.assertIn("scheduling", mod.hints(["Add chunked prefill support"], mod.RULES))

    def test_multitag_does_not_manufacture_primary_or_measured_benefit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_card(root, "sglang", "a", 2, "Fix overlap with KV cache")
            rows, _ = mod.collect(root)
            self.assertIsNone(rows[0]["primary_candidate"])
            self.assertEqual(set(rows[0]["mechanism_candidates"]), {"overlap", "data"})
            self.assertIn("fix", rows[0]["work_kind_hints"])
            self.assertNotIn("performance", rows[0]["work_kind_hints"])
            self.assertEqual(mod.select(rows, "data", "sglang", "fix"), rows)
            self.assertEqual(mod.select(rows, "scheduling"), [])
            self.assertEqual(rows[0]["evidence"]["applicability"], "not_established")

    def test_unknown_is_retained_and_invalid_identity_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_card(root, "vllm", "a", 9, "Update model configuration")
            rows, manifest = mod.collect(root)
            self.assertEqual(manifest["unclassified"], 1)
            self.assertEqual(mod.select(rows, "unclassified"), rows)
            path.write_text(path.read_text().replace("/pull/9", "/pull/10"))
            with self.assertRaises(ValueError):
                mod.collect(root)

    def test_rebuild_is_deterministic_and_manifest_tracks_source_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_card(root, "vllm", "a", 3, "Fuse norm")
            first = mod.collect(root)
            self.assertEqual(first, mod.collect(root))
            path.write_text(path.read_text() + "\nNew local evidence\n")
            second = mod.collect(root)
            self.assertEqual(first[0], second[0])
            self.assertNotEqual(first[1]["inputs"], second[1]["inputs"])


if __name__ == "__main__":
    unittest.main()
