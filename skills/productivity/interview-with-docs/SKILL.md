---
name: interview-with-docs
description: Interview the user about a plan or a design inside a project, one question per message, and keep the project's glossary and decision records up to date as the answers come. Settles each word with them, tests it with cases at the edge, checks what they say against the code, and offers an ADR for each decision worth one.
disable-model-invocation: true
argument-hint: "What should we think through?"
---

# Interview with docs

Run the interview of `interview-me` with the user, and build the project's docs while it runs. Each word you settle goes into its glossary at once. Each decision worth keeping gets a decision record, an ADR. At the end, the project knows what the user meant, not only this chat.

## Before you start

Run the `interview-me` skill and follow all of it: one question per message, your guess with each one, the summary, and the wait for a clear yes. This skill adds the docs on top. On the docs, this skill wins. On everything else, `interview-me` does.

When `interview-me` is not installed, stop and give the command that installs it:

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill interview-me
```

This needs a project folder to write in, with code or not. When you are not inside one, ask where the docs should go, or offer `interview-me` alone.

## 1. Find the project's docs

Before the first question, find:

- **The glossary:** `GLOSSARY.md`, or a map of several, such as `CONTEXT-MAP.md` or `GLOSSARY-MAP.md`, with a glossary for each part. With several, find which part the subject belongs to. Ask only when you cannot tell.
- **The decision records:** `docs/adr`, or the place the project's rules name.
- **The rules for agents:** `AGENTS.md`, `CLAUDE.md` or `.claude/rules`. When they say how or when to write a glossary or an ADR, follow them over this skill.
- **The code or the files the subject touches,** so you can check what the user says against them.

A file or a folder that does not exist yet is made only when you have the first thing to write in it.

## 2. During the interview

Each of these is a question of its own, still one per message, with your guess.

### A word that clashes with the glossary

When the user uses a word in another sense than the glossary's, say so before any other question: "The glossary says a 'booking' is a paid seat, but you seem to mean a held seat. Which is it?". When the glossary lists the word to avoid, give the word it uses.

### A vague word

When a word could mean two things, such as "account" for both the customer and their login, propose one exact word for each thing, and ask which one they mean.

### A case at the edge

When the answers draw a line between two things, test the line with a made-up case right on it: "A customer cancels one item of three. Is the order cancelled?". A case shows where a word is still unclear faster than a definition does.

Test the end of each new thing too: what is left after its last step, and what state it is in. "The customer removes the last item. Is the order still open, with nothing in it, or cancelled?"

### A way around a decision

When a decision opens a way around another one, ask about it at once, as a question of its own: close it, or accept it. "Removing every item one by one gives store credit, but you said a cancelled order goes back to the card. Is that fine?". Never leave it only as a note in the summary.

### What the files say

When the user says how something works today, check the code or the files. When the two disagree, say both: "The code cancels the whole order, but you said one item can be cancelled. Which is right?". Never ask what you can read.

## 3. Write the glossary as you go

When a word is settled, write it in the glossary at once, in that same message. Do not keep a list for the end. Say in one line what you wrote, so the user can correct it: "Added to `GLOSSARY.md`: **Booking**: a seat held for a customer, paid or not." The other words you or the user used for the same thing go under _Avoid_.

Use [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md), unless the project's glossary has a shape of its own.

The glossary holds only the words of this project, as its people say them. No code details, no plans, and no general words such as "cache" or "timeout". It is not a spec or a notebook.

## 4. Offer a decision record when it is worth one

Offer an ADR only when all three hold:

1. **Hard to undo:** changing it later costs real time or money.
2. **Surprising later:** someone who reads the work next year would ask "why this way?".
3. **A real choice:** there were real options, and one was picked for reasons.

When one is missing, write no ADR: an obvious choice, or one easy to undo, only adds noise. When the project's rules say when an ADR is due, they decide instead.

Offer it in one line, at the moment the decision is made, and write it on a yes. The offer is the one question of that message: any other question waits for the next one. When the project's rules say to write ADRs without asking, write it and say so in one line. Use [ADR-FORMAT.md](./ADR-FORMAT.md), or the project's own format.

A decision that changes an older ADR gets a new ADR. Mark the older one by how much changed:

- **All of it:** `Status: Replaced by 0004.`
- **Only a part:** `Status: Partly replaced by 0004.` The new ADR says which part changed, and which part still holds.

Never rewrite an ADR that was there before this interview, apart from that status line.

## 5. The summary

Before the summary, check that you asked the end of each new thing, as "A case at the edge" says: what is left after its last step, and what state it is in, such as a gift card with nothing left on it. When one is missing, ask it first, even when the user says that is all, and say it is the last question.

In the summary of `interview-me`, the "Decided" line names the ADR of each decision that has one. Add one line before the question:

```
- Docs written: {each word added to the glossary, and each ADR with its file}
```

A word or a record still in doubt goes under "Still open".

At the clear yes, read what you wrote once more against the final summary. A word or a decision that changed later in the interview is fixed now: an ADR written in this interview may still change, since nobody relies on it yet. Do not commit the files: that is the user's call, or the next step's.
