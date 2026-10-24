## What it does

`interview-me` asks you about a plan, a decision or an idea until it knows what you really want, before anything is built or written. It asks one question per message, always, and gives its own guess with each one, so you can answer with a quick "yes" or a correction.

It starts by saying what it understands so far, and how sure it is. It looks up facts itself, and asks you only what you must decide. When an answer sounds like what one is supposed to say, it asks what you would pick if you did not have to convince anyone.

When it could guess your next answers, it writes everything back: the goal, for whom, why now, when it is done, the limits, what is left out, and each choice you made. It starts nothing until you say a clear yes.

In a project with its own docs, it first reads the glossary, the ADRs and the rules for agents. It asks in the project's words, skips what an ADR already decided, and when a decision needs an ADR, or a new word needs the glossary, it says so and writes it only on your yes.

## When to reach for it

Type `/interview-me <subject>`, such as `/interview-me a new search page` or `/interview-me my plan for next month`. Use it when you know roughly what you want but have not said it all, or when you want the agent to understand you before it acts. It works for any subject, code included.

It is the one skill here that the agent can also start by itself, so your other skills can run it first, such as a skill that writes a spec.

## Prerequisites

None.
