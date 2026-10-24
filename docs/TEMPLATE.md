# {skill-name}

{One or two sentences: what the skill does for the reader, in plain words.}

**Start it:** `/{skill-name} {what to type after it}`. {It starts only when you type it. | The agent, or another skill, can also start it.}

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill {skill-name}
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** {The skills it calls, with the command that installs them, and the tools such as `git` or `gh`. Or "Nothing."}

**Where to run it:** {Any session in any folder, inside the project's folder, or a new folder. For a new folder: say that the reader makes it, a name such as `learn/docker`, and that they open the agent in it. Say what the skill writes and where.}

**Call it:** in Claude Code or GitHub Copilot, type `/{skill-name} {...}`. In Codex, type `${skill-name} {...}`.

**Agents:** {Claude Code, Codex and GitHub Copilot, or any agent that reads skills. Or the agents it is limited to, and why.}

## What it does

1. {Its steps, one short line each, in the skill's own order.}

## When to use it

| Your situation | Use |
| --- | --- |
| {The situation it fits} | `{skill-name}` |
| {A close situation where another skill fits better} | [`{other-skill}`](./{other-skill}.md) |

## Example

{One real situation, from what the reader types to what comes out. Use a made-up case anyone knows, such as a shop app, a team newsletter or a public course. Never a private project.}

```text
You:    /{skill-name} {...}

Agent:  {...}
```

## More use cases

- **{A case}:** {one or two lines.}

## What you get

{The files, issues, pull requests or answers at the end, and where they go.}


## Tips

- {Only when there are real ones. Drop this part otherwise.}
