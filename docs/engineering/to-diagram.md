# to-diagram

Turn an agreed plan, unfamiliar code project, or finished code change into diagrams. The skill picks the diagram types and links claims to the plan or the code it read.

**Start it:** `/to-diagram` with what you want to understand. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill to-diagram
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** Python 3.9 or later and a terminal tool to run its bundled renderer. It calls no other skill. The HTML report needs no network connection.

**Where to run it:** In any session for a plan from the chat. For existing or changed code, start inside that project's folder. The agent writes the report in the folder you name, or else in `~/.to-diagram/<project>/`, outside the project, so it adds no file to your repository. A plan from the chat alone goes in `~/.to-diagram/plans/`. The report's JSON stays beside it, so the agent can render it again.

**Call it:** in Claude Code or GitHub Copilot, type `/to-diagram` and your request. In Codex, type `$to-diagram` and your request.

**Agents:** Any agent that reads skills and can run Python, including Claude Code, Codex and GitHub Copilot.

## What it does

1. It decides whether you want to see a plan, understand existing code, or review a finished change.
2. It reads the agreed plan or the relevant code and diff. It states what it checked and what it could not verify.
3. It chooses one or more of Flowchart, Sequence, C4, ER and State. You do not have to choose.
4. It makes one standalone HTML report by default. The page follows your system's light or dark mode, with a switch at the top to pick one, and keeps the text in a narrow centered column. Each diagram has zoom (the buttons, or Ctrl and the scroll wheel), pan, a full-screen view, a status key, and details and evidence for every step. The diagrams read top to bottom, and right to left in an Arabic report, where every fixed word, such as a status, is in Arabic too. Ask for `.md` to get Markdown with Mermaid diagrams instead.
5. When there is a plan and finished code, it compares each important planned step with what the code does.

## When to use it

| Your situation | Use |
| --- | --- |
| You agreed on a plan and want to see its flow before coding | `to-diagram` |
| You opened an unfamiliar code project and want a map of how it works | `to-diagram` |
| An agent finished a code change and you want to understand what it did | `to-diagram` |
| You want to keep up with a project that changes every day | [`catch-me-up`](../productivity/catch-me-up.md) |
| You have not settled the plan and want the agent to ask you one question at a time | [`interview-me`](../productivity/interview-me.md) |

## Example

A shop team agrees that checkout should check stock before it asks the payment provider to authorize a charge.

```text
You:    /to-diagram Show our checkout plan before we write code.

Agent:  I made ~/.to-diagram/plans/checkout-plan.html. The flowchart
        shows the stock check, the out-of-stock branch and the payment
        call. It marks the retry policy as unknown. I used the agreed
        plan; I did not inspect code.

You:    /to-diagram The checkout change is done. Show what the code does
        and compare it with that plan.

Agent:  I made ~/.to-diagram/shop/checkout-audit.html. The sequence
        diagram shows that the payment call comes before the stock check.
        The audit marks that step as changed and links it to the service
        method I read.
```

## More use cases

- **A new codebase:** Ask for its entry flow and service boundaries. The report says which paths were inspected, so its map has a clear limit.
- **A database change:** Ask what a migration changed. An ER diagram shows keys and relationships that the migration actually defines.
- **A lifecycle:** Ask what states a job or order can enter. A State diagram shows transitions found in the code or agreed plan.

## What you get

One offline HTML report by default, and the agent tells you its full path. When the agent has a browser tool, it looks at every diagram before it hands the report over; when it has none, it says so. It has embedded diagrams, an evidence table and, when a plan exists, a comparison with finished code. If you ask for `.md`, you get Markdown with Mermaid diagrams and the same evidence text. The skill does not change code unless you also ask for implementation.

## Tips

- For a large project, name the workflow you need first, such as checkout or refunds. The report can then map that flow without pretending to cover the whole repository.
