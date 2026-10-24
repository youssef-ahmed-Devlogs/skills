# Skills

Agent skills for Claude Code, Codex, GitHub Copilot and other agents: think a plan through before the work starts, learn a topic or follow a course with a teacher beside you, clean up old code safely, hand fixes to CLI workers, and keep your agents' rules in the right place.

They are small and easy to change. Take the ones you need, and make them your own.

**New here?** Read [the guide](./docs/README.md): which skill fits which job, and how they work together. Each skill has its own page with a full example.

## Install

```bash
npx skills add youssef-ahmed-Devlogs/skills
```

It asks which skills you want, and for which agents. Plugins for Claude Code and Codex, one skill at a time, and updates: [Installing](./docs/install.md).

Some skills call skills of [Matt Pocock](https://github.com/mattpocock/skills), such as `tdd`. When one is missing, the skill stops and gives you the command that installs it.

## The skills

### Thinking and learning

| Skill | Use it to |
| --- | --- |
| [interview-me](./docs/productivity/interview-me.md) | Say what you really want, one question at a time, before anything is built |
| [tutor-me](./docs/productivity/tutor-me.md) | Learn a topic from zero, with lessons the agent builds and teaches in the chat |
| [study-with-me](./docs/productivity/study-with-me.md) | Follow a course, a book or a path, with a teacher who checks each step |

### Your agents

| Skill | Use it to |
| --- | --- |
| [add-rule-or-skill](./docs/productivity/add-rule-or-skill.md) | Add a rule, a skill or a check for your agents, in the right place |
| [explain-skill](./docs/productivity/explain-skill.md) | Understand any skill in simple words, with an example |

### Code

| Skill | Use it to |
| --- | --- |
| [delegating-to-cli](./docs/engineering/delegating-to-cli.md) | Hand a list of fixes to CLI workers, one tab each, and review each one |
| [setup-refactor-issues](./docs/engineering/setup-refactor-issues.md) | Prepare a project to clean up its old code, once |
| [refactor-issues](./docs/engineering/refactor-issues.md) | Open issues for old code that breaks your rules, safest first |
| [implement-refactor-issues](./docs/engineering/implement-refactor-issues.md) | Do those issues in one pull request, with what users get kept the same |

## Laravel

The Laravel rules, their ready checks, and `setup-laravel-rules`, which puts them in a project, are in [youssef-ahmed-Devlogs/laravel-rules](https://github.com/youssef-ahmed-Devlogs/laravel-rules). Then the three refactor skills work with them.

## License

[MIT](./LICENSE).
