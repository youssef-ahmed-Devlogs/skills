# ADR format

An ADR is a short note of one decision: what was decided, and why. ADRs live in `docs/adr`, numbered: `0001-short-name.md`, `0002-short-name.md`. The next number is one above the highest there.

```md
# {The decision, as a short title}

{A few sentences: the situation, the decision, and why.}
```

That is often enough. Add a part only when it helps a later reader:

- **Options turned down:** when someone would suggest them again.
- **What follows:** when the decision forces something that is not obvious.
- **Status:** such as `Replaced by 0007` when a later decision changes all of this one, or `Partly replaced by 0007` when it changes only a part.

## What deserves one

- The shape of the system, such as one app or several.
- A tool or a service that would take months to swap, such as the database or the payment provider.
- A line between two parts: which one owns what.
- A choice against the obvious way, so nobody "fixes" it later.
- A limit the work does not show, such as a law, a contract or a client's demand.
- An option turned down for reasons that are not obvious.

A choice that is easy to undo, or the one anyone would make, needs no ADR.
