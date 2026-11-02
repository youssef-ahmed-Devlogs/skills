# Diagram selection

Choose diagrams from the *question the user needs answered*, using the agreed plan, relevant code, or completed change. Start with one. Add another only when it reveals a different kind of relationship. There is no fixed diagram quota. A conversation-only plan is enough input; do not demand code evidence for planned elements.

| Type | Choose when the central question is… | Include | Avoid |
|---|---|---|---|
| `flowchart` | Which decisions and branches does a request take? | Entry, validation/guards, branches, failures, side effects, exit | A straight list of calls with no decisions; use sequence if ordering across actors is the issue |
| `sequence` | Who calls whom, in what order, and where do async boundaries or responses occur? | Actors, ordered messages, return/error paths, queue/event boundaries | Claiming a runtime call from import or naming alone |
| `c4` | Which service/module/container owns a responsibility and what crosses the boundary? | Explicit abstraction level, components/containers, directional dependencies and trust/data boundaries | Mixing classes, containers, and deployment nodes without labels |
| `er` | How does persistent data relate and what cardinality/constraints matter? | Actual tables/entities, keys, FKs, cardinalities, nullable/unique constraints when verified | Treating ORM relation names as proof of physical FKs; guessing cardinality |
| `state` | Which states exist, what triggers transitions, and what is forbidden? | States, events/guards, terminal or failure states, source of truth | Turning ordinary method call sequence into a state machine |

## Decision procedure

1. Write one explanation question for the task. If it is mainly branching, choose `flowchart`; cross-component temporal behavior, `sequence`; ownership/boundary, `c4`; persistence, `er`; lifecycle, `state`.
2. Check whether the first diagram hides a material second question. Example: checkout authorization can need a `sequence` for payment calls plus a `state` diagram for order status; a schema migration may need `er` plus a `flowchart` for the backfill. Add the second type only if the evidence supports it.
3. For an unfamiliar project, start with the smallest meaningful boundary (often `c4`) and a representative flow (`flowchart` or `sequence`) when the user needs behavior. State which directories and entry points were inspected; a map of a large project is necessarily bounded.
4. In a small plan or change, one diagram with a short evidence table may be enough. If none of the five clarifies it, state that in the report and use an evidence-linked textual trace.
5. Reassess after implementation if the user later requests an audit. The final report can change diagram types if the code reveals a different boundary, but explain the change.

## Backend inspection cues

- **Laravel:** Start from route to middleware/controller; trace container resolution, service/actions, events/jobs/listeners, policies, model writes, migrations, and transactions only where the code leads. Distinguish sync dispatch from queued execution.
- **NestJS:** Start from module/controller or message handler; trace guards/pipes/interceptors, injected providers, repository/ORM access, event/queue handlers, and exception mapping only where the code leads. Distinguish registered providers from invoked providers.
- **Both:** Search paths and symbols first; read the relevant implementation, call site, and tests. Use the diff to scope the post-implementation audit. A static trace cannot prove deployment wiring, external-service behavior, or every runtime branch; label those limits.
