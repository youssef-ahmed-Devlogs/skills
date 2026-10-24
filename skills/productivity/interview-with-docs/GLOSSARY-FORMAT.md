# Glossary format

A project has one glossary, `GLOSSARY.md` at its root. A project with several parts, each with words of its own, has a map at its root that lists them, and a glossary in each part's folder.

## A glossary

```md
# {Name of the project or the part}

{One or two sentences: what this part is, and why it is there.}

## Words

**Order**:
What a customer buys in one go.
_Avoid_: purchase, basket

**Refund**:
Money sent back to a customer for an order, or for part of one.
_Avoid_: return, chargeback
```

## Rules

- One word for each thing. When people use several, pick the best one, and list the others under _Avoid_.
- Say what the thing is, in one or two sentences, not what the code does with it.
- Only the words of this project. A general word, such as "cache" or "error", stays out, even when the project uses it a lot.
- Put the words under small headings when they fall into groups. A short glossary needs none.

## A map of several glossaries

```md
# Glossary map

- [Orders](./src/orders/GLOSSARY.md): what customers buy, and its states
- [Billing](./src/billing/GLOSSARY.md): invoices and payments

## How they meet

- Orders tells Billing when an order is paid.
```

When the subject belongs to one part, write in that part's glossary. When you cannot tell which, ask.
