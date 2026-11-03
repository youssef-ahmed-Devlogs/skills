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
    "ar": {"skip": "انتقل للمحتوى", "detail": "تفاصيل عنصر الرسم", "close": "إغلاق", "n_diagrams": "رسوم", "n_evidence": "دليل", "n_unknowns": "نقاط لم تُحسم", "n_gaps": "فروق عن الخطة", "as_text": "اقرأ الرسمة كقائمة", "used_in": "مستخدم في", "theme": "المظهر", "auto": "تلقائي", "light": "فاتح", "dark": "داكن", "contents": "المحتويات", "overview": "النطاق والقرارات", "statuses": "الحالات", "linked": "الأدلة المرتبطة", "full": "ملء الشاشة", "report": "تقرير الرسوم", "phase": "المرحلة", "repository": "المشروع", "baseline": "المرجع", "scope": "نطاق الفحص", "decisions": "القرارات", "unknowns": "ما لم يُحسم", "diagrams": "الرسوم", "audit": "مقارنة الخطة بالتنفيذ", "evidence": "الأدلة", "question": "سؤال المراجعة", "why": "سبب الاختيار", "zoom": "تكبير", "out": "تصغير", "reset": "إعادة الضبط", "element": "العنصر", "status": "الحالة", "step": "الخطوة", "planned": "المخطط", "actual": "المنفذ", "result": "النتيجة", "note": "ملاحظة", "source": "المصدر", "claim": "ما يثبته", "confidence": "الثقة", "kind": "النوع", "empty": "لا توجد عناصر", "help": "اسحب للتنقل، وكبّر بـ Ctrl مع عجلة الفأرة أو بالأزرار، واضغط على عنصر للتفاصيل.", "footer": "تقرير مبني على الأدلة المذكورة؛ حدود الفحص موضحة أعلاه."},
    "en": {"skip": "Skip to content", "detail": "Diagram detail", "close": "Close", "n_diagrams": "diagrams", "n_evidence": "evidence items", "n_unknowns": "open questions", "n_gaps": "differences from plan", "as_text": "Read the diagram as a list", "used_in": "Used in", "theme": "Theme", "auto": "Auto", "light": "Light", "dark": "Dark", "contents": "Contents", "overview": "Scope and decisions", "statuses": "Statuses", "linked": "Linked evidence", "full": "Full screen", "report": "Diagram report", "phase": "Phase", "repository": "Repository", "baseline": "Baseline", "scope": "Inspection scope", "decisions": "Decisions", "unknowns": "Unknowns", "diagrams": "Diagrams", "audit": "Plan vs implementation", "evidence": "Evidence", "question": "Review question", "why": "Why this diagram", "zoom": "Zoom in", "out": "Zoom out", "reset": "Reset", "element": "Element", "status": "Status", "step": "Step", "planned": "Planned", "actual": "Actual", "result": "Result", "note": "Note", "source": "Source", "claim": "Supported claim", "confidence": "Confidence", "kind": "Kind", "empty": "No items", "help": "Drag to pan, zoom with Ctrl and the scroll wheel or the buttons, and select an element for details.", "footer": "This report is bounded by the cited evidence and inspection scope."},
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
                for field in ("from", "to"):
                    expect_string(edge, field, ewhere)
                expect_string(edge, "label", ewhere, required=False)
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


TERMS = {
    "ar": {
        "plan": "خطة", "explain": "شرح", "audit": "مراجعة", "combined": "خطة ومراجعة",
        "implemented": "منفّذ", "planned": "مخطط", "changed": "متغيّر", "missing": "ناقص", "unknown": "غير معروف", "context": "سياق",
        "verified": "متحقق منه", "inferred": "مستنتج", "matched": "مطابق", "unverified": "لم يُتحقق منه",
        "code": "كود", "test": "تست", "request": "طلب", "assumption": "افتراض", "observation": "ملاحظة",
        "flowchart": "مخطط تدفق", "sequence": "تسلسل", "c4": "معمارية C4", "er": "جداول ER", "state": "حالات",
        "container": "حاويات", "component": "مكوّنات",
    },
    "en": {"c4": "C4", "er": "ER"},
}


def term(value, lang):
    """A fixed value of the schema, such as a status, in the report's language."""
    return TERMS[lang].get(value, value)


def badge(value, lang="en"):
    return f'<span class="badge {s(value)}"><i></i>{s(term(value, lang))}</span>'


RTL_LETTER = re.compile(r"[֐-ࣿיִ-﷿ﹰ-﻿]")
LTR_LETTER = re.compile(r"[A-Za-zÀ-ɏͰ-ϿЀ-ӿ]")


def text_dir(text):
    """The direction of the first strong letter, as dir="auto" picks it in HTML."""
    for ch in str(text):
        if RTL_LETTER.match(ch):
            return "rtl"
        if LTR_LETTER.match(ch):
            return "ltr"
    return "ltr"


def text_width(text, size, bold=False):
    # A rough width from the font size. The renderer has no font metrics, so it errs wide.
    width = 0.0
    for ch in str(text):
        if ch == " ":
            width += 0.3
        elif RTL_LETTER.match(ch):
            width += 0.52
        elif ch.isupper() or ch in "mwMW@%":
            width += 0.68
        elif ch in "il.,:;!|'()[]":
            width += 0.3
        else:
            width += 0.57
    return width * size * (1.06 if bold else 1)


def wrap(text, max_width, size, bold=False):
    lines, current = [], ""
    for word in str(text).split():
        candidate = f"{current} {word}".strip()
        if current and text_width(candidate, size, bold) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def svg_lines(lines, cx, top, css, size, line_height, anchor="middle", fit=None):
    """Text lines, each with its own direction, so a line that starts with English keeps its order."""
    out = []
    for i, line in enumerate(lines):
        limit = f' data-fit="{fit:.0f}"' if fit else ""
        out.append(f'<text class="{css}" x="{cx:.1f}" y="{top + i*line_height + size*0.8:.1f}" text-anchor="{anchor}" direction="{text_dir(line)}"{limit}>{s(line)}</text>')
    return "".join(out)


def detail_key(diagram, kind, index):
    return f"{diagram['id']}:{kind}:{index}"


NODE_LINE = 19
LABEL_SIZE = 12
LABEL_LINE = 15
FIELD_LINE = 19
H_GAP = 48
MAX_ROW = 4
MARGIN = 40


def size_node(node, diagram_type):
    decision = diagram_type == "flowchart" and node.get("kind") == "decision"
    inset = 64 if decision else 36
    fields = node.get("fields", []) if diagram_type == "er" else []
    field_texts = [f"{f.get('key', '')} {f['name']} {f.get('type', '')}{' NULL' if f.get('nullable') is True else ''}".strip() for f in fields]
    base = 300 if decision else 260
    label = wrap(node["label"], base - inset, 14, bold=True)
    widest = max([text_width(x, 14, True) for x in label] + [text_width(x, 12.5) for x in field_texts] + [0])
    width = max(240 if decision else 180, min(base, widest + inset))
    # The detail wraps to the width the label needs, so a long detail does not widen the node.
    detail = [] if fields else wrap(node.get("detail", ""), width - inset, 11.5) if node.get("detail") else []
    height = 24 + len(label)*NODE_LINE + 20
    if detail:
        height += 4 + len(detail)*16
    if fields:
        height += 12 + len(fields)*FIELD_LINE
    if decision:
        height = max(height + 8, 78)
    return {"w": width, "h": max(height, 60), "label": label, "detail": detail, "fields": field_texts, "decision": decision}


def layered_layout(nodes, edges, diagram_type):
    """A small Sugiyama layout: layers top to bottom, back edges on a side lane, fewer crossings."""
    ids = [n["id"] for n in nodes]
    index = {nid: i for i, nid in enumerate(ids)}
    sizes = {n["id"]: size_node(n, diagram_type) for n in nodes}

    # Back edges: found by a depth-first walk in source order, so the author's order decides.
    outgoing = {nid: [] for nid in ids}
    incoming_count = {nid: 0 for nid in ids}
    for i, e in enumerate(edges):
        outgoing[e["from"]].append(i)
        if e["from"] != e["to"]:
            incoming_count[e["to"]] += 1
    state, back = {}, set()

    def walk(u):
        state[u] = 1
        for i in outgoing[u]:
            v = edges[i]["to"]
            if state.get(v) == 1:
                back.add(i)
            elif v not in state:
                walk(v)
        state[u] = 2

    for nid in [n for n in ids if incoming_count[n] == 0] + ids:
        if nid not in state:
            walk(nid)
    forward = [i for i, e in enumerate(edges) if i not in back and e["from"] != e["to"]]

    # Longest-path layers.
    layer = {nid: 0 for nid in ids}
    for _ in range(len(ids)):
        changed = False
        for i in forward:
            a, b = edges[i]["from"], edges[i]["to"]
            if layer[b] < layer[a] + 1:
                layer[b] = layer[a] + 1
                changed = True
        if not changed:
            break

    # A wide layer pushes some of its sources one layer up, so the diagram stays readable.
    preds = {nid: set() for nid in ids}
    for i in forward:
        preds[edges[i]["to"]].add(edges[i]["from"])
    for _ in range(len(ids)):
        counts = {}
        for nid in ids:
            counts[layer[nid]] = counts.get(layer[nid], 0) + 1
        crowded = [k for k, c in sorted(counts.items()) if c > MAX_ROW and sum(1 for n in ids if layer[n] == k and not preds[n]) > 1]
        if not crowded:
            break
        k = crowded[0]
        sources = sorted((n for n in ids if layer[n] == k and not preds[n]), key=lambda n: (len(outgoing[n]), index[n]))
        excess = counts[k] - MAX_ROW
        if k == 0:
            for n in ids:
                layer[n] += 1
            k = 1
        for n in sources[:min(len(sources) - 1, excess)]:
            layer[n] = k - 1

    # A dummy point per layer that a long edge crosses, so it bends around nodes.
    width = {nid: sizes[nid]["w"] for nid in ids}
    chains, order_key = {}, {nid: float(index[nid]) for nid in ids}
    for i in forward:
        a, b = edges[i]["from"], edges[i]["to"]
        chain = [a]
        for k in range(layer[a] + 1, layer[b]):
            d = f"__d{i}_{k}"
            layer[d] = k
            width[d] = 14
            order_key[d] = index[a] + 0.5
            chain.append(d)
        chain.append(b)
        chains[i] = chain
    layers = {}
    for nid in sorted(layer, key=lambda n: order_key[n]):
        layers.setdefault(layer[nid], []).append(nid)
    depth = max(layers) + 1
    rows = [layers.get(k, []) for k in range(depth)]
    up, down = {n: [] for n in layer}, {n: [] for n in layer}
    for chain in chains.values():
        for a, b in zip(chain, chain[1:]):
            down[a].append(b)
            up[b].append(a)

    def crossings(rows):
        total = 0
        for k in range(len(rows) - 1):
            pos = {n: i for i, n in enumerate(rows[k + 1])}
            pairs = [(i, pos[b]) for i, a in enumerate(rows[k]) for b in down[a]]
            total += sum(1 for x in range(len(pairs)) for y in range(x + 1, len(pairs)) if (pairs[x][0] - pairs[y][0]) * (pairs[x][1] - pairs[y][1]) < 0)
        return total

    best, best_cross = [list(r) for r in rows], crossings(rows)
    for sweep in range(12):
        span = range(1, depth) if sweep % 2 == 0 else range(depth - 2, -1, -1)
        for k in span:
            ref = rows[k - 1] if sweep % 2 == 0 else rows[k + 1]
            pos = {n: i for i, n in enumerate(ref)}
            links = up if sweep % 2 == 0 else down
            current = {n: i for i, n in enumerate(rows[k])}
            rows[k].sort(key=lambda n: sum(pos[m] for m in links[n]) / len(links[n]) if links[n] else current[n])
        c = crossings(rows)
        if c < best_cross:
            best, best_cross = [list(r) for r in rows], c
    rows = best

    # X: start packed, then pull each node toward its neighbours while keeping the gaps.
    x = {}
    for row in rows:
        left = 0.0
        for n in row:
            x[n] = left
            left += width[n] + H_GAP

    def center(n):
        return x[n] + width[n] / 2

    def place(row, wanted):
        lefts = [wanted[n] - width[n] / 2 for n in row]
        fwd = list(lefts)
        for i in range(1, len(row)):
            fwd[i] = max(fwd[i], fwd[i - 1] + width[row[i - 1]] + H_GAP)
        bwd = list(lefts)
        for i in range(len(row) - 2, -1, -1):
            bwd[i] = min(bwd[i], bwd[i + 1] - width[row[i]] - H_GAP)
        for i, n in enumerate(row):
            x[n] = (fwd[i] + bwd[i]) / 2

    for sweep in range(16):
        span = range(depth) if sweep % 2 == 0 else range(depth - 1, -1, -1)
        for k in span:
            wanted = {}
            for n in rows[k]:
                near = up[n] + down[n]
                wanted[n] = sum(center(m) for m in near) / len(near) if near else center(n)
            place(rows[k], wanted)
    shift = min(x.values())
    for n in x:
        x[n] -= shift

    # Y: one band per layer; the gap below a band fits the labels of the edges that leave it.
    label_lines = {i: wrap(e.get("label", ""), 150, LABEL_SIZE) if e.get("label") else [] for i, e in enumerate(edges)}
    band_h = [max((sizes[n]["h"] for n in row if n in sizes), default=20) for row in rows]
    gaps = []
    for k in range(depth):
        leaving = [i for i in forward if layer[edges[i]["from"]] == k]
        most = max((len(label_lines[i]) for i in leaving), default=0)
        crowd = max(0, sum(1 for i in leaving if label_lines[i]) - 2)
        gaps.append(56 + most * LABEL_LINE + (12 if most else 0) + crowd * 12)
    band_top, top = [], 0.0
    for k in range(depth):
        band_top.append(top)
        top += band_h[k] + gaps[k]
    y = {}
    for k, row in enumerate(rows):
        for n in row:
            h = sizes[n]["h"] if n in sizes else band_h[k]
            y[n] = band_top[k] + (band_h[k] - h) / 2
    height = band_top[-1] + band_h[-1]
    return {"sizes": sizes, "x": x, "y": y, "width": width, "chains": chains, "back": back, "label_lines": label_lines, "band_h": band_h, "band_top": band_top, "layer": layer, "height": height}


def cubic(p0, p1, p2, p3, t):
    a = (1 - t) ** 3
    b = 3 * (1 - t) ** 2 * t
    c = 3 * (1 - t) * t * t
    d = t ** 3
    return (a*p0[0] + b*p1[0] + c*p2[0] + d*p3[0], a*p0[1] + b*p1[1] + c*p2[1] + d*p3[1])


def overlaps(a, b, pad=4):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def svg_graph(diagram, details, rtl=False):
    nodes, edges = diagram["nodes"], diagram["edges"]
    L = layered_layout(nodes, edges, diagram["type"])
    sizes, x, y, width = L["sizes"], L["x"], L["y"], L["width"]
    real = [n["id"] for n in nodes]
    content_w = max(x[n] + width[n] for n in x)
    box = {n: (x[n], y[n], x[n] + sizes[n]["w"], y[n] + sizes[n]["h"]) for n in real}

    # Ports: edges leave a node's bottom and enter its top, spread in the order of where they go.
    def spread(n, items):
        w = sizes[n]["w"]
        usable = max(0, w - (110 if sizes[n]["decision"] else 48))
        step = min(30, usable / max(1, len(items) - 1)) if len(items) > 1 else 0
        start = x[n] + w / 2 - step * (len(items) - 1) / 2
        return {key: start + i * step for i, key in enumerate(items)}

    out_ports, in_ports = {}, {}
    for n in real:
        leaving = sorted((i for i, c in L["chains"].items() if c[0] == n), key=lambda i: x[L["chains"][i][1]] + width[L["chains"][i][1]] / 2)
        arriving = sorted((i for i, c in L["chains"].items() if c[-1] == n), key=lambda i: x[L["chains"][i][-2]] + width[L["chains"][i][-2]] / 2)
        out_ports.update({(i, "out"): v for i, v in spread(n, leaving).items()})
        in_ports.update({(i, "in"): v for i, v in spread(n, arriving).items()})

    # Back edges and self loops run up a lane outside the nodes, on the nearer side.
    lanes, lane_count = {}, {"right": 0, "left": 0}
    for i in sorted(L["back"]) + [i for i, e in enumerate(edges) if e["from"] == e["to"]]:
        a = edges[i]["from"]
        side = "right" if x[a] + sizes[a]["w"] / 2 >= content_w / 2 else "left"
        lane_count[side] += 1
        lanes[i] = (side, lane_count[side])
    pad_left = 34 * lane_count["left"] + (60 if lane_count["left"] else 0)
    pad_right = 34 * lane_count["right"] + (60 if lane_count["right"] else 0)
    total_w = max(600, content_w + pad_left + pad_right + 2 * MARGIN)
    total_h = max(300, L["height"] + 2 * MARGIN)
    ox = (total_w - content_w - pad_left - pad_right) / 2 + pad_left
    oy = (total_h - L["height"]) / 2

    def X(v):
        v = v + ox
        return total_w - v if rtl else v

    def Y(v):
        return v + oy

    def P(pt):
        return f"{X(pt[0]):.1f} {Y(pt[1]):.1f}"

    placed = [box[n] for n in real]
    paths, labels = {}, {}
    for i, e in enumerate(edges):
        a, b = e["from"], e["to"]
        segments = []  # cubic segments in layout space, for drawing and label spots
        if i in lanes:
            side, k = lanes[i]
            ax = x[a] + sizes[a]["w"] if side == "right" else x[a]
            bx = x[b] + sizes[b]["w"] if side == "right" else x[b]
            lane_x = (content_w + 30 + 34 * k) if side == "right" else (-30 - 34 * k)
            ay, by = y[a] + sizes[a]["h"] / 2, y[b] + sizes[b]["h"] / 2
            if a == b:
                ay, by = y[a] + sizes[a]["h"] * 0.3, y[a] + sizes[a]["h"] * 0.7
            r = 14 if lane_x > ax else -14
            d = f"M {P((ax, ay))} L {P((lane_x - r, ay))} Q {P((lane_x, ay))} {P((lane_x, ay - 14 if by < ay else ay + 14))} L {P((lane_x, by + 14 if by < ay else by - 14))} Q {P((lane_x, by))} {P((lane_x - r, by))} L {P((bx, by))}"
            mid = (lane_x, (ay + by) / 2)
            spots = [mid, (lane_x, ay + (by - ay) * 0.3), (lane_x, ay + (by - ay) * 0.7)]
        else:
            chain = L["chains"][i]
            pts = [(out_ports[(i, "out")], y[a] + sizes[a]["h"])]
            for dmy in chain[1:-1]:
                k = L["layer"][dmy]
                cx = x[dmy] + width[dmy] / 2
                pts += [(cx, L["band_top"][k]), (cx, L["band_top"][k] + L["band_h"][k])]
            pts.append((in_ports[(i, "in")], y[b]))
            d = f"M {P(pts[0])}"
            for j in range(0, len(pts) - 1):
                p0, p3 = pts[j], pts[j + 1]
                if j % 2 == 1:  # straight run through a band
                    d += f" L {P(p3)}"
                    continue
                dy = (p3[1] - p0[1]) * 0.5
                p1, p2 = (p0[0], p0[1] + dy), (p3[0], p3[1] - dy)
                d += f" C {P(p1)}, {P(p2)}, {P(p3)}"
                segments.append((p0, p1, p2, p3))
            spots = []
            for seg in segments[:1] + segments[-1:] + segments[1:-1]:
                spots += [cubic(*seg, t) for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8, 0.12, 0.88)]
        paths[i] = d
        lines = L["label_lines"][i]
        if not lines:
            continue
        lw = max(text_width(t, LABEL_SIZE) for t in lines) + 14
        lh = len(lines) * LABEL_LINE + 6
        # The first free spot along the edge, then beside it; when none is free, the least covered one.
        tries = spots + [(sx + dx, sy) for sx, sy in spots[:3] for dx in (lw / 2 + 8, -lw / 2 - 8, lw + 16, -lw - 16)]
        choice, least = None, None
        for sx, sy in tries:
            cand = (sx - lw / 2, sy - lh / 2, sx + lw / 2, sy + lh / 2)
            covered = sum(max(0, min(cand[2], o[2]) - max(cand[0], o[0]) + 8) * max(0, min(cand[3], o[3]) - max(cand[1], o[1]) + 8) for o in placed if overlaps(cand, o))
            if covered == 0:
                choice = cand
                break
            if least is None or covered < least[0]:
                least = (covered, cand)
        choice = choice or least[1]
        placed.append(choice)
        labels[i] = (choice, lines)

    marker = f'arr-{s(diagram["id"])}'
    parts = [f'<svg role="group" aria-label="{s(diagram["title"])}" viewBox="0 0 {total_w:.0f} {total_h:.0f}" width="{total_w:.0f}" height="{total_h:.0f}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="arrowhead" d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>']
    for i, e in enumerate(edges):
        key = detail_key(diagram, "edge", i)
        details[key] = {"label": e.get("label", ""), "detail": e.get("detail", ""), "status": e["status"], "evidence": e.get("evidence", [])}
        parts.append(f'<g class="node edge-group" data-status="{s(e["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(e.get("label") or e["from"] + " → " + e["to"])}"><path class="edge-hit" d="{paths[i]}"/><path class="edge" d="{paths[i]}" marker-end="url(#{marker})"/></g>')
    for i, (rect, lines) in labels.items():
        key = detail_key(diagram, "edge", i)
        left = min(X(rect[0]), X(rect[2]))
        cx = left + (rect[2] - rect[0]) / 2
        parts.append(f'<g class="node" data-status="{s(edges[i]["status"])}" data-key="{s(key)}"><rect class="edge-label-bg" x="{left:.1f}" y="{Y(rect[1]):.1f}" width="{rect[2]-rect[0]:.1f}" height="{rect[3]-rect[1]:.1f}" rx="5"/>{svg_lines(lines, cx, Y(rect[1]) + 3, "edge-label", LABEL_SIZE, LABEL_LINE, fit=rect[2] - rect[0] - 8)}</g>')
    for i, node in enumerate(nodes):
        n, z = node["id"], sizes[node["id"]]
        key = detail_key(diagram, "node", i)
        details[key] = {"label": node["label"], "detail": node.get("detail", ""), "status": node["status"], "evidence": node.get("evidence", [])}
        w, h = z["w"], z["h"]
        left = min(X(x[n]), X(x[n] + w))
        top = Y(y[n])
        cx = left + w / 2
        kind = node.get("kind", "")
        css = "shape external" if kind == "external" else "shape"
        parts.append(f'<g class="node" data-status="{s(node["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(node["label"])}">')
        if z["decision"]:
            parts.append(f'<path class="{css}" d="M {left+22:.1f} {top:.1f} L {left+w-22:.1f} {top:.1f} L {left+w:.1f} {top+h/2:.1f} L {left+w-22:.1f} {top+h:.1f} L {left+22:.1f} {top+h:.1f} L {left:.1f} {top+h/2:.1f} Z"/>')
        else:
            radius = min(h / 2, 26) if kind in {"start", "end"} else 12
            parts.append(f'<rect class="{css}" x="{left:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius:.1f}"/>')
        text_h = len(z["label"]) * NODE_LINE + (4 + len(z["detail"]) * 16 if z["detail"] else 0)
        text_top = top + 22 if z["fields"] else top + (h - text_h) / 2
        room = w - (56 if z["decision"] else 20)
        parts.append(svg_lines(z["label"], cx, text_top, "node-label", 14, NODE_LINE, fit=room))
        if z["detail"]:
            parts.append(svg_lines(z["detail"], cx, text_top + len(z["label"]) * NODE_LINE + 4, "node-sub", 11.5, 16, fit=room))
        if z["fields"]:
            line_y = top + 22 + len(z["label"]) * NODE_LINE + 4
            parts.append(f'<path d="M {left+10:.1f} {line_y:.1f} H {left+w-10:.1f}" class="field-rule"/>')
            for k, field in enumerate(z["fields"]):
                parts.append(f'<text class="field" x="{left+16:.1f}" y="{line_y + 8 + k*FIELD_LINE + 12.5*0.8:.1f}" direction="ltr" text-anchor="start" data-fit="{w - 28:.0f}">{s(field)}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def svg_sequence(diagram, details, rtl=False):
    people, messages = diagram["participants"], diagram["messages"]
    ids = [p["id"] for p in people]
    order = {pid: i for i, pid in enumerate(ids)}
    heads = {p["id"]: wrap(p["label"], 180, 14, bold=True) for p in people}
    head_w = {pid: max(140, min(230, max(text_width(line, 14, True) for line in lines) + 36)) for pid, lines in heads.items()}
    head_h = max(len(lines) for lines in heads.values()) * NODE_LINE + 26

    # The gap between two neighbour lifelines fits both heads and the labels of the messages between them.
    gap = [max(190, head_w[a] / 2 + head_w[b] / 2 + 36) for a, b in zip(ids, ids[1:])]
    for m in messages:
        a, b = order[m["from"]], order[m["to"]]
        if a == b:
            continue
        lo, hi = min(a, b), max(a, b)
        need = max(text_width(line, LABEL_SIZE) for line in wrap(m["label"], 300, LABEL_SIZE)) + 44
        have = sum(gap[lo:hi])
        if need > have:
            for k in range(lo, hi):
                gap[k] += (need - have) / (hi - lo)
    loops = any(m["from"] == m["to"] for m in messages)
    xs, left = {}, MARGIN + head_w[ids[0]] / 2
    for i, pid in enumerate(ids):
        xs[pid] = left
        if i < len(gap):
            left += gap[i]
    right_pad = 260 if loops else 0
    total_w = max(600, left + head_w[ids[-1]] / 2 + MARGIN + right_pad)

    def X(v):
        return total_w - v if rtl else v

    rows, cur = [], 30 + head_h + 44
    for m in messages:
        a, b = xs[m["from"]], xs[m["to"]]
        room = 220 if a == b else abs(b - a) - 40
        lines = wrap(m["label"], room, LABEL_SIZE)
        lw = max(text_width(line, LABEL_SIZE) for line in lines) + 14
        lh = len(lines) * LABEL_LINE + 6
        if a == b:
            rows.append((a, b, cur, lines, lw, lh))
            cur += max(56, lh + 20) + 24
        else:
            y = cur + lh + 8
            rows.append((a, b, y, lines, lw, lh))
            cur = y + 30
    total_h = max(300, cur + 20)

    marker = f'arr-{s(diagram["id"])}'
    parts = [f'<svg role="group" aria-label="{s(diagram["title"])}" viewBox="0 0 {total_w:.0f} {total_h:.0f}" width="{total_w:.0f}" height="{total_h:.0f}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="arrowhead" d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>']
    for i, p in enumerate(people):
        x, w = X(xs[p["id"]]), head_w[p["id"]]
        key = detail_key(diagram, "participant", i)
        details[key] = {"label": p["label"], "detail": p.get("detail", ""), "status": p["status"], "evidence": p.get("evidence", [])}
        lines = heads[p["id"]]
        top = 30 + (head_h - len(lines) * NODE_LINE) / 2
        parts.append(f'<line class="seq-life" x1="{x:.1f}" x2="{x:.1f}" y1="{30 + head_h:.1f}" y2="{total_h - 20:.1f}"/><g class="node" data-status="{s(p["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(p["label"])}"><rect class="shape" x="{x - w/2:.1f}" y="30" width="{w:.1f}" height="{head_h:.1f}" rx="12"/>{svg_lines(lines, x, top, "node-label", 14, NODE_LINE, fit=w - 16)}</g>')
    for i, (m, (a, b, y, lines, lw, lh)) in enumerate(zip(messages, rows)):
        key = detail_key(diagram, "message", i)
        details[key] = {"label": m["label"], "detail": m.get("detail", ""), "status": m["status"], "evidence": m.get("evidence", [])}
        cls = "edge " + s(m.get("style", "call"))
        if a == b:
            h = max(56, lh + 20)
            path = f"M {X(a):.1f} {y:.1f} L {X(a + 56):.1f} {y:.1f} Q {X(a + 70):.1f} {y:.1f} {X(a + 70):.1f} {y + 14:.1f} L {X(a + 70):.1f} {y + h - 14:.1f} Q {X(a + 70):.1f} {y + h:.1f} {X(a + 56):.1f} {y + h:.1f} L {X(a + 4):.1f} {y + h:.1f}"
            box_left, box_top = a + 82, y + (h - lh) / 2
        else:
            path = f"M {X(a):.1f} {y:.1f} L {X(b):.1f} {y:.1f}"
            box_left, box_top = (a + b) / 2 - lw / 2, y - lh - 6
        left = min(X(box_left), X(box_left + lw))
        parts.append(f'<g class="node edge-group" data-status="{s(m["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(m["label"])}"><path class="edge-hit" d="{path}"/><path class="{cls}" d="{path}" marker-end="url(#{marker})"/><circle cx="{X(a):.1f}" cy="{y:.1f}" r="4.5" class="seq-dot"/><rect class="edge-label-bg" x="{left:.1f}" y="{box_top:.1f}" width="{lw:.1f}" height="{lh:.1f}" rx="5"/>{svg_lines(lines, left + lw / 2, box_top + 3, "edge-label", LABEL_SIZE, LABEL_LINE, fit=lw - 8)}</g>')
    parts.append("</svg>")
    return "".join(parts)


# The page. Each function returns one part of it; render_html puts them in order inside the template.

# How to read each diagram type. The text is fixed here, not written by the agent, so every report teaches a
# type in the same words, and a reader who has never seen the type learns its name, its use and how to read it.

GUIDE = {
    "ar": {
        "flowchart": {"name": "مخطط التدفق", "en": "Flowchart",
                      "what": "يعرض خطوات عملية واحدة بالترتيب، والأسئلة التي تقسمها إلى فروع.",
                      "when": "يُستخدم حين يكون السؤال: كيف يسير الطلب، وأين يتوقف أو يتفرع؟",
                      "read": "ابدأ من الشكل المستدير في الأعلى، واتبع الأسهم إلى الأسفل. عند كل سؤال اتبع السهم الذي يحمل إجابتك.",
                      "arrow": "الخطوة التالية.", "label": "الشرط أو الإجابة التي تأخذ هذا الطريق."},
        "sequence": {"name": "مخطط التسلسل", "en": "Sequence diagram",
                     "what": "يعرض من يخاطب من وبأي ترتيب: كل عمود مشارك، وكل سهم رسالة بين مشاركين.",
                     "when": "يُستخدم حين يكون السؤال: بأي ترتيب تتواصل الأجزاء، ومن ينتظر رد من؟",
                     "read": "الزمن يسير إلى الأسفل، فاقرأ الأسهم من الأعلى إلى الأسفل. يبدأ السهم من النقطة وينتهي عند المشارك الذي يستلم الرسالة."},
        "c4": {"name": "مخطط البنية", "en": "C4 model",
               "what": "يعرض أجزاء النظام، ومسؤولية كل جزء، والحدود التي تعبرها الطلبات والبيانات.",
               "when": "يُستخدم حين يكون السؤال: أي جزء مسؤول عن هذا، وأي جزء يعتمد على أي جزء؟",
               "read": "كل صندوق جزء من النظام، والسهم يعني أن الجزء يستخدم الجزء الذي يشير إليه.",
               "arrow": "الجزء الذي يُستخدم أو يُستدعى.", "label": "ما يُستخدم الجزء من أجله.",
               "levels": {"context": "هذه الرسمة على مستوى السياق: النظام كله، ومن حوله من أشخاص وأنظمة.",
                          "container": "هذه الرسمة على مستوى الحاويات: التطبيقات والخدمات وقواعد البيانات داخل النظام.",
                          "component": "هذه الرسمة على مستوى المكونات: الأجزاء داخل تطبيق واحد، مثل الكلاسات والخدمات."}},
        "er": {"name": "مخطط الكيانات والعلاقات", "en": "Entity-relationship diagram",
               "what": "يعرض جداول قاعدة البيانات وأعمدتها، والعلاقات التي تربط الجداول.",
               "when": "يُستخدم حين يكون السؤال: أين تُحفظ البيانات، وبأي جدول يرتبط كل جدول؟",
               "read": "كل صندوق جدول: اسمه في الأعلى وأعمدته تحت الخط. السهم يربط جدولين.",
               "arrow": "علاقة بين جدولين.", "label": "نوع العلاقة، مثل واحد إلى كثير."},
        "state": {"name": "مخطط الحالات", "en": "State diagram",
                  "what": "يعرض الحالات التي يمر بها شيء واحد، مثل طلب أو مهمة، وما ينقله من حالة إلى أخرى.",
                  "when": "يُستخدم حين يكون السؤال: بأي حالات يمر هذا الشيء، وأي انتقال مسموح؟",
                  "read": "كل صندوق حالة، وكل سهم انتقال من حالة إلى أخرى. الحالة التي لا يخرج منها سهم نهاية.",
                  "arrow": "انتقال إلى حالة أخرى.", "label": "الحدث أو الشرط الذي يسبب الانتقال."},
        "marks": {"start": "بداية الطريق أو نهايته.", "process": "خطوة تُنفَّذ.", "decision": "سؤال، وكل سهم يخرج منه إجابة مختلفة.",
                  "external": "شيء خارج النظام المشروح.", "box": "جزء من النظام.", "person": "شخص يستخدم النظام.", "state": "حالة.",
                  "table": "جدول، وأعمدته تحت الخط.", "participant": "مشارك، مثل كلاس أو خدمة أو شخص.",
                  "lifeline": "خط حياة المشارك، والزمن يسير عليه إلى الأسفل.", "call": "طلب أو استدعاء.", "return": "رد على طلب سابق.",
                  "async": "رسالة لا ينتظر مرسلها ردًا.", "self": "عمل يقوم به المشارك داخله.",
                  "PK": "مفتاح أساسي يميز كل صف.", "FK": "مفتاح أجنبي يشير إلى صف في جدول آخر.", "UK": "قيمة لا تتكرر في الجدول.", "NULL": "العمود قد يبقى فارغًا."},
        "guide": "طريقة قراءة الرسمة", "read_line": "طريقة القراءة", "marks_line": "الأشكال في هذه الرسمة",
        "explain_head": "الرسوم في التقرير، ولماذا اخترنا كل واحدة:", "also": "ويُسمى {} بالإنجليزية", "explain_title": "الرسمة في التقرير",
        "explain_what": "ماذا يعرض هذا النوع", "explain_why": "لماذا اخترناه هنا", "explain_foot": "طريقة قراءة كل رسمة مشروحة فوقها في التقرير، مع معنى كل شكل فيها.",
    },
    "en": {
        "flowchart": {"name": "Flowchart", "en": "",
                      "what": "Shows the steps of one process in order, and the questions that split it into branches.",
                      "when": "Use it when the question is: how does a request move, and where does it stop or branch?",
                      "read": "Start at the rounded shape at the top and follow the arrows down. At each question, follow the arrow that carries your answer.",
                      "arrow": "The next step.", "label": "The condition or answer that takes this path."},
        "sequence": {"name": "Sequence diagram", "en": "",
                     "what": "Shows who talks to whom and in what order: each column is a participant, and each arrow is a message between two of them.",
                     "when": "Use it when the question is: in what order do the parts talk, and who waits for whose answer?",
                     "read": "Time runs down, so read the arrows from top to bottom. An arrow starts at the dot and ends at the participant that receives the message."},
        "c4": {"name": "C4 model diagram", "en": "",
               "what": "Shows the parts of a system, what each part owns, and the boundaries that requests and data cross.",
               "when": "Use it when the question is: which part owns this, and which part depends on which?",
               "read": "Each box is a part of the system. An arrow means the part uses the part it points to.",
               "arrow": "The part that is used or called.", "label": "What the part is used for.",
               "levels": {"context": "This diagram is at the context level: the whole system, and the people and systems around it.",
                          "container": "This diagram is at the container level: the apps, services and databases inside the system.",
                          "component": "This diagram is at the component level: the parts inside one app, such as classes and services."}},
        "er": {"name": "Entity-relationship (ER) diagram", "en": "",
               "what": "Shows the database tables, their columns, and the relationships that link the tables.",
               "when": "Use it when the question is: where is the data stored, and which table links to which?",
               "read": "Each box is a table: its name on top, its columns under the line. An arrow links two tables.",
               "arrow": "A relationship between two tables.", "label": "The kind of relationship, such as one to many."},
        "state": {"name": "State diagram", "en": "",
                  "what": "Shows the states that one thing, such as an order or a job, goes through, and what moves it from one state to another.",
                  "when": "Use it when the question is: which states does this go through, and which moves are allowed?",
                  "read": "Each box is a state, and each arrow is a move from one state to another. A state with no arrow out is an end.",
                  "arrow": "A move to another state.", "label": "The event or condition that causes the move."},
        "marks": {"start": "The start or the end of the path.", "process": "A step that runs.", "decision": "A question; each arrow out of it is a different answer.",
                  "external": "Something outside the system being explained.", "box": "A part of the system.", "person": "A person who uses the system.", "state": "A state.",
                  "table": "A table, with its columns under the line.", "participant": "A participant, such as a class, a service or a person.",
                  "lifeline": "The participant's lifeline; time runs down it.", "call": "A request or a call.", "return": "An answer to an earlier request.",
                  "async": "A message whose sender does not wait for an answer.", "self": "Work the participant does inside itself.",
                  "PK": "Primary key: identifies each row.", "FK": "Foreign key: points to a row in another table.", "UK": "A value that never repeats in the table.", "NULL": "The column may be empty."},
        "guide": "How to read this diagram", "read_line": "How to read it", "marks_line": "Shapes in this diagram",
        "explain_head": "The diagrams in the report, and why each one was chosen:", "also": "{}", "explain_title": "In the report",
        "explain_what": "What this type shows", "explain_why": "Why it was chosen here", "explain_foot": "Each diagram in the report has a short guide above it on how to read it, with the meaning of each shape.",
    },
}
MARK_SHAPES = {"start": "pill", "person": "pill", "process": "rect", "box": "rect", "state": "rect", "participant": "rect", "decision": "hex",
               "external": "dashed", "table": "table", "lifeline": "life", "arrow": "arrow", "call": "call", "return": "return", "async": "async",
               "self": "self", "label": "label"}


def guide_marks(diagram):
    """The marks this diagram really draws, in a fixed order, so its key explains only what is on the page."""
    kind = diagram["type"]
    if kind == "sequence":
        styles = {m.get("style", "call") for m in diagram["messages"]}
        marks = ["participant", "lifeline"] + [st for st in ("call", "return", "async") if st in styles]
        return marks + (["self"] if any(m["from"] == m["to"] for m in diagram["messages"]) else [])
    nodes, edges = diagram["nodes"], diagram["edges"]
    kinds = [n.get("kind", "") for n in nodes]
    if kind == "flowchart":
        marks = ["start"] if {"start", "end"} & set(kinds) else []
        marks += ["process"] if any(k not in {"start", "end", "decision", "external"} for k in kinds) else []
        marks += [k for k in ("decision", "external") if k in kinds]
    elif kind == "c4":
        marks = ["person"] if "person" in kinds else []
        marks += ["box"] if any(k not in {"person", "external"} for k in kinds) else []
        marks += ["external"] if "external" in kinds else []
    elif kind == "er":
        fields = [f for n in nodes for f in n.get("fields", [])]
        marks = ["table"] + [k for k in ("PK", "FK", "UK") if any(f.get("key") == k for f in fields)]
        marks += ["NULL"] if any(f.get("nullable") is True for f in fields) else []
    else:
        marks = ["state"]
    return marks + (["arrow"] if edges else []) + (["label"] if any(e.get("label") for e in edges) else [])


def mark_icon(shape):
    """A small picture of one mark, drawn with the diagram's own classes, so it follows the theme. Arrows turn in a right-to-left page."""
    head = '<path class="arrowhead" d="M34 9L42 14L34 19Z"/>'
    dot = '<circle class="seq-dot" cx="5" cy="14" r="3.5"/>'
    pics = {
        "pill": '<rect class="shape" x="2" y="5" width="40" height="18" rx="9"/>',
        "rect": '<rect class="shape" x="2" y="5" width="40" height="18" rx="4"/>',
        "hex": '<path class="shape" d="M9 5H35L42 14L35 23H9L2 14Z"/>',
        "dashed": '<rect class="shape external" x="2" y="5" width="40" height="18" rx="4"/>',
        "table": '<rect class="shape" x="2" y="2" width="40" height="24" rx="4"/><path class="field-rule" d="M7 11H37"/>',
        "life": '<path class="seq-life" d="M22 1V27"/>',
        "arrow": f'<path class="edge" d="M3 14H35"/>{head}',
        "call": f'<path class="edge" d="M5 14H35"/>{head}{dot}',
        "return": f'<path class="edge return" d="M5 14H35"/>{head}{dot}',
        "async": f'<path class="edge async" d="M5 14H35"/>{head}{dot}',
        "self": '<circle class="seq-dot" cx="5" cy="5" r="3.5"/><path class="edge" d="M4 5H28Q38 5 38 14Q38 23 28 23H12"/><path class="arrowhead" d="M13 18L5 23L13 28Z"/>',
        "label": '<rect class="edge-label-bg" x="3" y="6" width="38" height="16" rx="4"/><path class="label-line" d="M10 14H34"/>',
    }
    turn = " turn" if shape in {"arrow", "call", "return", "async", "self"} else ""
    return f'<svg class="mark{turn}" viewBox="0 0 44 28" aria-hidden="true"><g class="node">{pics[shape]}</g></svg>'


def diagram_guide(diagram, lang):
    """What the diagram type is called, what it is for, how to read it, and a key of the shapes this diagram uses."""
    g = GUIDE[lang]
    info = g[diagram["type"]]
    level = f' {info["levels"][diagram["level"]]}' if diagram["type"] == "c4" else ""
    english = f' <span class="en" lang="en" dir="ltr">{s(info["en"])}</span>' if info["en"] else ""
    keys = ""
    for mark in guide_marks(diagram):
        meaning = info.get(mark) or g["marks"][mark]
        icon = f'<code class="key-mark" dir="ltr">{s(mark)}</code>' if mark in {"PK", "FK", "UK", "NULL"} else mark_icon(MARK_SHAPES[mark])
        keys += f"<li>{icon}<span>{s(meaning)}</span></li>"
    return (f'<details class="guide" open><summary><span class="guide-label">{s(g["guide"])}</span><span class="guide-type">{s(info["name"])}{english}</span></summary>'
            f'<div class="guide-body"><p>{s(info["what"])} {s(info["when"])}{s(level)}</p><p><strong>{s(g["read_line"])}:</strong> {s(info["read"])}</p>'
            f'<ul class="marks" aria-label="{s(g["marks_line"])}">{keys}</ul></div></details>')


def explain_text(report):
    """Ready text for the agent's chat reply: each diagram's type, what that type shows, and why it was chosen for this task."""
    lang = "ar" if report["language"].lower().startswith("ar") else "en"
    g = GUIDE[lang]
    out = [g["explain_head"], ""]
    for n, d in enumerate(report["diagrams"], 1):
        info = g[d["type"]]
        named = " " + g["also"].format(info["en"]) if info["en"] else ""
        out += [f'{n}. **{info["name"]}**{named}', f'   - {g["explain_title"]}: {d["title"]}', f'   - {g["explain_what"]}: {info["what"]}', f'   - {g["explain_why"]}: {d["reason"]}']
    return "\n".join(out + ["", g["explain_foot"]])


# One line under each section title, and what each confidence level means, so the page never assumes the reader knows the method.
SECTION_HELP = {
    "ar": {"overview": "ما فحصناه، وما قررناه، وما بقي بلا إجابة. اقرأه أولًا لتعرف حدود التقرير.",
           "diagrams": "كل رسمة تجيب عن سؤال واحد، وفوقها شرح لطريقة قراءتها. لون إطار العنصر يبين حالته كما في المفتاح، واضغط أي عنصر لترى تفاصيله وأدلته.",
           "audit": "كل صف خطوة من الخطة: ما كان مخططًا، وما وجدناه منفذًا، وهل يتطابقان.",
           "evidence": "كل ما في التقرير يستند إلى دليل هنا. رقم الدليل يظهر بجانب كل عنصر، وعمود «مستخدم في» يعيدك إلى العنصر في رسمته.",
           "levels": "معنى درجات الثقة",
           "verified": "قرأناه في الكود أو رأيناه يعمل.", "inferred": "استنتجناه من الكود، ولم نره يعمل.",
           "planned": "مكتوب في الخطة، ولم يُنفذ بعد.", "unknown": "لم نجد عليه دليلًا كافيًا."},
    "en": {"overview": "What was inspected, what was decided, and what is still open. Read it first to know the limits of the report.",
           "diagrams": "Each diagram answers one question, and a short guide above it explains how to read it. The colour of an element's border shows its status, as in the key. Select any element to see its details and evidence.",
           "audit": "Each row is one step of the plan: what was planned, what was found built, and whether they match.",
           "evidence": "Everything in the report rests on evidence listed here. The evidence number appears next to each element, and the Used in column takes you back to the element in its diagram.",
           "levels": "What the confidence levels mean",
           "verified": "Read in the code or seen working.", "inferred": "Concluded from the code, but not seen working.",
           "planned": "Written in the plan, not built yet.", "unknown": "Not enough evidence was found."},
}


ICONS = {
    "in": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    "out": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/></svg>',
    "reset": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>',
    "full": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
    "mark": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="6" rx="1.5"/><rect x="14" y="15" width="7" height="6" rx="1.5"/><path d="M6.5 9v4.5a2 2 0 0 0 2 2H14"/></svg>',
}
STATUS_ORDER = ("implemented", "planned", "changed", "missing", "unknown", "context")


def evidence_links(refs):
    return " ".join(f'<a class="ref" href="#ev-{s(ref)}">{s(ref)}</a>' for ref in refs) or "—"


def elements(diagram):
    """Every element of a diagram with its detail key, in drawing order: nodes or participants, then edges or messages."""
    kind_a, kind_b = ("participant", "message") if diagram["type"] == "sequence" else ("node", "edge")
    first = diagram.get("participants" if kind_a == "participant" else "nodes", [])
    second = diagram.get("messages" if kind_b == "message" else "edges", [])
    return [(detail_key(diagram, kind_a, i), kind_a, item) for i, item in enumerate(first)] + [(detail_key(diagram, kind_b, i), kind_b, item) for i, item in enumerate(second)]


def element_name(diagram, kind, item, rtl=False):
    """An element's name as safe HTML. Each name sits in <bdi>, so an arrow between two English names still points the reading way."""
    if kind in {"node", "participant"}:
        return f"<bdi>{s(item['label'])}</bdi>"
    names = {n["id"]: n["label"] for n in diagram.get("nodes", diagram.get("participants", []))}
    label = f": <bdi>{s(item['label'])}</bdi>" if item.get("label") else ""
    return f"<bdi>{s(names[item['from']])}</bdi> {'←' if rtl else '→'} <bdi>{s(names[item['to']])}</bdi>{label}"


def page_topbar(report, u):
    theme = "".join(f'<button type="button" data-theme-choice="{c}" aria-pressed="false">{s(u[c])}</button>' for c in ("auto", "light", "dark"))
    return (f'<header class="topbar"><div class="topbar-inner"><a class="brand" href="#top"><span class="brand-mark">{ICONS["mark"]}</span>'
            f'<span>{s(u["report"])}</span><span class="brand-title">{s(report["title"])}</span></a>'
            f'<div class="theme" role="group" aria-label="{s(u["theme"])}">{theme}</div></div></header>')


def page_hero(report, u, lang):
    facts = "".join(f'<div><dt>{s(u[k])}</dt><dd>{s(report[k])}</dd></div>' for k in ("repository", "baseline"))
    counts = [(len(report["diagrams"]), u["n_diagrams"]), (len(report["evidence"]), u["n_evidence"]), (len(report["unknowns"]), u["n_unknowns"])]
    if report["audit"]:
        counts.append((sum(1 for row in report["audit"] if row["verdict"] != "matched"), u["n_gaps"]))
    stats = "".join(f'<li><b>{n}</b><span>{s(name)}</span></li>' for n, name in counts)
    return (f'<header class="hero" id="top"><p class="kicker">{s(term(report["phase"], lang))}</p><h1>{s(report["title"])}</h1>'
            f'<p class="lede">{s(report["summary"])}</p><ul class="stats">{stats}</ul><dl class="facts">{facts}</dl></header>')


def page_toc(report, u):
    items = [f'<li><a href="#overview">{s(u["overview"])}</a></li>']
    items += [f'<li><a href="#d-{s(d["id"])}">{s(d["title"])}</a></li>' for d in report["diagrams"]]
    if report["audit"]:
        items.append(f'<li><a href="#audit">{s(u["audit"])}</a></li>')
    items.append(f'<li><a href="#evidence">{s(u["evidence"])}</a></li>')
    return f'<nav class="toc" aria-label="{s(u["contents"])}"><ol>{"".join(items)}</ol></nav>'


def bullet_list(values, empty):
    return "<ul>" + "".join(f"<li>{s(v)}</li>" for v in values) + "</ul>" if values else f'<p class="empty">{s(empty)}</p>'


def section_intro(part, lang):
    return f'<p class="section-intro">{s(SECTION_HELP[lang][part])}</p>'


def page_overview(report, u, lang):
    return (f'<section id="overview" aria-labelledby="overview-title"><h2 id="overview-title" class="section-title">{s(u["overview"])}</h2>{section_intro("overview", lang)}'
            f'<div class="panel"><h3>{s(u["scope"])}</h3><p>{s(report["scope"])}</p></div>'
            f'<div class="two"><div class="panel"><h3>{s(u["decisions"])}</h3>{bullet_list(report["decisions"], u["empty"])}</div>'
            f'<div class="panel"><h3>{s(u["unknowns"])}</h3>{bullet_list(report["unknowns"], u["empty"])}</div></div></section>')


def diagram_text(diagram, u, lang, rtl):
    """The diagram as a list, for screen readers, for search, and for anyone who reads faster than they trace lines."""
    rows = []
    for key, kind, item in elements(diagram):
        detail = f'<span class="t-detail">{s(item["detail"])}</span>' if item.get("detail") else ""
        refs = f'<span class="t-refs">{evidence_links(item.get("evidence", []))}</span>' if item.get("evidence") else ""
        rows.append(f'<li class="t-{kind}"><button type="button" class="t-name" data-open="{s(key)}">{element_name(diagram, kind, item, rtl)}</button>{badge(item["status"], lang)}{detail}{refs}</li>')
    return f'<details class="as-text"><summary>{s(u["as_text"])}</summary><ol>{"".join(rows)}</ol></details>'


def diagram_figure(diagram, details, u, lang, rtl):
    svg = svg_sequence(diagram, details, rtl=rtl) if diagram["type"] == "sequence" else svg_graph(diagram, details, rtl=rtl)
    chip = term(diagram["type"], lang) + (f' · {term(diagram["level"], lang)}' if diagram["type"] == "c4" else "")
    tools = "".join(f'<button type="button" data-action="{a}" aria-label="{s(u[k])}" title="{s(u[k])}">{ICONS[a]}</button>' for a, k in (("out", "out"), ("in", "zoom"), ("reset", "reset"), ("full", "full")))
    title_id = f'd-{s(diagram["id"])}-title'
    return (f'<figure class="diagram" id="d-{s(diagram["id"])}" aria-labelledby="{title_id}">'
            f'<figcaption class="diagram-head"><div class="titles"><span class="chip">{s(chip)}</span><h3 id="{title_id}">{s(diagram["title"])}</h3>'
            f'<p class="question"><strong>{s(u["question"])}:</strong> {s(diagram["question"])}</p><p class="reason">{s(u["why"])}: {s(diagram["reason"])}</p></div>'
            f'<div class="tools" role="toolbar" aria-label="{s(diagram["title"])}">{tools}</div></figcaption>'
            f'{diagram_guide(diagram, lang)}<div class="viewport">{svg}</div><p class="hint">{s(u["help"])}</p>{diagram_text(diagram, u, lang, rtl)}</figure>')


def page_diagrams(report, details, u, lang, rtl):
    used = {item["status"] for d in report["diagrams"] for _, _, item in elements(d) if item.get("status")}
    legend = "".join(f'<li><i class="swatch {s(st)}"></i>{s(term(st, lang))}</li>' for st in STATUS_ORDER[:-1] if st in used)
    head = f'<div class="section-head"><h2 id="diagrams-title" class="section-title">{s(u["diagrams"])}</h2>' + (f'<ul class="legend" aria-label="{s(u["statuses"])}">{legend}</ul>' if legend else "") + "</div>"
    body = "".join(diagram_figure(d, details, u, lang, rtl) for d in report["diagrams"]) or f'<p class="empty">{s(u["empty"])}</p>'
    return f'<section id="diagrams" class="wide" aria-labelledby="diagrams-title">{head}{section_intro("diagrams", lang)}{body}</section>'


def page_audit(report, u, lang):
    if not report["audit"]:
        return ""
    counts = {}
    for row in report["audit"]:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    summary = "".join(f'<li>{badge(v, lang)}<b>{n}</b></li>' for v, n in counts.items())
    heads = (u["step"], u["planned"], u["actual"], u["result"], u["note"], u["evidence"])
    rows = ""
    for row in report["audit"]:
        cells = (s(row["step"]), s(row["planned"]), s(row["actual"]), badge(row["verdict"], lang), s(row.get("note", "")), evidence_links(row.get("evidence", [])))
        rows += "<tr>" + "".join(f'<td data-label="{s(h)}">{c}</td>' for h, c in zip(heads, cells)) + "</tr>"
    return (f'<section id="audit" aria-labelledby="audit-title"><div class="section-head"><h2 id="audit-title" class="section-title">{s(u["audit"])}</h2><ul class="verdicts">{summary}</ul></div>{section_intro("audit", lang)}'
            f'<div class="tablewrap"><table class="stack"><thead><tr>{"".join(f"<th scope=col>{s(h)}</th>" for h in heads)}</tr></thead><tbody>{rows}</tbody></table></div></section>')


def page_evidence(report, u, lang):
    cited = {}
    for d in report["diagrams"]:
        for key, kind, item in elements(d):
            for ref in item.get("evidence", []):
                cited.setdefault(ref, []).append((key, d, kind, item))
    rows = ""
    for e in report["evidence"]:
        location = " · ".join(filter(None, [e.get("path", ""), e.get("symbol", ""), e.get("lines", "")])) or term(e["kind"], lang)
        uses = "".join(f'<li><button type="button" data-open="{s(key)}">{element_name(d, kind, item, lang == "ar")}</button></li>' for key, d, kind, item in cited.get(e["id"], [])[:6])
        more = len(cited.get(e["id"], [])) - 6
        uses += f'<li class="more">+{more}</li>' if more > 0 else ""
        used_in = f'<ul class="used-in">{uses}</ul>' if uses else '<span class="empty">—</span>'
        rows += (f'<tr id="ev-{s(e["id"])}"><th scope="row" class="id">{s(e["id"])}</th><td data-label="{s(u["source"])}"><code>{s(location)}</code><span class="kind">{s(term(e["kind"], lang))}</span></td>'
                 f'<td data-label="{s(u["claim"])}">{s(e["claim"])}</td><td data-label="{s(u["confidence"])}">{badge(e["confidence"], lang)}</td><td data-label="{s(u["used_in"])}">{used_in}</td></tr>')
    heads = ("ID", u["source"], u["claim"], u["confidence"], u["used_in"])
    used = {e["confidence"] for e in report["evidence"]}
    levels = "".join(f'<div><dt>{badge(c, lang)}</dt><dd>{s(SECTION_HELP[lang][c])}</dd></div>' for c in ("verified", "inferred", "planned", "unknown") if c in used)
    levels = f'<dl class="levels" aria-label="{s(SECTION_HELP[lang]["levels"])}">{levels}</dl>' if levels else ""
    return (f'<section id="evidence" aria-labelledby="evidence-title"><h2 id="evidence-title" class="section-title">{s(u["evidence"])}</h2>{section_intro("evidence", lang)}{levels}'
            f'<div class="tablewrap"><table class="stack"><thead><tr>{"".join(f"<th scope=col>{s(h)}</th>" for h in heads)}</tr></thead><tbody>{rows}</tbody></table></div></section>')


def render_html(report, template):
    rtl = report["language"].lower().startswith("ar")
    lang = "ar" if rtl else "en"
    u = UI[lang]
    details = {}
    content = page_hero(report, u, lang) + page_toc(report, u) + page_overview(report, u, lang) + page_diagrams(report, details, u, lang, rtl) + page_audit(report, u, lang) + page_evidence(report, u, lang)
    for item in details.values():
        item["state"] = item["status"]
        item["status"] = term(item["status"], lang)
    data = json.dumps({"evidence": report["evidence"], "details": details}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    replacements = {"__LANG__": s(report["language"]), "__DIR__": "rtl" if rtl else "ltr", "__TITLE__": s(report["title"]), "__SKIP__": s(u["skip"]), "__DETAIL_LABEL__": s(u["detail"]), "__CLOSE__": s(u["close"]), "__LINKED__": s(u["linked"]), "__TOPBAR__": page_topbar(report, u), "__CONTENT__": content, "__FOOTER__": s(u["footer"]), "__DATA__": data}
    return re.sub(r"__(?:LANG|DIR|TITLE|SKIP|DETAIL_LABEL|CLOSE|LINKED|TOPBAR|CONTENT|FOOTER|DATA)__", lambda match: replacements[match.group()], template)


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
            out.append(f'    {ids[e["from"]]} --> {ids[e["to"]]}' + (f': {mermaid_text(e["label"])}' if e.get("label") else ""))
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
                        note = ' "nullable"' if f.get("nullable") is True else ""
                        out.append(f"        {typ} {name}{key}{note}")
                out.append("    }")
            else:
                out.append(f'    {ids[n["id"]]}["{alias}"]')
        for e in diagram["edges"]:
            if e.get("cardinality"):
                out.append(f'    {ids[e["from"]]} {e["cardinality"]} {ids[e["to"]]} : "{mermaid_text(e.get("label", ""))}"')
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
        out.append(f'    {ids[e["from"]]} -->' + (f'|"{mermaid_text(e["label"])}"|' if e.get("label") else "") + f' {ids[e["to"]]}')
    return "\n".join(out)


def md_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_md(report):
    lang="ar" if report["language"].lower().startswith("ar") else "en"
    u=UI[lang]
    out=[f'# {report["title"]}',"",f'**{u["phase"]}:** {term(report["phase"], lang)}  ',f'**{u["repository"]}:** {report["repository"]}  ',f'**{u["baseline"]}:** {report["baseline"]}',"",report["summary"],"",f'**{u["scope"]}:** {report["scope"]}',""]
    for key in ("decisions","unknowns"):
        out += [f"## {u[key]}",""]
        out += [f"- {v}" for v in report[key]] or [f'- {u["empty"]}']
        out.append("")
    out += [f'## {u["diagrams"]}',""]
    for d in report["diagrams"]:
        info = GUIDE[lang][d["type"]]
        level = f' {info["levels"][d["level"]]}' if d["type"]=="c4" else ""
        out += [f'### {d["title"]}', "", f'**{info["name"]}**' + (" " + GUIDE[lang]["also"].format(info["en"]) if info["en"] else "") + f'. {info["what"]}{level}  ', f'**{GUIDE[lang]["read_line"]}:** {info["read"]}', "", f'**{u["question"]}:** {d["question"]}  ',f'**{u["why"]}:** {d["reason"]}',"","```mermaid",render_mermaid(d),"```","",f'| {u["element"]} | {u["status"]} | {u["evidence"]} |',"| --- | --- | --- |"]
        elems = [(x.get("label",x.get("id","")),x) for x in d.get("nodes",d.get("participants",[]))]
        elems += [(f"{x['from']} → {x['to']}" + (f": {x['label']}" if x.get("label") else ""),x) for x in d.get("edges",d.get("messages",[]))]
        out += [f'| {md_cell(name)} | {term(x["status"], lang)} | {", ".join(x.get("evidence",[])) or "—"} |' for name,x in elems]
        out.append("")
    if report["audit"]:
        out += [f'## {u["audit"]}',"",f'| {u["step"]} | {u["planned"]} | {u["actual"]} | {u["result"]} | {u["note"]} | {u["evidence"]} |',"| --- | --- | --- | --- | --- | --- |"]
        out += ["| " + " | ".join(md_cell(row.get(k,"")) for k in ("step","planned","actual")) + " | " + term(row["verdict"], lang) + " | " + md_cell(row.get("note","")) + " | " + ", ".join(row.get("evidence",[])) + " |" for row in report["audit"]]
        out.append("")
    out += [f'## {u["evidence"]}',"",f'| ID | {u["kind"]} | {u["source"]} | {u["claim"]} | {u["confidence"]} |',"| --- | --- | --- | --- | --- |"]
    for e in report["evidence"]:
        location=" · ".join(filter(None,[e.get("path",""),e.get("symbol",""),e.get("lines","")])) or "—"
        out.append("| " + " | ".join(md_cell(v) for v in (e["id"],term(e["kind"], lang),location,e["claim"],term(e["confidence"], lang))) + " |")
    out.append("")
    return "\n".join(out)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path,help="UTF-8 report JSON")
    parser.add_argument("-o","--output",type=Path,help="Output .html (default) or .md")
    parser.add_argument("--check",action="store_true",help="Validate without writing")
    parser.add_argument("--explain",action="store_true",help="Print chat text on each diagram's type and why it was chosen, without writing")
    args=parser.parse_args(argv)
    try:
        report=json.loads(args.input.read_text(encoding="utf-8"))
        validate(report)
        if args.check:
            print(f"Valid report: {args.input}")
            return 0
        if args.explain:
            print(explain_text(report))
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
