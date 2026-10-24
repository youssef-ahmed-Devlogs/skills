# explain-skill

You see a skill and do not know what it does. This skill reads it in full and explains it in simple words, with a real example.

**Start it:** `/explain-skill <name>`. It starts only when you type it.

## What it does

1. It finds the skill: in your project, in your home folder, then in this repository and in [Matt Pocock's skills](https://github.com/mattpocock/skills).
2. It reads its `SKILL.md` and every file it points to. It never guesses from the name.
3. It explains it in your language, in this order: what it is, when to use it, its steps, what you get, an example, what it needs, and what comes before and after it.

## When to use it

| Your situation | Use |
| --- | --- |
| You want to know what a skill does before you run it | `explain-skill` |
| You want to know which skill fits a job | [The guide](../README.md) |
| You want to add or change a skill | [`add-rule-or-skill`](./add-rule-or-skill.md) |

## Example

```text
You:    /explain-skill refactor-issues

Agent:  What it is: it opens GitHub issues for old code that breaks your project's own
        rules, without changing what users get.

        When to use it: your rules grew, and old files do not follow them yet. If no rules
        are written, write them first.

        What it does:
        1. Checks the project is set up, by setup-refactor-issues.
        2. Reads your rules, and runs the project's searches.
        3. Grades each file by how much a mistake could hurt.
        4. Opens up to 10 issues, safest files first, one file each.

        What you get: issues labelled `refactor`, ready for an agent.

        Example: in a shop app, `src/utils/date.ts` uses console.log, which your rules ban.
        It opens "Refactor src/utils/date.ts", with what to change and how the output stays
        the same.

        It needs: setup-refactor-issues run once, and gh.
        Before it: setup-refactor-issues. After it: implement-refactor-issues.
```

## More use cases

- **A skill of another author:** such as `/explain-skill tdd`, before you add it to your work.
- **A skill a teammate added:** to know what it does before it runs in your project.
- **No such skill:** it names the closest ones, and stops.

## What you get

An answer in the chat, under 40 lines. It writes no file.

## What it needs

Nothing.
