from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_en_book_latex.py"


def load_exporter():
    spec = importlib.util.spec_from_file_location("export_en_book_latex", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ExportEnglishBookLatexTest(unittest.TestCase):
    def test_english_latex_exporter_uses_submission_nav_and_outputs(self):
        exporter = load_exporter()
        config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))

        items = exporter.prepare_latex_items(exporter.flatten_nav(exporter.find_en_nav(config)))
        paths = [item.path for item in items]

        self.assertEqual(exporter.OUT_TEX.name, "data_engineering_book_en_16k_latex.tex")
        self.assertEqual(exporter.OUT_PDF.name, "data_engineering_book_en_16k_latex.pdf")
        self.assertIn("preface.md", paths)
        self.assertIn("part14/p15_dataagent_semantic_nl2sql_agent.md", paths)
        self.assertIn("appendix_f_terminology_and_chinese_english_mapping.md", paths)
        self.assertNotIn("index.md", paths)
        self.assertNotIn("translation-status.md", paths)

    def test_english_latex_document_has_book_metadata_and_front_matter(self):
        exporter = load_exporter()
        stats = exporter.ExportStats()
        with tempfile.TemporaryDirectory() as tmpdir:
            assets = exporter.AssetManager(Path(tmpdir) / "latex_assets_en_test", stats)
            assets.reset()
            tex = exporter.build_latex_document(
                [exporter.NavItem("Preface", "preface.md", 1)],
                assets,
                stats,
            )

        self.assertIn(r"\title{Data Engineering for Large Foundation Models\\A Handbook}", tex)
        self.assertIn(r"\tableofcontents", tex)
        self.assertIn(r"\frontmatter", tex)
        self.assertIn(r"\mainmatter", tex)
        self.assertEqual(stats.files, 1)


if __name__ == "__main__":
    unittest.main()
