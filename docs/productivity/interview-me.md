# interview-me

The agent asks you about a plan, a decision or an idea, one question at a time, until it knows what you really want. Nothing is built or written before your clear yes.

**Start it:** `/interview-me <subject>`. The agent, or another skill, can also start it by itself when a request is not clear yet.

## What it does

1. It says in one line what it understands so far, and how sure it is, from 0 to 100%.
2. It asks one question per message, always, with its own guess, so a quick "yes" is often enough.
3. It looks up facts itself, in your files, your docs or the web, and asks you only what you must decide.
4. When an answer is vague, such as "professional" or "scalable", its next question is what that word means to you.
5. When it could guess your next three answers, it writes it all back: the goal, for whom, why now, when it is done, the limits, what is left out, and each choice you made.
6. It waits for a clear yes. "Sounds good" is not one.

## When to use it

| Your situation | Use |
| --- | --- |
| You know roughly what you want, but have not said it all | `interview-me` |
| You want the agent to understand you before it writes a spec or code | `interview-me` |
| You already know exactly what to build, step by step | Ask for it directly |
| You plan inside a project, and want its glossary and ADRs written as you go | [`interview-with-docs`](./interview-with-docs.md) |
| You want to learn a topic, not plan something | [`tutor-me`](./tutor-me.md) |

## Example

You want a small newsletter for your team, and you have not thought it through:

```text
You:    /interview-me a weekly newsletter for my team

Agent:  What I understand: you want a short weekly mail that keeps your team up to date.
        How sure: 25%. Missing: who writes it, what goes in it, and what done looks like.

        ❓ Will you write each issue yourself, rather than collect parts from the team?
        ➡️ My guess: yes, by yourself, since you said "for my team", not "by my team".

You:    No, each person adds one line about their week.

Agent:  What I understand: a weekly mail built from one line by each person.
        How sure: 45%.

        ❓ Should the agent remind people on Thursday, and send it on Friday?
        ➡️ My guess: yes, a reminder and a fixed day, so nobody has to chase anyone.
```

After a few more questions it writes the summary:

```text
What you want:

- Goal: a weekly team mail, one line from each person.
- For whom: the 8 people of the team, and the manager.
- Why now: people miss what others did, and meetings run long.
- Done when: a mail goes out every Friday, with no one chasing lines by hand.
- Limits: no new paid tool; it uses the team's mail and chat.
- Not doing: no design work, no archive site.
- Decided: a reminder on Thursday at noon; people who skip a week are left out, not chased.
- Still open: the mail's title.

Is this right, or what should change?
```

## More use cases

- **Before a feature:** "/interview-me a search page for the shop". The summary becomes the input of a spec or a plan.
- **A choice of your own:** which laptop to buy, whether to take a job offer, how to plan a trip.
- **A piece of writing:** a talk, a blog post or a CV, so the agent knows the reader and the point before it drafts.
- **Inside a project with docs:** it reads the glossary, the ADRs and the rules for agents first. It asks in the project's words, and skips what an ADR already decided. It writes nothing in them: for that, use [`interview-with-docs`](./interview-with-docs.md).
- **From another skill:** a skill that writes specs can run it first, so the spec rests on your answers.

## What you get

A short summary you can correct line by line, and a list of next steps, such as saving it to a file or turning it into a spec. It writes no file unless you agree.

## What it needs

Nothing. It needs you in the chat to answer: in a scheduled run with nobody there, it stops and says what is unclear.

## Tips

- Answer "I don't know" when you don't. It gives you two concrete options instead.
- When its guess is wrong, say so plainly. It guesses wrong on purpose now and then, to check you are not only being polite.
