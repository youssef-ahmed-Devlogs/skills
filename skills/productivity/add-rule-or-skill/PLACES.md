# Which kind, and where

A starting map, not the final word: the skill fetches every source below again on each run, and a source that now says something else wins. Each kind loads at a different time, so each fits a different need. Pick by how the agent must use it, not by how big it is.

## One home that every agent reads

A project may start with one agent and go on with another, such as Claude Code today and Codex tomorrow. So write each rule once, in a place every agent the project uses reads:

- **Lines for every session** go in `AGENTS.md`. Codex and GitHub Copilot read it. Claude Code reads it when the project has no `CLAUDE.md`; when it has one, that `CLAUDE.md` imports it with a line `@AGENTS.md`, and holds only what is for Claude Code alone. [2] [6] [8]
- **Skills** go in `.agents/skills`, which Codex and GitHub Copilot read. Claude Code reads `.claude/skills`, so the installer, `npx skills add`, links each skill there too. [3] [7] [9]
- **A check that must never be skipped** goes where every agent and every person meets it: a test, CI or a git hook. An agent's own hook runs only for that agent.
- **A kind only some agents have**, such as a rule for some files, an agent hook, an output style or a subagent: make it for each agent the project uses, in that agent's place below. Then add one line to `AGENTS.md` that says it exists and where, so the next agent knows.

Find which agents the project uses from their files, such as `CLAUDE.md`, `.claude`, `.codex`, `.github/copilot-instructions.md` or `.github/instructions`. Ask the user when it is not clear.

## The kinds

| The need | The kind | Where, for every agent | Why |
| --- | --- | --- | --- |
| Every session must know it, such as a build command or "never push to main" | A short line | `AGENTS.md` at the project root, or the user's shared rules for every project | Loaded in full at the start of every session. Keep it under 200 lines: every line costs on every request. [1] [2] [6] |
| A procedure, checklist or reference needed only sometimes | A skill | `skills/<kind>/<name>/SKILL.md` in a skills repository, installed into `.agents/skills` | Only its description loads at the start; the body loads when it is used. [3] [7] |
| A mechanical rule of code, such as a banned function or a folder | A check: a test such as Pest `arch()`, a linter rule, or a search for old code | `tests/`, the linter's config, `refactor-issues` and its checks file | A mechanical violation gets a deterministic check; prose rules are for judgement calls. [4] |
| It must happen every time, the same way, with no judgement | A test, CI or a git hook | `tests/`, `.github/workflows`, `.git/hooks` | An instruction is a request, not a guarantee. A check is enforcement, for every agent. [1] |
| The shape of an issue or a pull request | A GitHub template, which a rule points at | `.github/ISSUE_TEMPLATE`, `.github/pull_request_template.md` | One place for each shape, read by people, GitHub and agents alike. |
| A decision and its reason | An ADR | `docs/adr` | So the reason is never lost. [5] |

## The kinds that differ by agent

Make these for each agent the project uses, and name them in `AGENTS.md`.

| The need | The kind | Claude Code | Codex | GitHub Copilot |
| --- | --- | --- | --- | --- |
| It holds only for some files, such as the rules of controllers | A rule for some files | `.claude/rules/<subject>.md` with `paths` [2] | An `AGENTS.md` in that folder. Codex reads it only when it starts inside that folder, so name the rule in the root `AGENTS.md` too [6] | `.github/instructions/<subject>.instructions.md` with `applyTo` [8] |
| A workflow with side effects, or one the user starts on purpose | A skill only the user starts | `disable-model-invocation: true` in `SKILL.md` [3] | `allow_implicit_invocation: false` in `agents/openai.yaml` [7] | `disable-model-invocation: true` in `SKILL.md`, in VS Code [9] |
| A step the agent must run, or must not run, at a set moment | An agent hook | `.claude/settings.json` [1] | `.codex/config.toml` or `.codex/hooks.json` [10] | `.github/hooks/*.json` [8] |
| How every reply sounds: language, length, format | An output style, or personal instructions | `~/.claude/output-styles` [1] | `~/.codex/AGENTS.md` [6] | The personal instructions in Copilot's settings [8] |
| A side task that reads a lot but returns a little | A subagent or custom agent | `.claude/agents` [1] | Check its docs today | `.github/agents/<name>.md` [8] |
| Data or actions in another system | An MCP server, with a skill that says how to use it | `.mcp.json` [1] | `.codex/config.toml` [10] | `.vscode/mcp.json`, or the IDE's own file [8] |

## Which repository

- **A shared repository**: it holds for every project, or every project of one stack, such as the user's own repository of skills or rules. Projects get it on their next update from there.
- **The project**: only this project needs it, such as its own domain rules.
- **The user's own setup**: a personal preference for every project, which the team does not share. Each agent has its own folder, such as `~/.claude`, `~/.codex` or `~/.copilot`, and `~/.agents/skills` holds skills for every agent.

## Sources

1. Claude Code docs, [Extend Claude Code](https://code.claude.com/docs/en/features-overview): when to use CLAUDE.md, rules, skills, subagents, hooks and MCP.
2. Claude Code docs, [How Claude remembers your project](https://code.claude.com/docs/en/memory): CLAUDE.md, `AGENTS.md`, and rules with `paths`.
3. Claude Code docs, [Skills](https://code.claude.com/docs/en/skills), and the open [Agent Skills specification](https://agentskills.io/specification).
4. The `retro` skill of [mattpocock/skills](https://github.com/mattpocock/skills): a mechanical violation gets a check, a judgement call gets a written standard.
5. Michael Nygard, [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).
6. Codex docs, [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md): which `AGENTS.md` files load, from `~/.codex` to the folder you work in.
7. Codex docs, [Agent Skills](https://developers.openai.com/codex/skills): `.agents/skills`, `$` to call a skill, and `agents/openai.yaml`.
8. GitHub docs, [Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet): instructions, path rules, agents, hooks, skills and MCP.
9. VS Code docs, [Agent skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills): where Copilot finds skills, `/` to call one, and `disable-model-invocation`.
10. Codex docs, [Advanced configuration](https://developers.openai.com/codex/config-advanced) and [Hooks](https://developers.openai.com/codex/hooks): hooks and MCP servers in `.codex`.
