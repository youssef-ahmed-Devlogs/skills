---
name: explain-skill
description: Explain one skill in simple words, with a real example. Use when the user types a skill's name and wants to know what it does, when to use it, and what they get.
disable-model-invocation: true
---

# Explain a skill

The user names a skill, such as `/explain-skill to-spec`. Explain it so a beginner gets it in one read.

## 1. Find it and read it all

Look for the skill's folder in `.agents/skills/<name>`, `.claude/skills/<name>`, `~/.claude/skills/<name>`, then in [youssef-ahmed-Devlogs/skills](https://github.com/youssef-ahmed-Devlogs/skills) at `skills/<kind>/<name>`, then in [Matt Pocock's skills](https://github.com/mattpocock/skills). Read its `SKILL.md` and every file it points to: the explanation comes from what the skill says, never from its name alone.

No name given: ask for one. No skill of that name: name the closest ones, and stop.

## 2. Explain it, in this order

Write in the user's language, in short plain sentences, with no jargon a beginner would not know. When the skill uses a word of its own, such as _seam_ or _frontier_, say what it means the first time.

1. **What it is**: one or two sentences.
2. **When to use it**: the situation, and one case where another skill fits better, with that skill's name.
3. **What it does**: its steps, one short line each, in its own order.
4. **What you get at the end**: a file, an issue, a branch, a review, or an answer.
5. **An example**: one real situation from start to end: what the user types, what the skill asks or does, and what comes out. Use the kind of project the user works on now when you can tell.
6. **What it needs**: the skills it calls, from its "Before you start" part, and whether each is installed. Give the install command for a missing one.
7. **What comes before and after it**: the skills it usually follows or leads to, as the skill and its author's README lay them out.

Keep it under 40 lines. Done when every part above is there and nothing in it goes beyond what the skill's files say.
