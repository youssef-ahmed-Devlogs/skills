# Which kind, and where

A starting map, not the final word: the skill fetches every source below again on each run, and a source that now says something else wins. Each kind loads at a different time, so each fits a different need. Pick by how the agent must use it, not by how big it is.

| The need | The kind | Where | Why |
| --- | --- | --- | --- |
| Every session must know it, such as a build command or "never push to main" | A short line in `AGENTS.md` (or `CLAUDE.md`, which imports it) | The project root, or the user's shared rules for every project | Loaded in full at the start of every session. Keep it under 200 lines: every line costs on every request. [1] [2] |
| It holds only for some files, such as the rules of controllers | A rule with `paths` | `.claude/rules/<subject>.md` | Loads only when the agent works on matching files. [2] |
| A procedure, checklist or reference needed only sometimes | A skill | `skills/<kind>/<name>/SKILL.md` | Only its description loads at the start; the body loads when it is used. [3] [1] |
| A workflow with side effects, or one the user starts on purpose | A skill with `disable-model-invocation: true` | Same | The agent cannot start it by itself, and nothing loads until it is run. [3] |
| It must happen every time, the same way, with no judgement | A hook, a git hook, CI, or a test | `.claude/settings.json`, `.git/hooks`, `.github/workflows`, `tests/` | An instruction is a request, not a guarantee. A hook or a check is enforcement. [1] |
| A mechanical rule of code, such as a banned function or a folder | A check: a test such as Pest `arch()`, a linter rule, or a search for old code | `tests/`, the linter's config, `refactor-issues` and its checks file | A mechanical violation gets a deterministic check; prose rules are for judgement calls. [4] |
| How every reply sounds: language, length, format | An output style | `~/.claude/output-styles` | It sets the response for the whole session, and it can be switched off. [1] |
| A side task that reads a lot but returns a little | A subagent | `.claude/agents` | Its work stays out of the main context; only a summary comes back. [1] |
| Data or actions in another system | An MCP server, with a skill that says how to use it | `.mcp.json` | MCP gives the tools; the skill gives the know-how. [1] |
| The shape of an issue or a pull request | A GitHub template, which a rule points at | `.github/ISSUE_TEMPLATE`, `.github/pull_request_template.md` | One place for each shape, read by people, GitHub and skills alike. |
| A decision and its reason | An ADR | `docs/adr` | So the reason is never lost. [5] |

## Which repository

- **A shared repository**: it holds for every project, or every project of one stack, such as the user's own repository of skills or rules. Projects get it on their next update from there.
- **The project**: only this project needs it, such as its own domain rules.
- **The user's own setup** (`~/.claude`): a personal preference for every project, which the team does not share.

## Sources

1. Claude Code docs, [Extend Claude Code](https://code.claude.com/docs/en/features-overview): when to use CLAUDE.md, rules, skills, subagents, hooks and MCP.
2. Claude Code docs, [How Claude remembers your project](https://code.claude.com/docs/en/memory): CLAUDE.md, `AGENTS.md`, and rules with `paths`.
3. Claude Code docs, [Skills](https://code.claude.com/docs/en/skills), and the open [Agent Skills specification](https://agentskills.io/specification).
4. The `retro` skill of [mattpocock/skills](https://github.com/mattpocock/skills): a mechanical violation gets a check, a judgement call gets a written standard.
5. Michael Nygard, [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).
