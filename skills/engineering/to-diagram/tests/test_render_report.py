import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_report", ROOT / "scripts" / "render_report.py")
render = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render)


class ReportTests(unittest.TestCase):
    def load(self, name="order-checkout.json"):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_all_five_diagram_types_render_and_html_is_self_contained(self):
        first = self.load()
        second = self.load("architecture-data.json")
        first["diagrams"] += second["diagrams"]
        first["evidence"] += second["evidence"]
        render.validate(first)
        template = (ROOT / "assets" / "report.html").read_text(encoding="utf-8")
        page = render.render_html(first, template)
        self.assertEqual(page.count('<article class="diagram">'), 5)
        self.assertIn('dir="rtl"', page)
        self.assertIn('data-key="D1:edge:0"', page)
        self.assertIn('data-action="in"', page)
        self.assertNotIn('https://', page)
        self.assertNotIn('<script src=', page)
        self.assertIn('id="ev-E3"', page)
        markdown = render.render_md(first)
        self.assertEqual(markdown.count("```mermaid"), 5)
        self.assertIn("erDiagram", markdown)
        self.assertIn("stateDiagram-v2", markdown)
        self.assertIn("## مقارنة الخطة بالتنفيذ", markdown)

    def test_conversation_only_plan_and_existing_project_modes(self):
        plan = self.load("agreed-plan.json")
        existing = self.load("architecture-data.json")
        render.validate(plan)
        render.validate(existing)
        self.assertEqual(plan["phase"], "plan")
        self.assertFalse(any(e["kind"] == "code" for e in plan["evidence"]))
        self.assertEqual(existing["phase"], "explain")
        self.assertTrue(any(e["kind"] == "code" for e in existing["evidence"]))

    def test_claim_with_missing_evidence_is_rejected(self):
        report = self.load()
        report["diagrams"][0]["nodes"][0]["evidence"] = ["ABSENT"]
        with self.assertRaisesRegex(ValueError, "unknown ID"):
            render.validate(report)

    def test_implemented_claim_needs_code_or_observation(self):
        report = self.load()
        report["diagrams"][0]["nodes"][0]["evidence"] = ["E1"]
        with self.assertRaisesRegex(ValueError, "requires code or observation"):
            render.validate(report)

    def test_report_text_cannot_break_out_of_embedded_json_or_html(self):
        report = self.load()
        report["title"] = '</script><script>alert("x")</script>'
        report["diagrams"][0]["nodes"][0]["label"] = '<img src=x onerror=alert(1)>'
        template = (ROOT / "assets" / "report.html").read_text(encoding="utf-8")
        page = render.render_html(report, template)
        self.assertNotIn('<script>alert("x")</script>', page)
        self.assertNotIn('<img src=x', page)
        self.assertIn("&lt;img", page)
        self.assertIn("\\u003cimg", page)

    def test_cli_writes_html_default_and_explicit_markdown(self):
        source = ROOT / "examples" / "order-checkout.json"
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "report.html"
            md_path = Path(tmp) / "report.md"
            self.assertEqual(render.main([str(source), "-o", str(html_path)]), 0)
            self.assertEqual(render.main([str(source), "-o", str(md_path)]), 0)
            self.assertIn("<svg", html_path.read_text(encoding="utf-8"))
            self.assertIn("```mermaid", md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
