# Skills

This repository holds Youssef Ahmed's agent skills. People install them with `npx skills add youssef-ahmed-Devlogs/skills`, or as a Claude Code or Codex plugin.

Skills are in bucket folders under `skills/`:

- `engineering/`: daily code work.
- `productivity/`: work around the code, such as rules, skills and the agent itself.
- `laravel/`: skills for Laravel projects only.

Every skill is in five places. When you add, rename or remove one, change all five in the same pull request:

1. Its folder, `skills/<bucket>/<name>/`, with a `SKILL.md` whose `name` equals the folder name.
2. Its `agents/openai.yaml`, for Codex.
3. Its line in the bucket's `README.md`, with the name linked to its `SKILL.md`.
4. Its line in the top `README.md`, with the name linked to its `SKILL.md`.
5. Its entry in the `skills` list of `.claude-plugin/plugin.json`, and its docs page, `docs/<bucket>/<name>.md`.

Every skill here is user-invoked: `disable-model-invocation: true` in its `SKILL.md`, and `policy.allow_implicit_invocation: false` in its `agents/openai.yaml`. A model-invoked skill drops both, and its bucket `README.md` lists it under "Model-invoked".

A skill that needs a skill of another author, such as Matt Pocock's `tdd`, says so in a "Before you start" part, with the command that installs it from that author's repository. Never copy another author's skill here.

Raise the `version` in `.claude-plugin/plugin.json` when a change should reach plugin users: plugins update only when it changes.

Write in very simple English: short sentences, common words, one idea per sentence. No em-dashes. Name no private project, client or repository.

Every change goes through a pull request to `main`.
