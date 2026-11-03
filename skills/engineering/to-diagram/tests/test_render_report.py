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
        self.assertEqual(page.count('<figure class="diagram"'), 5)
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
        self.assertRegex(svg, r'direction="rtl"[^>]*>فحص auth</text>')
        self.assertRegex(svg, r'direction="ltr"[^>]*>AccessDenied page</text>')
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

    def sequence(self, label="POST /checkout", loop=False):
        return {"id": "S9", "type": "sequence", "title": "t", "question": "q", "reason": "r",
                "participants": [{"id": "a", "label": "Checkout API", "status": "context"}, {"id": "b", "label": "مزوّد الدفع الخارجي", "status": "context"}],
                "messages": [{"from": "a", "to": "a" if loop else "b", "label": label, "status": "context"}]}

    def test_a_long_sequence_label_widens_the_gap_and_stays_in_its_box(self):
        label = "يطلب تفويض المبلغ من مزوّد الدفع مع رقم الطلب ومفتاح عدم التكرار"
        svg = render.svg_sequence(self.sequence(label), {}, rtl=True)
        lines = [float(x) for x in re.findall(r'<line class="seq-life" x1="([\d.]+)"', svg)]
        widest = max(render.text_width(line, render.LABEL_SIZE) for line in render.wrap(label, 300, render.LABEL_SIZE))
        self.assertGreater(abs(lines[0] - lines[1]), widest)
        self.assertIn('class="edge-label-bg"', svg)
        self.assertGreater(lines[0], lines[1])

    def test_a_self_message_label_sits_beside_its_loop(self):
        svg = render.svg_sequence(self.sequence("validates the cart", loop=True), {})
        loop_x = float(re.search(r'<line class="seq-life" x1="([\d.]+)"', svg).group(1))
        label_x = float(re.search(r'class="edge-label-bg" x="([\d.]+)"', svg).group(1))
        self.assertGreater(label_x, loop_x + 70)

    def test_an_arabic_report_shows_no_schema_word_in_english(self):
        report = self.load("architecture-data.json")
        report["language"] = "ar"
        template = (ROOT / "assets" / "report.html").read_text(encoding="utf-8")
        page = render.render_html(report, template)
        self.assertNotIn("Code Flow Audit", page)
        self.assertIn('<p class="kicker">شرح</p>', page)
        self.assertIn("<span>تقرير الرسوم</span>", page)
        self.assertIn('<span class="badge verified"><i></i>متحقق منه</span>', page)
        self.assertIn('"status":"منفّذ"', page)
        self.assertIn("| منفّذ |", render.render_md(report))

    def test_a_nullable_field_says_so(self):
        diagram = self.load("architecture-data.json")["diagrams"][1]
        diagram["nodes"][1]["fields"].append({"name": "coupon_id", "type": "bigint", "key": "FK", "nullable": True})
        self.assertIn(">FK coupon_id bigint NULL</text>", render.svg_graph(diagram, {}))
        self.assertIn('bigint coupon_id FK "nullable"', render.render_mermaid(diagram))

    def test_every_text_in_a_box_carries_its_room(self):
        report = self.load()
        for diagram in report["diagrams"]:
            draw = render.svg_sequence if diagram["type"] == "sequence" else render.svg_graph
            svg = draw(diagram, {})
            for css in ("node-label", "edge-label", "field"):
                for tag in re.findall(rf'<text class="{css}"[^>]*>', svg):
                    self.assertIn("data-fit=", tag)

    def test_the_page_follows_light_and_dark_and_the_svg_has_no_fixed_colour(self):
        report = self.load()
        template = (ROOT / "assets" / "report.html").read_text(encoding="utf-8")
        page = render.render_html(report, template)
        self.assertIn('content="light dark"', page)
        self.assertIn("prefers-color-scheme:dark", page)
        self.assertEqual(page.count("data-theme-choice="), 3)
        for diagram in report["diagrams"]:
            draw = render.svg_sequence if diagram["type"] == "sequence" else render.svg_graph
            self.assertNotRegex(draw(diagram, {}), r'(fill|stroke)="#')

    def test_each_diagram_reads_as_a_list_and_evidence_links_back_to_it(self):
        report = self.load("architecture-data.json")
        template = (ROOT / "assets" / "report.html").read_text(encoding="utf-8")
        page = render.render_html(report, template)
        self.assertEqual(page.count('<details class="as-text">'), len(report["diagrams"]))
        self.assertIn('data-open="C1:node:1"', page)
        evidence_row = page[page.index('id="ev-P2"'):page.index('id="ev-P3"')]
        self.assertIn('data-open="C1:edge:1"', evidence_row)
        self.assertIn('<ul class="stats">', page)

    def test_an_edge_name_points_the_reading_way(self):
        diagram = self.load("architecture-data.json")["diagrams"][0]
        edge = diagram["edges"][0]
        self.assertIn("</bdi> → <bdi>", render.element_name(diagram, "edge", edge))
        self.assertIn("</bdi> ← <bdi>", render.element_name(diagram, "edge", edge, rtl=True))

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
