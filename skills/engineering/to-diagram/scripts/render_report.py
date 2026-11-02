#!/usr/bin/env python3
"""Render an evidence-linked, offline diagram report from agent-authored JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import sys

TYPES = {"flowchart", "sequence", "c4", "er", "state"}
STATUSES = {"planned", "implemented", "changed", "missing", "unknown", "context"}
CONFIDENCES = {"verified", "inferred", "planned", "unknown"}
VERDICTS = {"matched", "changed", "missing", "unverified"}
EVIDENCE_KINDS = {"code", "test", "request", "assumption", "observation"}
UI = {
    "ar": {"phase": "المرحلة", "repository": "المشروع", "baseline": "المرجع", "scope": "نطاق الفحص", "decisions": "القرارات", "unknowns": "ما لم يُحسم", "diagrams": "الرسوم", "audit": "مقارنة الخطة بالتنفيذ", "evidence": "الأدلة", "question": "سؤال المراجعة", "why": "سبب الاختيار", "zoom": "تكبير", "out": "تصغير", "reset": "إعادة الضبط", "element": "العنصر", "status": "الحالة", "step": "الخطوة", "planned": "المخطط", "actual": "المنفذ", "result": "النتيجة", "note": "ملاحظة", "source": "المصدر", "claim": "ما يثبته", "confidence": "الثقة", "kind": "النوع", "empty": "لا توجد عناصر", "help": "اسحب للتنقل، استخدم عجلة الفأرة للتكبير، واضغط على عنصر للتفاصيل.", "footer": "تقرير مبني على الأدلة المذكورة؛ حدود الفحص موضحة أعلاه."},
    "en": {"phase": "Phase", "repository": "Repository", "baseline": "Baseline", "scope": "Inspection scope", "decisions": "Decisions", "unknowns": "Unknowns", "diagrams": "Diagrams", "audit": "Plan vs implementation", "evidence": "Evidence", "question": "Review question", "why": "Why this diagram", "zoom": "Zoom in", "out": "Zoom out", "reset": "Reset", "element": "Element", "status": "Status", "step": "Step", "planned": "Planned", "actual": "Actual", "result": "Result", "note": "Note", "source": "Source", "claim": "Supported claim", "confidence": "Confidence", "kind": "Kind", "empty": "No items", "help": "Drag to pan, scroll to zoom, and select an element for details.", "footer": "This report is bounded by the cited evidence and inspection scope."},
}


def s(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def err(message):
    raise ValueError(message)


def expect_string(obj, key, where, required=True):
    value = obj.get(key)
    if required and (not isinstance(value, str) or not value.strip()):
        err(f"{where}.{key}: non-empty string required")
    if value is not None and not isinstance(value, str):
        err(f"{where}.{key}: string required")


def validate(report):
    if not isinstance(report, dict):
        err("report: object required")
    for field in ("title", "language", "phase", "repository", "baseline", "scope", "summary"):
        expect_string(report, field, "report")
    if report["phase"] not in {"plan", "explain", "audit", "combined"}:
        err("report.phase: expected plan, explain, audit, or combined")
    for field in ("decisions", "unknowns", "evidence", "diagrams", "audit"):
        if not isinstance(report.get(field), list):
            err(f"report.{field}: array required")
    for field in ("decisions", "unknowns"):
        if any(not isinstance(v, str) for v in report[field]):
            err(f"report.{field}: strings required")
    evidence = {}
    for i, item in enumerate(report["evidence"]):
        where = f"evidence[{i}]"
        if not isinstance(item, dict):
            err(f"{where}: object required")
        for field in ("id", "kind", "claim", "confidence"):
            expect_string(item, field, where)
        if item["id"] in evidence:
            err(f"{where}.id: duplicate {item['id']}")
        if item["kind"] not in EVIDENCE_KINDS or item["confidence"] not in CONFIDENCES:
            err(f"{where}: invalid kind or confidence")
        for field in ("path", "symbol", "lines"):
            expect_string(item, field, where, required=False)
        if item["kind"] in {"code", "test"} and not item.get("path"):
            err(f"{where}.path: required for code/test evidence")
        evidence[item["id"]] = item

    def check_element(item, where, require_status=True):
        if not isinstance(item, dict):
            err(f"{where}: object required")
        if require_status:
            expect_string(item, "status", where)
            if item["status"] not in STATUSES:
                err(f"{where}.status: invalid status")
        refs = item.get("evidence", [])
        if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
            err(f"{where}.evidence: array of IDs required")
        for ref in refs:
            if ref not in evidence:
                err(f"{where}.evidence: unknown ID {ref}")
        if item.get("status") == "implemented" and not any(evidence[r]["kind"] in {"code", "observation"} for r in refs):
            err(f"{where}: implemented element requires code or observation evidence")
        if item.get("status") in {"planned", "changed", "missing", "unknown"} and not refs:
            err(f"{where}: status {item['status']} requires evidence")
        expect_string(item, "detail", where, required=False)

    diagram_ids = set()
    for i, diagram in enumerate(report["diagrams"]):
        where = f"diagrams[{i}]"
        if not isinstance(diagram, dict):
            err(f"{where}: object required")
        for field in ("id", "type", "title", "question", "reason"):
            expect_string(diagram, field, where)
        if diagram["id"] in diagram_ids:
            err(f"{where}.id: duplicate")
        diagram_ids.add(diagram["id"])
        if diagram["type"] not in TYPES:
            err(f"{where}.type: must be one of {', '.join(sorted(TYPES))}")
        if diagram["type"] == "sequence":
            parts = diagram.get("participants")
            messages = diagram.get("messages")
            if not isinstance(parts, list) or not parts or not isinstance(messages, list):
                err(f"{where}: participants and messages arrays required")
            ids = set()
            for j, part in enumerate(parts):
                pwhere = f"{where}.participants[{j}]"
                check_element(part, pwhere)
                for field in ("id", "label"):
                    expect_string(part, field, pwhere)
                if part["id"] in ids:
                    err(f"{pwhere}.id: duplicate")
                ids.add(part["id"])
            for j, msg in enumerate(messages):
                mwhere = f"{where}.messages[{j}]"
                check_element(msg, mwhere)
                for field in ("from", "to", "label"):
                    expect_string(msg, field, mwhere)
                if msg["from"] not in ids or msg["to"] not in ids:
                    err(f"{mwhere}: unknown participant")
                if msg.get("style", "call") not in {"call", "return", "async"}:
                    err(f"{mwhere}.style: invalid")
        else:
            nodes, edges = diagram.get("nodes"), diagram.get("edges")
            if not isinstance(nodes, list) or not nodes or not isinstance(edges, list):
                err(f"{where}: nodes and edges arrays required")
            ids = set()
            for j, node in enumerate(nodes):
                nwhere = f"{where}.nodes[{j}]"
                check_element(node, nwhere)
                for field in ("id", "label"):
                    expect_string(node, field, nwhere)
                if node["id"] in ids:
                    err(f"{nwhere}.id: duplicate")
                ids.add(node["id"])
                if diagram["type"] == "er":
                    fields = node.get("fields", [])
                    if not isinstance(fields, list):
                        err(f"{nwhere}.fields: array required")
                    for k, f in enumerate(fields):
                        if not isinstance(f, dict):
                            err(f"{nwhere}.fields[{k}]: object required")
                        expect_string(f, "name", f"{nwhere}.fields[{k}]")
            for j, edge in enumerate(edges):
                ewhere = f"{where}.edges[{j}]"
                check_element(edge, ewhere)
                for field in ("from", "to", "label"):
                    expect_string(edge, field, ewhere)
                if edge["from"] not in ids or edge["to"] not in ids:
                    err(f"{ewhere}: unknown node")
                if diagram["type"] == "er" and edge.get("cardinality") is not None and edge["cardinality"] not in {"||--||", "||--o{", "||--|{", "|o--o{", "|o--||", "}o--o{", "}o..o{", "||..o{", "||..||"}:
                    err(f"{ewhere}.cardinality: unsupported Mermaid ER notation")
        if diagram["type"] == "c4" and diagram.get("level") not in {"context", "container", "component"}:
            err(f"{where}.level: context, container, or component required")
    for i, row in enumerate(report["audit"]):
        where = f"audit[{i}]"
        if not isinstance(row, dict):
            err(f"{where}: object required")
        for field in ("step", "planned", "actual", "verdict"):
            expect_string(row, field, where)
        if row["verdict"] not in VERDICTS:
            err(f"{where}.verdict: invalid")
        check_element(row, where, require_status=False)
        if row["verdict"] in {"matched", "changed"} and not any(evidence[r]["kind"] in {"code", "observation"} for r in row.get("evidence", [])):
            err(f"{where}: matched/changed requires code or observation evidence")
        expect_string(row, "note", where, required=False)
    return evidence


def badge(value):
    return f'<span class="badge {s(value)}">{s(value)}</span>'


def list_card(title, values, empty):
    body = "<ul>" + "".join(f"<li>{s(v)}</li>" for v in values) + "</ul>" if values else f'<p class="muted">{s(empty)}</p>'
    return f'<div class="card"><h3>{s(title)}</h3>{body}</div>'


def evidence_links(refs):
    return ", ".join(f'<a href="#ev-{s(ref)}">{s(ref)}</a>' for ref in refs) or "—"


def multiline_svg(text, x, y, css="node-label", max_chars=28, anchor="middle"):
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > max_chars:
            lines.append(current); current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    lines = lines[:3] or [""]
    offset = -(len(lines)-1)*8
    return f'<text class="{css}" x="{x}" y="{y+offset}" text-anchor="{anchor}" dominant-baseline="middle">' + "".join(f'<tspan x="{x}" dy="{0 if i == 0 else 18}">{s(line)}</tspan>' for i, line in enumerate(lines)) + "</text>"


def detail_key(diagram, kind, index):
    return f"{diagram['id']}:{kind}:{index}"


def svg_graph(diagram, details):
    nodes, edges = diagram["nodes"], diagram["edges"]
    depths = {node["id"]: 0 for node in nodes}
    for _ in range(max(1, len(nodes)-1)):
        changed = False
        for edge in edges:
            if edge["from"] != edge["to"] and depths[edge["to"]] < depths[edge["from"]] + 1:
                depths[edge["to"]] = min(len(nodes)-1, depths[edge["from"]] + 1)
                changed = True
        if not changed:
            break
    # Cycles can inflate depths; cap to a legible grid in source order.
    if max(depths.values(), default=0) > max(5, len(nodes)//2+1):
        depths = {node["id"]: i//3 for i, node in enumerate(nodes)}
    columns = {}
    for node in nodes:
        columns.setdefault(depths[node["id"]], []).append(node)
    max_rows = max((len(v) for v in columns.values()), default=1)
    row_gap = max(175, max((57 + 19 * len(node.get("fields", [])) + 25 for node in nodes), default=175))
    width = max(650, (max(columns, default=0)+1)*310+80)
    height = max(350, max_rows*row_gap+90)
    positions = {}
    for col, members in columns.items():
        for row, node in enumerate(members):
            x = 55 + col*310
            y = 55 + row*row_gap + (max_rows-len(members))*row_gap/2
            positions[node["id"]] = (x,y)
    parts = [f'<svg role="img" aria-label="{s(diagram["title"])}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arr-{s(diagram["id"])}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7990b1"/></marker></defs>']
    for i, edge in enumerate(edges):
        x1,y1 = positions[edge["from"]]; x2,y2 = positions[edge["to"]]
        if x1 == x2 and y1 == y2:
            path = f"M {x1+240} {y1+42} C {x1+300} {y1+20}, {x1+300} {y1+120}, {x1+240} {y1+90}"
        elif x1 == x2:
            path = f"M {x1+120} {y1+92} C {x1+120} {(y1+y2)/2}, {x2+120} {(y1+y2)/2}, {x2+120} {y2}"
        else:
            path = f"M {x1+240} {y1+45} C {(x1+x2+240)/2} {y1+45}, {(x1+x2+240)/2} {y2+45}, {x2} {y2+45}"
        key = detail_key(diagram,"edge",i)
        parts.append(f'<g class="node" data-status="{s(edge["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(edge["label"])}"><path class="edge" d="{path}" marker-end="url(#arr-{s(diagram["id"])})"/>')
        mx = (x1+x2+240)/2 if x1 != x2 else x1+135
        my = (y1+y2)/2+35
        parts.append(f'<text class="edge-label" x="{mx}" y="{my}" text-anchor="middle">{s(edge["label"][:45])}</text></g>')
        details[detail_key(diagram,"edge",i)] = {"label":edge["label"],"detail":edge.get("detail", ""),"status":edge["status"],"evidence":edge.get("evidence", [])}
    for i, node in enumerate(nodes):
        x,y = positions[node["id"]]
        key = detail_key(diagram,"node",i)
        details[key] = {"label":node["label"],"detail":node.get("detail", ""),"status":node["status"],"evidence":node.get("evidence", [])}
        h = 112 if diagram["type"] == "er" and node.get("fields") else 92
        fields = node.get("fields", [])
        if fields:
            h = max(112, 57+len(fields)*19)
        parts.append(f'<g class="node" data-status="{s(node["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(node["label"])}">')
        if node.get("kind") == "decision" and diagram["type"] == "flowchart":
            parts.append(f'<path class="shape" d="M {x+120} {y} L {x+240} {y+46} L {x+120} {y+92} L {x} {y+46} Z"/>')
        else:
            radius = 30 if node.get("kind") in {"start","end"} else 13
            parts.append(f'<rect class="shape" x="{x}" y="{y}" width="240" height="{h}" rx="{radius}"/>')
        parts.append(multiline_svg(node["label"],x+120,y+32,max_chars=28))
        if fields:
            parts.append(f'<path d="M {x+10} {y+57} H {x+230}" stroke="#52617c"/>')
            for k, field in enumerate(fields):
                label = f"{field.get('key','')} {field['name']} {field.get('type','')}".strip()
                parts.append(f'<text class="field" x="{x+18}" y="{y+77+k*19}" direction="ltr">{s(label[:34])}</text>')
        elif node.get("detail"):
            parts.append(f'<text class="node-sub" x="{x+120}" y="{y+70}" text-anchor="middle">{s(node["detail"][:35])}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def svg_sequence(diagram, details):
    parts_data = diagram["participants"]
    messages = diagram["messages"]
    width = max(650, len(parts_data)*230+80)
    height = max(350, 175+len(messages)*95)
    xs = {p["id"]: 155+i*230 for i,p in enumerate(parts_data)}
    parts = [f'<svg role="img" aria-label="{s(diagram["title"])}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arr-{s(diagram["id"])}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7990b1"/></marker></defs>']
    for i,p in enumerate(parts_data):
        x=xs[p["id"]]; key=detail_key(diagram,"participant",i)
        details[key]={"label":p["label"],"detail":p.get("detail", ""),"status":p["status"],"evidence":p.get("evidence", [])}
        parts.append(f'<line class="seq-life" x1="{x}" x2="{x}" y1="90" y2="{height-30}"/><g class="node" data-status="{s(p["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(p["label"])}"><rect class="shape" x="{x-95}" y="30" width="190" height="60" rx="12"/>{multiline_svg(p["label"],x,60,max_chars=22)}</g>')
    for i,m in enumerate(messages):
        x1,x2=xs[m["from"]],xs[m["to"]]; y=135+i*95
        cls="edge " + s(m.get("style","call"))
        if x1 == x2:
            path=f"M {x1} {y} C {x1+105} {y-24}, {x1+105} {y+42}, {x1} {y+42}"
        else:
            path=f"M {x1} {y} L {x2} {y}"
        key=detail_key(diagram,"message",i)
        details[key]={"label":m["label"],"detail":m.get("detail", ""),"status":m["status"],"evidence":m.get("evidence", [])}
        parts.append(f'<g class="node" data-status="{s(m["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(m["label"])}"><path class="{cls}" d="{path}" marker-end="url(#arr-{s(diagram["id"])})"/><text class="edge-label" x="{(x1+x2)/2}" y="{y-12}" text-anchor="middle">{s(m["label"][:60])}</text><circle cx="{x1}" cy="{y}" r="5" fill="#7dd3fc"/></g>')
    parts.append("</svg>")
    return "".join(parts)


def render_html(report, template):
    ar = report["language"].lower().startswith("ar")
    u = UI["ar" if ar else "en"]
    details = {}
    header = f'<div class="eyebrow">Code Flow Audit · {s(report["phase"])}</div><h1>{s(report["title"])}</h1><p class="summary">{s(report["summary"])}</p><div class="meta"><span class="pill">{s(report["repository"])}</span><span class="pill">{s(u["phase"])}: {s(report["phase"])}</span><span class="pill">{s(report["baseline"])}</span></div>'
    content = f'<section class="grid">{list_card(u["decisions"],report["decisions"],u["empty"])}{list_card(u["unknowns"],report["unknowns"],u["empty"])}<div class="card"><h3>{s(u["scope"])}</h3><p>{s(report["scope"])}</p></div></section>'
    content += f'<section id="diagrams"><h2>{s(u["diagrams"])}</h2>'
    if not report["diagrams"]:
        content += f'<p class="muted">{s(u["empty"])}</p>'
    for diagram in report["diagrams"]:
        svg = svg_sequence(diagram,details) if diagram["type"] == "sequence" else svg_graph(diagram,details)
        content += f'<article class="diagram"><div class="diagram-head"><div><div class="eyebrow">{s(diagram["type"])}' + (f' · {s(diagram["level"])}' if diagram["type"] == "c4" else "") + f'</div><h3>{s(diagram["title"])}</h3><p><strong>{s(u["question"])}:</strong> {s(diagram["question"])}</p><p class="muted"><strong>{s(u["why"])}:</strong> {s(diagram["reason"])}</p></div><div class="toolbar"><button data-action="in" aria-label="{s(u["zoom"])}">+</button><button data-action="out" aria-label="{s(u["out"])}">−</button><button data-action="reset" aria-label="{s(u["reset"])}">↺</button></div></div><div class="viewport">{svg}</div><p class="muted">{s(u["help"])}</p></article>'
    content += "</section>"
    if report["audit"]:
        content += f'<section id="audit"><h2>{s(u["audit"])}</h2><div class="tablewrap"><table><thead><tr><th>{s(u["step"])}</th><th>{s(u["planned"])}</th><th>{s(u["actual"])}</th><th>{s(u["result"])}</th><th>{s(u["note"])}</th><th>{s(u["evidence"])}</th></tr></thead><tbody>'
        for row in report["audit"]:
            content += f'<tr><td>{s(row["step"])}</td><td>{s(row["planned"])}</td><td>{s(row["actual"])}</td><td>{badge(row["verdict"])}</td><td>{s(row.get("note",""))}</td><td>{evidence_links(row.get("evidence",[]))}</td></tr>'
        content += "</tbody></table></div></section>"
    content += f'<section id="evidence"><h2>{s(u["evidence"])}</h2><div class="tablewrap"><table><thead><tr><th>ID</th><th>{s(u["source"])}</th><th>{s(u["claim"])}</th><th>{s(u["confidence"])}</th></tr></thead><tbody>'
    for e in report["evidence"]:
        location = " · ".join(filter(None,[e.get("path",""),e.get("symbol",""),e.get("lines","")])) or e["kind"]
        content += f'<tr id="ev-{s(e["id"])}"><td><strong>{s(e["id"])}</strong></td><td><code>{s(location)}</code><br><span class="muted">{s(e["kind"])}</span></td><td>{s(e["claim"])}</td><td>{badge(e["confidence"])}</td></tr>'
    content += "</tbody></table></div></section>"
    data = json.dumps({"evidence":report["evidence"],"details":details},ensure_ascii=False,separators=(",",":"))
    data = data.replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    replacements = {"__LANG__":s(report["language"]),"__DIR__":"rtl" if ar else "ltr","__TITLE__":s(report["title"]),"__SKIP__":"انتقل للمحتوى" if ar else "Skip to content","__DETAIL_LABEL__":"تفاصيل عنصر الرسم" if ar else "Diagram detail","__CLOSE__":"إغلاق" if ar else "Close","__HEADER__":header,"__CONTENT__":content,"__FOOTER__":s(u["footer"]),"__DATA__":data}
    return re.sub(r"__(?:LANG|DIR|TITLE|SKIP|DETAIL_LABEL|CLOSE|HEADER|CONTENT|FOOTER|DATA)__", lambda match: replacements[match.group()], template)


def mermaid_text(value):
    return str(value).replace('"', "'").replace("\n", " ").replace("`", "'")


def render_mermaid(diagram):
    kind = diagram["type"]
    if kind == "sequence":
        out=["sequenceDiagram"]
        aliases={p["id"]:f"P{i+1}" for i,p in enumerate(diagram["participants"])}
        for p in diagram["participants"]:
            out.append(f"    participant {aliases[p['id']]} as {mermaid_text(p['label'])}")
        for m in diagram["messages"]:
            arrow={"call":"->>","return":"-->>","async":"-)"}.get(m.get("style","call"),"->>")
            out.append(f"    {aliases[m['from']]}{arrow}{aliases[m['to']]}: {mermaid_text(m['label'])}")
        return "\n".join(out)
    if kind == "state":
        ids={n["id"]:f"S{i+1}" for i,n in enumerate(diagram["nodes"])}
        out=["stateDiagram-v2"]
        for n in diagram["nodes"]:
            out.append(f'    state "{mermaid_text(n["label"])}" as {ids[n["id"]]}')
        for e in diagram["edges"]:
            out.append(f'    {ids[e["from"]]} --> {ids[e["to"]]}: {mermaid_text(e["label"])}')
        return "\n".join(out)
    if kind == "er":
        ids={n["id"]:f"E{i+1}" for i,n in enumerate(diagram["nodes"])}
        out=["erDiagram"]
        for n in diagram["nodes"]:
            alias=mermaid_text(n["label"])
            fields=n.get("fields",[])
            if fields:
                out.append(f'    {ids[n["id"]]}["{alias}"] {{')
                for f in fields:
                    typ=str(f.get("type", ""))
                    name=str(f["name"])
                    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_()\[\]-]*",typ) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_\-]*",name):
                        key=f.get("key", "")
                        key=f" {key}" if key in {"PK","FK","UK"} else ""
                        out.append(f"        {typ} {name}{key}")
                out.append("    }")
            else:
                out.append(f'    {ids[n["id"]]}["{alias}"]')
        for e in diagram["edges"]:
            if e.get("cardinality"):
                out.append(f'    {ids[e["from"]]} {e["cardinality"]} {ids[e["to"]]} : "{mermaid_text(e["label"])}"')
            else:
                out.append(f'    %% Relationship omitted: cardinality unverified; see evidence table for {ids[e["from"]]} to {ids[e["to"]]}')
        return "\n".join(out)
    ids={n["id"]:f"N{i+1}" for i,n in enumerate(diagram["nodes"])}
    out=["flowchart LR" if kind in {"c4","er"} else "flowchart TD"]
    for n in diagram["nodes"]:
        label=mermaid_text(n["label"])
        if kind=="er" and n.get("fields"):
            label += "<br/>" + "<br/>".join(mermaid_text(f["name"]) for f in n["fields"])
        out.append(f'    {ids[n["id"]]}["{label}"]')
    for e in diagram["edges"]:
        out.append(f'    {ids[e["from"]]} -->|"{mermaid_text(e["label"])}"| {ids[e["to"]]}')
    return "\n".join(out)


def md_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_md(report):
    u=UI["ar" if report["language"].lower().startswith("ar") else "en"]
    out=[f'# {report["title"]}',"",f'**{u["phase"]}:** {report["phase"]}  ',f'**{u["repository"]}:** {report["repository"]}  ',f'**{u["baseline"]}:** {report["baseline"]}',"",report["summary"],"",f'**{u["scope"]}:** {report["scope"]}',""]
    for key in ("decisions","unknowns"):
        out += [f"## {u[key]}",""]
        out += [f"- {v}" for v in report[key]] or [f'- {u["empty"]}']
        out.append("")
    out += [f'## {u["diagrams"]}',""]
    for d in report["diagrams"]:
        out += [f'### {d["title"]} ({d["type"]}' + (f', {d["level"]}' if d["type"]=="c4" else "") + ")", "",f'**{u["question"]}:** {d["question"]}  ',f'**{u["why"]}:** {d["reason"]}',"","```mermaid",render_mermaid(d),"```","",f'| {u["element"]} | {u["status"]} | {u["evidence"]} |',"| --- | --- | --- |"]
        elems = [(x.get("label",x.get("id","")),x) for x in d.get("nodes",d.get("participants",[]))]
        elems += [(f"{x['from']} → {x['to']}: {x['label']}",x) for x in d.get("edges",d.get("messages",[]))]
        out += [f'| {md_cell(name)} | {x["status"]} | {", ".join(x.get("evidence",[])) or "—"} |' for name,x in elems]
        out.append("")
    if report["audit"]:
        out += [f'## {u["audit"]}',"",f'| {u["step"]} | {u["planned"]} | {u["actual"]} | {u["result"]} | {u["note"]} | {u["evidence"]} |',"| --- | --- | --- | --- | --- | --- |"]
        out += ["| " + " | ".join(md_cell(row.get(k,"")) for k in ("step","planned","actual","verdict","note")) + " | " + ", ".join(row.get("evidence",[])) + " |" for row in report["audit"]]
        out.append("")
    out += [f'## {u["evidence"]}',"",f'| ID | {u["kind"]} | {u["source"]} | {u["claim"]} | {u["confidence"]} |',"| --- | --- | --- | --- | --- |"]
    for e in report["evidence"]:
        location=" · ".join(filter(None,[e.get("path",""),e.get("symbol",""),e.get("lines","")])) or "—"
        out.append("| " + " | ".join(md_cell(v) for v in (e["id"],e["kind"],location,e["claim"],e["confidence"])) + " |")
    out.append("")
    return "\n".join(out)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path,help="UTF-8 report JSON")
    parser.add_argument("-o","--output",type=Path,help="Output .html (default) or .md")
    parser.add_argument("--check",action="store_true",help="Validate without writing")
    args=parser.parse_args(argv)
    try:
        report=json.loads(args.input.read_text(encoding="utf-8"))
        validate(report)
        if args.check:
            print(f"Valid report: {args.input}")
            return 0
        output=args.output or args.input.with_suffix(".html")
        if output.suffix.lower() not in {".html",".md"}:
            err("output must end in .html or .md")
        if output.suffix.lower()==".html":
            template=(Path(__file__).resolve().parent.parent/"assets"/"report.html").read_text(encoding="utf-8")
            rendered=render_html(report,template)
        else:
            rendered=render_md(report)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(rendered,encoding="utf-8")
        print(output)
        return 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(f"render_report: {exc}",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
