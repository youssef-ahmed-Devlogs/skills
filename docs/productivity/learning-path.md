# learning-path

Turn a topic into a course in the Learn site template. Each lesson asks you to predict two outcomes, try them, then apply what you learned to one project.

**Start it** with `/learning-path Teach me Go`.

## Before you start

**Install it** globally for Claude Code, Gemini CLI and Codex.

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill learning-path -g -a claude-code gemini-cli codex -y
```

After a change reaches the default branch, update this skill with `npx skills update learning-path -g`. See the [installation guide](../install.md).

**It needs** Node.js to build the site. Checking the examples may need the tools for the subject you choose.

**Where to run it** Open the workspace where you want the course. The agent creates a folder for the topic. If you have a practice project, give its path so the exercises can use its files.

**Call it** with `/learning-path` in Claude Code or `$learning-path` in Codex. In Gemini CLI, ask to use the skill by name.

**Agents** Claude Code, Gemini CLI, Codex and other agents that can read skills and write local files.

## What it does

1. Picks a final task and orders the lessons so each new idea comes before its first use.
2. Copies the bundled Learn template and writes every lesson in English and Arabic.
3. Builds two cases per lesson. You change one condition, compare the results and try it in your project.
4. Checks the sources, builds the site and tests the pages and controls.

## When to use it

| Your situation | Use |
| --- | --- |
| You want the Learn layout and a course built around one project | `learning-path` |
| You have a book or course and want someone to study it with you | [study-with-me](./study-with-me.md) |

## Example

```text
You:    /learning-path Teach me Python. I use spreadsheets to plan my reading.
Agent:  Open the first lesson. Predict which session the planner will suggest
        from 25, 10 and 40 minutes. Run both examples, then change the list.
        Your exercise is to recommend the shortest session and keep the
        original log in the order you entered it.
```

## More use cases

- Learn Go by extending a small shop API you already run.
- Reopen a generated course and add a section that builds on its last checkpoint.

## What you get

Open `index.html` in the course folder. It links to the lessons, practice tasks and quizzes. The folder also contains the editable course data, the generator and its stylesheet.
