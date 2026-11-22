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

1. Chooses each short question from the subject and what the learner has already said. A question can help choose the starting point, a foundation or a type of practice. Once the answers are enough to propose the lessons, it shows the plan in chat. Explanations, examples and quizzes belong in the site after approval.
   If a needed skill is missing, it explains where the learner will use it and pauses. The learner can switch to a separate foundations course, include a short introduction in this course, or start the original topic directly. They then review and approve the lesson plan for their chosen route.
2. Opens with a lesson on what the subject is, why it arose and where it is used. Each new concept gets an explanation before its worked example and practice.
3. Places the guide and controls on the right in Arabic and on the left in English. The lesson index sits across the scene on desktop. On a phone the guide comes first and the index opens in a drawer. The other course pages follow the same reading order.
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

Agent:  I'll use this chat to plan the site. Have your readers used Git before?
You:    They can commit and read the log. They lose track of which branch moves.
Agent:  How much practice time should the course fit?
You:    Twenty minutes. Let them try it on a graph.
Agent:  They already know commits. The gap is tracking branch labels.
        I suggest two short lessons. First, what is a branch and why would
        a team need one? Then switch branches and trace a commit. Finish by
        predicting both labels on an unfamiliar graph. Shall I build that?
You:    Yes, build that version.
Agent:  The course is ready. Start with why teams use branches.
```

## More use cases

- Teach rhythm by letting the learner change tempo and subdivision separately.
- Teach averages by changing one observation and comparing the mean with the median.

## What you get

A working website in your chosen folder. Full courses include guided lessons, practice, a lab and quick reference sheets. The controls, scene labels and feedback support both languages. The course keeps your reading place and preferences on your device.

Read the current task and explanation in the step guide. A single Notes section collects any hints and feedback. The diagram keeps its labels and values. Lesson goals, explanations and small labels use bold text. Code blocks use the bundled JetBrainsMono Nerd Font Mono in both languages, including offline.
