# Productivity

Skills for work that is not code: rules, skills, the agent itself, and learning a topic.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[add-rule-or-skill](./add-rule-or-skill/SKILL.md)**: Talk through something new you want an agent to know or do, such as a rule, a skill or a check. It finds out whether it exists, and what it should be and where it goes, from today's official docs.
- **[explain-skill](./explain-skill/SKILL.md)**: Explain one skill in simple words, with a real example: what it does, when to use it, and what you get.
- **[tutor-me](./tutor-me/SKILL.md)**: Learn a topic over many sessions. It builds each lesson from trusted sources, then teaches it in the chat one part at a time, and moves on only when you show you understood.
