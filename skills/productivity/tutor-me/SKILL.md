---
name: tutor-me
description: Tutor the user in a topic over many sessions. Builds each lesson as a Markdown file from trusted sources, then teaches it in the chat one part at a time, and moves on only when the user shows they understood.
disable-model-invocation: true
argument-hint: "What do you want to learn?"
---

# Tutor me

The user wants to learn a topic over many sessions. You build each lesson as a Markdown file from trusted sources, then teach it to them in the chat, one part at a time. The lesson file is for you, not for them: they learn from the talk, so never ask them to read it.

## Before you start

The first session settles the user's goal with the `interview-me` skill. Run it and follow all of it: one question per message, your guess with each one, the summary, and the wait for a clear yes. On the goal, `interview-me` decides how you ask. On everything else, this skill does.

When `interview-me` is not installed, stop and give the command that installs it:

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill interview-me
```

## The workspace

Write every file in the folder the user ran this skill in. The files hold where the user stands, so a new session goes on where the last one stopped. Make each one only when it is first needed. [WORKSPACE-FORMAT.md](./WORKSPACE-FORMAT.md) gives the shape of each.

- `GOAL.md`: what the user wants to do with the topic. Every lesson serves it.
- `SOURCES.md`: the trusted sources the lessons are built from.
- `lessons/01-<name>.md`: one lesson each, with its parts, its checks and how far the user got. Its shape is in [LESSON-FORMAT.md](./LESSON-FORMAT.md).
- `KNOWN.md`: what the user knew before, what they have shown since, and the wrong ideas they dropped.
- `TERMS.md`: the words of the topic, once the user uses them right.
- `sheets/<name>.md`: short sheets to look things up later, such as syntax, steps or a process. These are the only files the user reads.
- `NOTES.md`: how the user likes to be taught, questions to come back to, and your working notes.

## Each session

1. Read `GOAL.md`, `SOURCES.md`, `NOTES.md`, `KNOWN.md`, and the lesson in progress: the newest lesson that is not done.
2. When there is no goal yet, run the interview of `interview-me` on what the user wants to do with the topic. After their clear yes, write `GOAL.md` from its summary, before the first lesson: its Goal, Done when, Limits and Not doing become the Goal, Done when, Time and limits and Not for now of `GOAL.md`. When the topic is a tool, a language or a framework, find the version the user works with, from their project's lock files or by asking, and write it in `GOAL.md`. Then ask three short questions that show what they know already, and write what they show in `KNOWN.md`.
3. When an earlier lesson is done, warm up first, from memory: one question on the last lesson, and one on the lesson recalled longest ago, each in its own message. Answer each reply as "Answering the user" says, and after a miss ask a new question on the same point. Write the result in `KNOWN.md`. A lesson leaves the warm-ups once three later sessions have recalled it.
4. When a lesson is in progress, go on from its first part that is not done. Otherwise build the next lesson.
5. Teach the lesson in the chat.
6. When the lesson is done, add what the user showed to `KNOWN.md`, `TERMS.md` and `sheets/`, and mark the lesson done. Give the user the link of its best source. Then ask whether to start the next lesson now.

## Build a lesson

- Pick what to teach from `GOAL.md` and `KNOWN.md`: the next step the user can reach with some effort, not one they already know and not one far ahead. When the user names a topic, teach that.
- Find sources first, starting from `SOURCES.md`, and search for more when it lacks the lesson's topic. Never build a lesson from your own memory alone. Add each good source to `SOURCES.md`, with the version it holds for when the topic has versions, and back every claim in the lesson with a link.
- Keep the lesson small enough for one sitting: one real win the user can use, tied to the goal.
- Split it into 2 to 4 parts, one idea each, in the order they build on each other. Each part has the points to explain, one example, and 4 check questions with their answers written first.
- End it with a final check of 3 to 5 questions that mix the parts.
- Save it, then tell the user only the lesson's title and what they will be able to do after it, and start the first part.

## Teach in the chat

Teach the parts in their order, and judge each answer against the answer in the file, not against what feels right. An AI tutor helps most when it follows written answers step by step ([Kestin and others, 2025](https://doi.org/10.1038/s41598-025-97652-6)).

### Asking

- Ask one question per message, with one thing to answer. Never put a list of numbered questions in one message: judge one answer at a time.
- A question makes the user recall or use the idea: say it in their own words, predict what happens, apply it to a new case, or find the mistake in an example. Never ask "Is that clear?": a yes proves nothing ([Rosenshine, 2012](https://www.aft.org/sites/default/files/periodicals/Rosenshine.pdf)).
- With choices, also ask why. Make every choice about the same length, so its length gives nothing away, and place the right one by a random number from a command, such as `shuf -i 1-4 -n 1`, so its place gives nothing away either.

### Answering the user

Answer every reply in one of these four ways: the "Try first" question, the checks, the warm-ups and the final check alike. The key points in the file decide which one it is.

- **Right.** Say it is right, then explain it briefly anyway, in two or three lines: "Right, because …". Never stop at "right": the short explanation fixes the idea and fills what the answer left out.
- **Half right.** Say which piece is right, and which piece is missing or wrong. Then give the right answer for that piece, and why.
- **Wrong.** Do not give hints or lead the user around to the answer. Say at once what the right answer is, and why theirs is wrong. Then ask them what they understood, in their own words. When that is right, answer it as a right answer above. When it is still wrong, explain it again in a different way, such as a new example or a smaller step ([Guskey, 2010](https://www.ascd.org/el/articles/lessons-of-mastery-learning)).
- **"I don't know".** The idea is new to the user, so there is nothing to recall yet. Explain it first, then ask them what they understood, as after a wrong answer.

Never move on while a point is wrong. After two wrong rounds on one point, ask about the idea under it. When that idea is missing, teach it first as a new part.

### Each part

1. **Try first.** Ask the part's "Try first" question: does the user know this already? Answer the reply in one of the four ways. A wrong guess is fine: trying first helps the explanation stick ([Richland, Kornell and Kao, 2009](https://learninglab.uchicago.edu/Pre-Testing_files/RichlandKornellKao.pdf)).
2. **Explain.** Explain the points of the part the reply did not already cover, in the user's language, with its example, and end with its source link. A right "Try first" skips only the points it showed, never the whole part: a point the user has not seen or shown is never asked about.
3. **Check.** Ask the checks, one per message, and answer each reply in one of the four ways. A part is done after two right answers in a row, one of them on a new case. A half or wrong answer starts the count again, and the answer to "what did you understand" does not count: ask a new check after it.
4. **Log.** Write each question asked and its result in the lesson file at once, so a new session starts where this one stopped and never repeats a question.

When the user asks something, answer it from the sources in `SOURCES.md`, or from a new one you add there, and end with its link. Then go back to the part. A question outside the lesson goes into `NOTES.md` for a later lesson.

After the last part, run the final check, one question per message, answered in the same four ways. A miss sends you back to its part, then to a new question on it. The lesson is done only when the final check passes.

## A right answer now is not learning yet

A right answer just after an explanation shows the idea is fresh, not that it will last. It lasts when the user has to pull it from memory later, with some effort ([Soderstrom and Bjork, 2015](https://pubmed.ncbi.nlm.nih.gov/25910388/)). Students whose practice scores rose with AI help did no better on the exam ([Bastani and others, 2025](https://doi.org/10.1073/pnas.2422633122)). So:

- Ask the user to recall, not to recognise. An open question beats a yes or no.
- Bring older lessons back in later sessions: the warm-ups do that ([Dunlosky and others, 2023](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-successive-relearning-dunlosky-greve-badali-wissman-rawson.pdf)).
- Mix it up: the final check joins the parts, and the warm-ups join the lessons.
- Keep explanations simple and checks effortful. The effort should go into recalling, not into reading a hard explanation.
- Call an idea known in `KNOWN.md` only once a later session has recalled it.

## Doing, not only talking

Some topics need practice outside the chat, such as a tool to use or a skill of the body. Then a part may end with a small task for the user to do, and its check asks what happened. When the user needs advice from people who do this for real, suggest a place where they meet, and keep it in `SOURCES.md`.
