# Report JSON contract

The renderer accepts UTF-8 JSON. All displayed strings are escaped. The agent supplies the model after inspecting the request and code; the renderer does not discover architecture automatically.

## Top level

```json
{
  "title": "Checkout authorization / تفويض الطلب",
  "language": "ar",
  "phase": "plan|explain|audit|combined",
  "repository": "repository name/path or 'not examined' for a conversation-only plan",
  "baseline": "commit, diff range, working tree date, or agreed conversation plan",
  "scope": "What was inspected and excluded",
  "summary": "One paragraph",
  "decisions": ["Brief design choices"],
  "unknowns": ["Concrete unresolved facts"],
  "evidence": [],
  "diagrams": [],
  "audit": []
}
```

`language` is `ar` or `en` (other BCP 47 tags are accepted by the renderer). `phase` is `plan` for a plan with or without code, `explain` for an existing project without a change comparison, `audit` for a completed change, or `combined` for a plan and later implementation comparison. `audit` can be empty when there is no prior plan/specification to compare against; say so in `scope` or `unknowns`. All arrays can be empty, but a diagram or audit claim requires references.

## Evidence

```json
{"id":"E1","kind":"code|test|request|assumption|observation","path":"app/Services/Checkout.php","symbol":"Checkout::start","lines":"42-71","claim":"Calls the payment gateway before saving order status","confidence":"verified|inferred|planned|unknown"}
```

`path`, `symbol`, and `lines` are optional for request/assumption evidence, including an agreed conversation-only plan. `path` is repository-relative, unless the source is outside the repository and explicitly stated. `lines` is a human-readable range, not a parser guarantee. `verified` means directly supported by inspected code/test output for the exact claim; `inferred` means a static inference; `planned` means future design; `unknown` means unresolved. Test evidence must distinguish source inspection from actual execution in its `claim`.

## Diagrams

Common fields: `id`, `type`, `title`, `question`, `reason`. Types are exactly `flowchart`, `sequence`, `c4`, `er`, `state`. Every diagram node, edge, message, and participant may carry `detail`, `status`, and `evidence` (array of evidence IDs). Status is `planned`, `implemented`, `changed`, `missing`, `unknown`, or `context`. The renderer rejects missing evidence IDs and `implemented` elements without a code or observation reference.

### Flowchart, C4, ER, State

```json
{
  "id":"D1", "type":"flowchart", "title":"Request flow",
  "question":"Where can checkout fail?", "reason":"Shows validation branches",
  "nodes":[
    {"id":"n1","label":"POST /checkout","detail":"Entry point","status":"implemented","evidence":["E1"],"kind":"start"},
    {"id":"n2","label":"Validate stock?","status":"planned","evidence":["E2"],"kind":"decision"}
  ],
  "edges":[{"from":"n1","to":"n2","label":"request","status":"planned","evidence":["E2"]}]
}
```

For `c4`, set `level` to `context`, `container`, or `component`; `nodes[].kind` can be `person`, `system`, `container`, `component`, or `external`. For `er`, each node is a table/entity with optional `fields`: `[{"name":"order_id","type":"bigint","key":"PK|FK|UK","nullable":false}]`; edges should label verified cardinality, such as `1 → many`. Add `cardinality` only when its exact Mermaid crow's-foot notation is known, for example `||--o{` for exactly one to zero or many. If omitted, HTML shows the relationship label but Markdown omits that edge from its ER diagram and keeps it in the evidence table. For `state`, nodes represent states and edges represent events/guards. For `flowchart`, node `kind` may be `start`, `end`, `decision`, `process`, or `external`. The renderer lays nodes out automatically, top to bottom, and mirrors the layout in a right-to-left report; put branches in edge labels. An edge `label` is optional: leave it out on a plain next step rather than writing filler such as "then". Keep labels short. Each text line takes the direction of its first letter, so in an Arabic report start every node and edge label with an Arabic word, and put a code name after it.

### Sequence

```json
{
  "id":"D2", "type":"sequence", "title":"Payment handshake",
  "question":"Who invokes the gateway?", "reason":"Shows order and response boundary",
  "participants":[{"id":"api","label":"API","status":"implemented","evidence":["E1"]},{"id":"gateway","label":"Gateway","status":"context","evidence":["E3"]}],
  "messages":[{"from":"api","to":"gateway","label":"authorize()","style":"call|return|async","status":"implemented","evidence":["E1"]}]
}
```

The sequence array order is the message order. `return` renders dashed; `async` renders dotted.

## Audit rows

```json
{"step":"Validate stock before payment","planned":"Stock guard before gateway call","actual":"Guard is after gateway call","verdict":"changed","evidence":["E1","E4"],"note":"Potential authorization of unavailable items"}
```

`verdict` is `matched`, `changed`, `missing`, or `unverified`. Compare material planned steps individually. A `missing` row means no implementation was found within the stated inspection scope, not a global proof of absence. Use `unverified` if the code or runtime evidence is insufficient. For an audit, cite evidence for observed implementation; a planned-only request reference is insufficient to support `matched`.

## CLI

```bash
python3 scripts/render_report.py examples/order-checkout.json -o checkout.html
python3 scripts/render_report.py examples/order-checkout.json -o checkout.md
```

Only `.html` and `.md` outputs are supported. `--check` validates a JSON file without writing. The default output when `-o` is omitted is `<input-stem>.html`.
