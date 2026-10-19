## What it does

`add-rule-or-skill` talks through something new you want an agent to know or do: a rule, a skill, a hook or a check. It searches the project, your own setup and your shared repositories, so you do not add something that already exists. Then it researches the official docs again, that day, and tells you what kind it should be and where it goes.

It writes nothing until you agree.

## When to reach for it

Type `/add-rule-or-skill` when you have an idea for your agents and do not know whether it exists, or where it belongs.

## Prerequisites

Matt Pocock's [`writing-for-agents`](https://github.com/mattpocock/skills), which it follows when it writes a skill or a rule. When it is missing, the skill stops and gives you the command that installs it.
