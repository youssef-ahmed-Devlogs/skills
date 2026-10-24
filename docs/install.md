# Installing

Pick one way per agent. Installing the same skills in two ways gives you every skill twice.

## Any agent, with skills.sh

```bash
npx skills add youssef-ahmed-Devlogs/skills
```

It asks which skills you want, for which agents, and where: in the current project, or in your home folder for every project.

To skip the questions, name what you want. This puts `tutor-me` in your home folder, for Claude Code and Codex:

```bash
npx skills add youssef-ahmed-Devlogs/skills -g -y -a claude-code -a codex --skill tutor-me
```

- `-g`: for every project, not only the current one.
- `-a`: one agent each time, such as `claude-code`, `codex` or `github-copilot`.
- `--skill`: one skill each time. Leave it out to pick from the list.

Update later with:

```bash
npx skills update
```

## Call a skill

| Agent | Type | Example |
| --- | --- | --- |
| Claude Code | `/` and the skill's name | `/tutor-me Docker` |
| Codex | `$` and the skill's name, or `/skills` to pick one | `$tutor-me Docker` |
| GitHub Copilot | `/` and the skill's name | `/tutor-me Docker` |

Each skill's page says where to run it: in any session, inside your project, or in a new folder you make for it.

## Change agents

The skills' files are plain Markdown, and their rules go where every agent reads them, such as `AGENTS.md`. So a project or a course you started with one agent goes on with another: install the same skills for the new agent, open it in the same folder, and call the skill again.

## Claude Code, as a plugin

```bash
claude plugin marketplace add youssef-ahmed-Devlogs/skills
claude plugin install youssef-ahmed-skills@youssef-ahmed
```

The plugin holds every skill, and updates when a new version comes out.

## Codex, as a plugin

```bash
codex plugin marketplace add youssef-ahmed-Devlogs/skills
codex plugin add youssef-ahmed-skills@youssef-ahmed
```

## Skills of other authors

Some skills here call skills of [Matt Pocock](https://github.com/mattpocock/skills), such as `tdd` and `code-review`. Each page says which ones under "What it needs". When one is missing, the skill stops and gives you the command that installs it.
