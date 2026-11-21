# visual-learning-studio

Build a visual lesson or a whole learning website. Readers can switch between Arabic and English, try a change in the diagram, and see what it does.

**Start it** with `/visual-learning-studio Build a visual course on Git branches for beginners`.

## Before you start

**Install it** with the skills installer.

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill visual-learning-studio
```

Pick the agents you use. Other install options and updates are in [Installing](../install.md).

**It needs** an agent that can write and test a website. The styles, controls, icons and fonts come with the skill.

**Where to run it** is the folder where you want the website. For a new course, make a folder such as `learn/git` and open your agent there.

**Call it** with `/visual-learning-studio` in Claude Code or GitHub Copilot, or `$visual-learning-studio` in Codex. Add a topic and tell it what the learner should be able to do.

**Agents** include Claude Code, Codex, GitHub Copilot and other agents that read skills and can build web pages.

## What it does

1. Starts from a task the learner wants to do and works back to the first lesson.
2. Builds scenes that change one thing at a time and show its effect.
3. Adds a course tree, a step guide, a timeline and controls for both languages and themes.
4. Tests the path, the controls and the layout on small and large screens.

## When to use it

| Your situation | Use |
| --- | --- |
| You want a website people can use to learn at their own pace | `visual-learning-studio` |
| You want a teacher to work with you in the chat | [tutor-me](./tutor-me.md) |

## Example

```text
You:    /visual-learning-studio Build a beginner course on Git branches.
        I want readers to predict which branch moves after a commit.

Agent:  The first lesson starts with two labels on the same commit.
        Pick a branch, predict which label moves, then commit and check.
        Later, try the same decision with another branch checked out.
        The website opens at the first lesson. Use the folder tree to jump
        ahead, or switch to the lab to try another history.
```

## More use cases

- Teach rhythm by letting the learner change tempo and subdivision separately.
- Teach averages by changing one observation and comparing the mean with the median.

## What you get

A working website in your chosen folder. Full courses include guided lessons, practice, a lab and quick reference sheets. The controls, scene labels and feedback support both languages. The course keeps your reading place and preferences on your device.
