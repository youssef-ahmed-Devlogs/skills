# Skills

This repository holds Youssef Ahmed's agent skills. People install them with `npx skills add youssef-ahmed-Devlogs/skills`, or as a Claude Code or Codex plugin.

Skills are in bucket folders under `skills/`:

- `engineering/`: daily code work.
- `productivity/`: work that is not code, such as rules, skills, the agent itself, and learning a topic or following a course.

Every skill is in five places. When you add, rename or remove one, change all five in the same pull request:

1. Its folder, `skills/<bucket>/<name>/`, with a `SKILL.md` whose `name` equals the folder name.
2. Its `agents/openai.yaml`, for Codex.
3. Its line in the bucket's `README.md`, with the name linked to its `SKILL.md`.
4. Its row in the top `README.md`, in the group table that fits it, such as "Thinking and learning" or "Code", and its row in the table of `docs/README.md`. Both link the name to its docs page. When it is a step of a bigger job, such as the refactor skills, add it to "How they fit together" in `docs/README.md` too.
5. Its entry in the `skills` list of `.claude-plugin/plugin.json`, and its docs page, `docs/<bucket>/<name>.md`.

## Docs

Every skill's docs page is a copy of [`docs/TEMPLATE.md`](./docs/TEMPLATE.md), filled in, with the same parts in the same order: a title and one or two sentences, a **Start it** line, `What it does`, `When to use it` with a table of situations, `Example` with a real chat from start to end, `More use cases`, `What you get`, `What it needs`, and `Tips` when there are any.

- Write the example from the skill's own text, so it shows what the skill really does. An example names no private project: use a shop app, a team newsletter or a public course.
- A change to a skill's behaviour changes its docs page in the same pull request.
- The top `README.md` keeps its order: a short intro, Install, the skills in group tables, then the rest. Each row is one short line; the details live in the docs page.

Every skill here is user-invoked, apart from `interview-me`, which other skills run: `disable-model-invocation: true` in its `SKILL.md`, and `policy.allow_implicit_invocation: false` in its `agents/openai.yaml`. A model-invoked skill drops both, and its bucket `README.md` lists it under "Model-invoked".

A skill that needs a skill of another author, such as Matt Pocock's `tdd`, says so in a "Before you start" part, with the command that installs it from that author's repository. Never copy another author's skill here.

Raise the `version` in `.claude-plugin/plugin.json` when a change should reach plugin users: plugins update only when it changes.

Write in very simple English: short sentences, common words, one idea per sentence. No em-dashes. Name no private project, client or repository.

Every change goes through a pull request to `main`.
