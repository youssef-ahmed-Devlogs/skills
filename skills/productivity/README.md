# Productivity

Skills for work that is not code: rules, skills, the agent itself, and learning a topic or following a course.

## Model-invoked

You can type them, and the agent or another skill can also run them when the task fits.

- **[interview-me](./interview-me/SKILL.md)**: Think a plan, a decision or an idea through, one question per message, until the agent knows what you really want. It says it all back and starts nothing before your clear yes. Works for any subject. In a project it asks in the project's words, and skips what its decision records already decided.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[add-rule-or-skill](./add-rule-or-skill/SKILL.md)**: Talk through something new you want an agent to know or do, such as a rule, a skill or a check. It finds out whether it exists, and what it should be and where it goes, from today's official docs.
- **[explain-skill](./explain-skill/SKILL.md)**: Explain one skill in simple words, with a real example: what it does, when to use it, and what you get.
- **[interview-with-docs](./interview-with-docs/SKILL.md)**: The interview of `interview-me` inside a project, with its docs written as you go. It settles each word with you, tests it with cases at the edge, checks it against the code, writes it in the glossary at once, and offers an ADR for each decision worth one.
- **[study-with-me](./study-with-me/SKILL.md)**: Follow a course, a book or a path you study on your own, with a teacher beside you. It knows where you are and reads your practice code, checks each step you finish, fills every gap so you never need another course, and tells the course's habits apart from the official way.
- **[tutor-me](./tutor-me/SKILL.md)**: Learn a topic over many sessions. It builds each lesson from trusted sources, then teaches it in the chat one part at a time, and moves on only when you show you understood.
