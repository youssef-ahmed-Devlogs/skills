import importlib.util
import json
import re
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

    def boxes(self, svg, pattern):
        return [tuple(float(v) for v in m) for m in re.findall(pattern, svg)]

    def test_edge_labels_and_nodes_do_not_overlap(self):
        for name in ("order-checkout.json", "architecture-data.json", "agreed-plan.json"):
            report = self.load(name)
            for diagram in report["diagrams"]:
                if diagram["type"] == "sequence":
                    continue
                svg = render.svg_graph(diagram, {}, rtl=report["language"].startswith("ar"))
                labels = self.boxes(svg, r'class="edge-label-bg" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"')
                nodes = self.boxes(svg, r'<rect class="shape[^"]*" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"')
                rects = [(x, y, x + w, y + h) for x, y, w, h in labels + nodes]
                for i in range(len(rects)):
                    for j in range(i + 1, len(rects)):
                        a, b = rects[i], rects[j]
                        self.assertFalse(a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3], f"{name} {diagram['id']}: {a} overlaps {b}")

    def test_er_fields_stay_inside_their_table(self):
        diagram = self.load("architecture-data.json")["diagrams"][1]
        diagram["nodes"][1]["fields"] += [{"name": f"extra_{k}", "type": "varchar"} for k in range(4)]
        svg = render.svg_graph(diagram, {})
        for match in re.finditer(r'<rect class="shape" x="[\d.]+" y="([\d.]+)" width="[\d.]+" height="([\d.]+)"/>(.*?)</g>', svg):
            bottom = float(match.group(1)) + float(match.group(2))
            for y in re.findall(r'class="field" x="[\d.]+" y="([\d.]+)"', match.group(3)):
                self.assertLess(float(y), bottom - 4)

    def test_each_text_line_takes_the_direction_of_its_first_letter(self):
        self.assertEqual(render.text_dir("Gate::before هل هو"), "ltr")
        self.assertEqual(render.text_dir("فحص Gate::before"), "rtl")
        self.assertEqual(render.text_dir("123 - users"), "ltr")
        diagram = {"id": "D9", "type": "flowchart", "title": "t", "question": "q", "reason": "r",
                   "nodes": [{"id": "a", "label": "فحص auth", "status": "context"}, {"id": "b", "label": "AccessDenied page", "status": "context"}],
                   "edges": [{"from": "a", "to": "b", "status": "context"}]}
        svg = render.svg_graph(diagram, {}, rtl=True)
        self.assertIn('direction="rtl">فحص auth</text>', svg)
        self.assertIn('direction="ltr">AccessDenied page</text>', svg)
        self.assertNotIn('class="edge-label"', svg)

    def test_edge_label_is_optional_and_rtl_mirrors_the_layout(self):
        report = self.load("agreed-plan.json")
        report["diagrams"][0]["edges"][0].pop("label")
        render.validate(report)
        self.assertNotIn('|""|', render.render_md(report))
        diagram = report["diagrams"][0]
        ltr = render.svg_graph(diagram, {}, rtl=False)
        rtl = render.svg_graph(diagram, {}, rtl=True)
        self.assertNotEqual(ltr, rtl)

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
