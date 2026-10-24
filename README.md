# Skills

My agent skills, for the work I do every day: handing fixes to CLI workers, refactoring old code without changing what users get, and placing new rules and skills where they belong.

They are small and easy to change. Take the ones you need, and make them your own.

They work beside [Matt Pocock's skills](https://github.com/mattpocock/skills). Some of mine call his, such as `implement` and `tdd`. When one is missing, the skill stops and gives you the command that installs it.

## Installation

Pick one way per agent. Installing both gives you every skill twice.

<details>
<summary><strong>Any agent</strong> (skills.sh, you update by hand)</summary>

```bash
npx skills add youssef-ahmed-Devlogs/skills
```

It asks which skills you want, for which agent, and where: in the current project, or in your home folder for every project. Update later with `npx skills update`.

</details>

<details>
<summary><strong>Claude Code</strong> (plugin)</summary>

```bash
claude plugin marketplace add youssef-ahmed-Devlogs/skills
claude plugin install youssef-ahmed-skills@youssef-ahmed
```

</details>

<details>
<summary><strong>Codex</strong> (plugin)</summary>

```bash
codex plugin marketplace add youssef-ahmed-Devlogs/skills
codex plugin add youssef-ahmed-skills@youssef-ahmed
```

</details>

## Engineering

- **[delegating-to-cli](./skills/engineering/delegating-to-cli/SKILL.md)**: Work through a list of fixes by handing each one to its own Claude Code CLI session in a terminal tab. You write the issue, answer the worker, review its diff, merge and clean up.
- **[implement-refactor-issues](./skills/engineering/implement-refactor-issues/SKILL.md)**: Do the open refactor issues that `refactor-issues` opened, one batch in one pull request, with what users get kept the same. Works in any project and any language.
- **[refactor-issues](./skills/engineering/refactor-issues/SKILL.md)**: Open the next batch of refactor issues that bring old code in line with the project's own code rules, safest first. Works in any project and any language.
- **[setup-refactor-issues](./skills/engineering/setup-refactor-issues/SKILL.md)**: Prepare a project for `refactor-issues`: write its checks file and reading list from its own code rules, wire in the ready checks of a stack's rules, and make the labels. Works in any project and any language.

## Productivity

- **[add-rule-or-skill](./skills/productivity/add-rule-or-skill/SKILL.md)**: Talk through something new you want an agent to know or do, such as a rule, a skill or a check. It finds out whether it exists, and what it should be and where it goes, from today's official docs.
- **[explain-skill](./skills/productivity/explain-skill/SKILL.md)**: Explain one skill in simple words, with a real example: what it does, when to use it, and what you get.
- **[interview-me](./skills/productivity/interview-me/SKILL.md)**: Think a plan, a decision or an idea through, one question per message, until the agent knows what you really want. It says it all back and starts nothing before your clear yes. Works for any subject. In a project it asks in the project's words, and offers to record each decision that needs an ADR.
- **[tutor-me](./skills/productivity/tutor-me/SKILL.md)**: Learn a topic over many sessions. It builds each lesson from trusted sources, then teaches it in the chat one part at a time, and moves on only when you show you understood.

## Laravel

The Laravel rules, their ready checks, and `setup-laravel-rules`, which puts them in a project, are in [youssef-ahmed-Devlogs/laravel-rules](https://github.com/youssef-ahmed-Devlogs/laravel-rules). Then `setup-refactor-issues`, `refactor-issues` and `implement-refactor-issues` work with them.

Every skill starts only when you type its name, such as `/refactor-issues`, apart from `interview-me`, which the agent and other skills can also run. Each one has a page in [`docs`](./docs) that says when to use it.

## License

[MIT](./LICENSE).
