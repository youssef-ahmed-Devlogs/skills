---
name: interview-me
description: Interview the user, one question per message, until you know what they really want from a plan, a decision or an idea, before anything is built or written. Works for any subject, not only code.
disable-model-invocation: true
argument-hint: "What should we think through?"
---

# Interview me

The user has a plan, a decision or an idea, and wants you to understand it the way they do before you act on it. What people ask for is often not what they need: someone asks for "an app" when a shared sheet would do. Find the gap now, while it costs nothing. Ask one question at a time until you could answer for them, then say it all back and wait for a clear yes.

The subject can be anything: a feature, a trip, a business choice, a piece of writing, what to do next. Write no files unless the user asks.

This needs the user in the chat. When nobody can answer, such as in a scheduled run, stop and say what is unclear instead of guessing.

## 1. Say what you understand now

Before the first question, write your current read of what the user wants in one sentence, and how sure you are, from 0 to 100%. Below 70%, add what is missing.

```
What I understand: you want a simple way to see where your money goes each month.
How sure: 30%. Missing: who else uses it, and what done looks like.
```

When an answer changes your read, write the new one the same way, in two lines. The number should rise as you go. Be honest with it: a number you cannot back up helps nobody.

## 2. Ask one question

- **One question per message, always.** Never two, and never a numbered list, even when several questions are ready. Keep the others for later messages.
- **Give your guess with it, and why.** Word the question so that "yes" takes your guess. Reacting to a guess is faster than answering from nothing, and it shows your own assumptions.
- **Ask first what other questions hang on.** A question whose answer depends on one still open waits until that one is answered.
- **Find facts yourself.** When a question needs a fact you can look up, in the files, the docs or the web, look it up, or send a sub-agent, and do not ask. Ask the user only what they must decide, or what only they know.
- **Guess wrong on purpose now and then,** in a direction you expect them to push back on. A user who agrees with every guess may only be polite.

```
❓ Will you write down each payment yourself, rather than have it read your bank statements?

➡️ My guess: yes, by hand, since you said you want to "keep an eye on it". Reading statements would change the whole tool.
```

## 3. Listen to the answer

- **What they want, or what sounds right.** Answers like "scalable", "clean", "the way most apps do it" or "I should probably" are what a good answer sounds like, not what the user wants. Ask: "If you did not have to convince anyone, what would you pick?"
- **"Whatever you think" is not an answer.** The user has not decided. Give two concrete options and ask which one.
- **"I don't know" is a real answer.** Offer two concrete options, or keep it as an open point for the summary.
- **Some questions cannot be settled by talking,** such as how a page should look or how a text should sound. Offer a quick rough draft for the user to react to, then come back to the question.
- **An answer that changes an earlier one** reopens it. Say so, and ask again what it changed.

## 4. Know when to stop

Stop asking when you could guess the user's answer to the next three questions you would ask. That is the test, not a feeling.

When many questions have gone by and your read is not getting clearer, the questions are wrong, or something basic is missing. Say so plainly, and ask whether to step back to the goal.

## 5. Say it back

Write back what the user wants, in their own words where you can, short enough to correct line by line:

```
What you want:

- Goal: {one line}
- For whom: {one line}
- Why now: {one line}
- Done when: {one line, something anyone could check}
- Limits: {time, money, tools, people}
- Not doing: {what is left out on purpose}
- Decided: {each choice made in the interview, one line each}
- Still open: {what the user did not know yet, if anything}

Is this right, or what should change?
```

Never leave out "Not doing": half of all misunderstandings are about what is not part of the work.

## 6. Wait for a clear yes

- "Sounds good", "sure, go" and "whatever you think" are not a yes. Ask what they would change, or give two options.
- A correction goes into the summary. Write it again and ask again.
- On a clear yes: give the final summary, offer the next steps, such as saving it to a file or turning it into a spec or a plan, and stop. Do nothing else in that turn, and start no work until the user picks a step.
