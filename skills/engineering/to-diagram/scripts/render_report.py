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
    "ar": {"phase": "المرحلة", "repository": "المشروع", "baseline": "المرجع", "scope": "نطاق الفحص", "decisions": "القرارات", "unknowns": "ما لم يُحسم", "diagrams": "الرسوم", "audit": "مقارنة الخطة بالتنفيذ", "evidence": "الأدلة", "question": "سؤال المراجعة", "why": "سبب الاختيار", "zoom": "تكبير", "out": "تصغير", "reset": "إعادة الضبط", "element": "العنصر", "status": "الحالة", "step": "الخطوة", "planned": "المخطط", "actual": "المنفذ", "result": "النتيجة", "note": "ملاحظة", "source": "المصدر", "claim": "ما يثبته", "confidence": "الثقة", "kind": "النوع", "empty": "لا توجد عناصر", "help": "اسحب للتنقل، وكبّر بـ Ctrl مع عجلة الفأرة أو بالأزرار، واضغط على عنصر للتفاصيل.", "footer": "تقرير مبني على الأدلة المذكورة؛ حدود الفحص موضحة أعلاه."},
    "en": {"phase": "Phase", "repository": "Repository", "baseline": "Baseline", "scope": "Inspection scope", "decisions": "Decisions", "unknowns": "Unknowns", "diagrams": "Diagrams", "audit": "Plan vs implementation", "evidence": "Evidence", "question": "Review question", "why": "Why this diagram", "zoom": "Zoom in", "out": "Zoom out", "reset": "Reset", "element": "Element", "status": "Status", "step": "Step", "planned": "Planned", "actual": "Actual", "result": "Result", "note": "Note", "source": "Source", "claim": "Supported claim", "confidence": "Confidence", "kind": "Kind", "empty": "No items", "help": "Drag to pan, zoom with Ctrl and the scroll wheel or the buttons, and select an element for details.", "footer": "This report is bounded by the cited evidence and inspection scope."},
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


def badge(value):
    return f'<span class="badge {s(value)}">{s(value)}</span>'


def list_card(title, values, empty):
    body = "<ul>" + "".join(f"<li>{s(v)}</li>" for v in values) + "</ul>" if values else f'<p class="muted">{s(empty)}</p>'
    return f'<div class="card"><h3>{s(title)}</h3>{body}</div>'


def evidence_links(refs):
    return ", ".join(f'<a href="#ev-{s(ref)}">{s(ref)}</a>' for ref in refs) or "—"


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


def svg_lines(lines, cx, top, css, size, line_height, anchor="middle"):
    """Text lines, each with its own direction, so a line that starts with English keeps its order."""
    out = []
    for i, line in enumerate(lines):
        out.append(f'<text class="{css}" x="{cx:.1f}" y="{top + i*line_height + size*0.8:.1f}" text-anchor="{anchor}" direction="{text_dir(line)}">{s(line)}</text>')
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
    field_texts = [f"{f.get('key', '')} {f['name']} {f.get('type', '')}".strip() for f in fields]
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
    parts = [f'<svg role="img" aria-label="{s(diagram["title"])}" viewBox="0 0 {total_w:.0f} {total_h:.0f}" width="{total_w:.0f}" height="{total_h:.0f}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7990b1"/></marker></defs>']
    for i, e in enumerate(edges):
        key = detail_key(diagram, "edge", i)
        details[key] = {"label": e.get("label", ""), "detail": e.get("detail", ""), "status": e["status"], "evidence": e.get("evidence", [])}
        parts.append(f'<g class="node edge-group" data-status="{s(e["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(e.get("label") or e["from"] + " → " + e["to"])}"><path class="edge-hit" d="{paths[i]}"/><path class="edge" d="{paths[i]}" marker-end="url(#{marker})"/></g>')
    for i, (rect, lines) in labels.items():
        key = detail_key(diagram, "edge", i)
        left = min(X(rect[0]), X(rect[2]))
        cx = left + (rect[2] - rect[0]) / 2
        parts.append(f'<g class="node" data-status="{s(edges[i]["status"])}" data-key="{s(key)}"><rect class="edge-label-bg" x="{left:.1f}" y="{Y(rect[1]):.1f}" width="{rect[2]-rect[0]:.1f}" height="{rect[3]-rect[1]:.1f}" rx="5"/>{svg_lines(lines, cx, Y(rect[1]) + 3, "edge-label", LABEL_SIZE, LABEL_LINE)}</g>')
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
        parts.append(svg_lines(z["label"], cx, text_top, "node-label", 14, NODE_LINE))
        if z["detail"]:
            parts.append(svg_lines(z["detail"], cx, text_top + len(z["label"]) * NODE_LINE + 4, "node-sub", 11.5, 16))
        if z["fields"]:
            line_y = top + 22 + len(z["label"]) * NODE_LINE + 4
            parts.append(f'<path d="M {left+10:.1f} {line_y:.1f} H {left+w-10:.1f}" stroke="#52617c"/>')
            for k, field in enumerate(z["fields"]):
                parts.append(f'<text class="field" x="{left+16:.1f}" y="{line_y + 8 + k*FIELD_LINE + 12.5*0.8:.1f}" direction="ltr" text-anchor="start">{s(field)}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def svg_sequence(diagram, details):
    parts_data = diagram["participants"]
    messages = diagram["messages"]
    width = max(650, len(parts_data)*230+80)
    height = max(350, 175+len(messages)*95)
    xs = {p["id"]: 155+i*230 for i,p in enumerate(parts_data)}
    parts = [f'<svg role="img" aria-label="{s(diagram["title"])}" viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arr-{s(diagram["id"])}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7990b1"/></marker></defs>']
    for i,p in enumerate(parts_data):
        x=xs[p["id"]]; key=detail_key(diagram,"participant",i)
        details[key]={"label":p["label"],"detail":p.get("detail", ""),"status":p["status"],"evidence":p.get("evidence", [])}
        parts.append(f'<line class="seq-life" x1="{x}" x2="{x}" y1="90" y2="{height-30}"/><g class="node" data-status="{s(p["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(p["label"])}"><rect class="shape" x="{x-95}" y="30" width="190" height="60" rx="12"/>{svg_lines(wrap(p["label"],170,14,True)[:2],x,60-len(wrap(p["label"],170,14,True)[:2])*19/2,"node-label",14,NODE_LINE)}</g>')
    for i,m in enumerate(messages):
        x1,x2=xs[m["from"]],xs[m["to"]]; y=135+i*95
        cls="edge " + s(m.get("style","call"))
        if x1 == x2:
            path=f"M {x1} {y} C {x1+105} {y-24}, {x1+105} {y+42}, {x1} {y+42}"
        else:
            path=f"M {x1} {y} L {x2} {y}"
        key=detail_key(diagram,"message",i)
        details[key]={"label":m["label"],"detail":m.get("detail", ""),"status":m["status"],"evidence":m.get("evidence", [])}
        parts.append(f'<g class="node" data-status="{s(m["status"])}" data-key="{s(key)}" tabindex="0" role="button" aria-label="{s(m["label"])}"><path class="{cls}" d="{path}" marker-end="url(#arr-{s(diagram["id"])})"/><text class="edge-label" x="{(x1+x2)/2}" y="{y-12}" text-anchor="middle" direction="{text_dir(m["label"])}">{s(m["label"])}</text><circle cx="{x1}" cy="{y}" r="5" fill="#7dd3fc"/></g>')
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
        svg = svg_sequence(diagram,details) if diagram["type"] == "sequence" else svg_graph(diagram,details,rtl=ar)
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
                        out.append(f"        {typ} {name}{key}")
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
        elems += [(f"{x['from']} → {x['to']}" + (f": {x['label']}" if x.get("label") else ""),x) for x in d.get("edges",d.get("messages",[]))]
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
