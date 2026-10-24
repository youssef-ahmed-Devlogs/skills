# interview-with-docs

The same interview as [`interview-me`](./interview-me.md), inside a project, with the project's docs written while you talk. Each word you settle goes into the glossary at once, and each big decision can become an ADR, so the next person, or the next agent, knows what you meant.

**Start it:** `/interview-with-docs <subject>`, in the project's folder. It starts only when you type it.

## What it does

1. It reads the project's glossary, its ADRs, its rules for agents, and the code or files the subject touches.
2. It runs the interview of `interview-me`: one question per message, with its own guess, until it knows what you want.
3. When you use a word in another sense than the glossary's, or a word that could mean two things, it asks which one you mean.
4. It tests each line between two things with a made-up case right on it, and checks what you say against the code.
5. When a word is settled, it writes it in the glossary at once, and tells you in one line.
6. When a decision is hard to undo, would surprise a later reader, and came from a real choice, it offers an ADR, and writes it on your yes.
7. The summary at the end lists every word and every ADR it wrote.

## When to use it

| Your situation | Use |
| --- | --- |
| You plan a change inside a project, and want its words and decisions written down | `interview-with-docs` |
| You want to think a plan through, and need no docs from it | [`interview-me`](./interview-me.md) |
| The plan is not about a project, such as a trip or a job offer | [`interview-me`](./interview-me.md) |

## Example

A shop app has a `GLOSSARY.md`, six ADRs, and an order page where customers cancel a whole order:

```text
You:    /interview-with-docs let customers cancel part of an order

Agent:  I read GLOSSARY.md, the 6 ADRs in docs/adr, and the order code.

        What I understand: a customer can cancel some items of an order, not only all of it.
        How sure: 40%. Missing: until when, and what happens to the money.

        ❓ The glossary calls cancelling a whole order a "Cancellation". Should cancelling
           some items get a word of its own?
        ➡️ My guess: yes, a word of its own, since the money and the stock work differently.

You:    Yes. Call it "Item cancellation".

Agent:  Added to GLOSSARY.md: **Item cancellation**: a customer takes back one or more
        items of an order before it ships. _Avoid_: partial cancel, part refund.

        A case at the edge: the customer cancels all three items, one by one.
        ❓ Does the order then become a Cancellation, rather than three Item cancellations?
        ➡️ My guess: yes, so no order stays open with nothing in it.

You:    Yes. And the money always goes back to the card, never to store credit.

Agent:  That is a real choice, hard to undo once customers rely on it, and a later
        reader would ask why there is no store credit.
        ❓ Shall I write it as ADR 0007, "Refunds go back to the card"?
```

After a few more questions, the summary ends with what it wrote:

```text
- Decided: the money goes back to the card (ADR 0007); cancelling every item cancels the order.
- Docs written: "Item cancellation" in GLOSSARY.md; docs/adr/0007-refunds-go-back-to-the-card.md.

Is this right, or what should change?
```

## More use cases

- **A word everyone says differently:** "account" means the customer to sales and the login to support. It proposes one word for each, and writes both in the glossary.
- **The code says otherwise:** you say an order can be split, and the code never splits one. It shows you both, and asks which is right before it writes anything.
- **A project with no docs yet:** the first settled word makes `GLOSSARY.md`, and the first ADR makes `docs/adr`.
- **A project with its own rules for ADRs:** when its rules say when an ADR is due, or to write it without asking, it follows them.
- **Changing an old decision:** it writes a new ADR, and marks the old one as replaced by it. It never rewrites the old one.

## What you get

- The project's glossary, with each word you settled, written as you went.
- An ADR in `docs/adr`, or the place the project's rules name, for each decision you said yes to.
- The summary of `interview-me`, with a "Docs written" line.

It commits nothing: the files wait in the folder for you, or for the next step.

## What it needs

[`interview-me`](./interview-me.md) from this repository, which it runs. When it is missing, the skill stops and gives you the command:

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill interview-me
```

## Tips

- Correct a glossary line the moment it shows up. It is cheaper than finding the wrong word in the code later.
- Not every decision needs an ADR. When it offers none, the choice was easy to undo or obvious, and that is fine.
