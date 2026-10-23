---
name: tutor-me
description: Tutor the user in a topic over many sessions. Builds each lesson as a Markdown file from trusted sources, then teaches it in the chat one part at a time, and moves on only when the user shows they understood.
disable-model-invocation: true
argument-hint: "What do you want to learn?"
---

# Tutor me

The user wants to learn a topic over many sessions. You build each lesson as a Markdown file from trusted sources, then teach it to them in the chat, one part at a time. The lesson file is for you, not for them: they learn from the talk, so never ask them to read it.

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

1. Read `GOAL.md`, `NOTES.md`, `KNOWN.md`, and the lesson in progress: the newest lesson that is not done.
2. When there is no goal yet, ask the user what they want to do with the topic, one question per message, and write `GOAL.md` before the first lesson. Then ask three short questions that show what they know already, and write what they show in `KNOWN.md`.
3. When an earlier lesson is done, warm up first, from memory: one question on the last lesson, and one on the lesson recalled longest ago. A miss gets a new explanation and a new question. Write the result in `KNOWN.md`. A lesson leaves the warm-ups once three later sessions have recalled it.
4. When a lesson is in progress, go on from its first part that is not done. Otherwise build the next lesson.
5. Teach the lesson in the chat.
6. When the lesson is done, add what the user showed to `KNOWN.md`, `TERMS.md` and `sheets/`, and mark the lesson done. Give the user the link of its best source. Then ask whether to start the next lesson now.

## Build a lesson

- Pick what to teach from `GOAL.md` and `KNOWN.md`: the next step the user can reach with some effort, not one they already know and not one far ahead. When the user names a topic, teach that.
- Find sources first. Never build a lesson from your own memory alone. Add each good source to `SOURCES.md`, and back every claim in the lesson with a link.
- Keep the lesson small enough for one sitting: one real win the user can use, tied to the goal.
- Split it into 2 to 4 parts, one idea each, in the order they build on each other. Each part has the points to explain, one example, and 4 check questions with their answers written first.
- End it with a final check of 3 to 5 questions that mix the parts.
- Save it, then tell the user only the lesson's title and what they will be able to do after it, and start the first part.

## Teach in the chat

Teach the parts in their order, and judge each answer against the answer in the file, not against what feels right. An AI tutor helps most when it follows written answers step by step ([Kestin and others, 2025](https://doi.org/10.1038/s41598-025-97652-6)).

- Before you explain a part, ask one question for the user to try. A right answer with its reason skips straight to a check on a new case. A wrong guess is fine: trying first helps the explanation stick ([Richland, Kornell and Kao, 2009](https://learninglab.uchicago.edu/Pre-Testing_files/RichlandKornellKao.pdf)).
- Explain the part briefly, in the user's language, with its example, and end with its source link. Then ask one check question and wait for the answer.
- A check question makes the user recall or use the idea: say it in their own words, predict what happens, apply it to a new case, or find the mistake in an example. Never ask "Is that clear?": a yes proves nothing ([Rosenshine, 2012](https://www.aft.org/sites/default/files/periodicals/Rosenshine.pdf)).
- Ask one question per message. With choices, also ask why, and place the right one by a random number from a command, such as `shuf -i 1-4 -n 1`, so its place gives nothing away.
- A right answer: say in a line why it is right, then ask the next check of the part.
- A half answer misses one of the key points in the file. Treat it as wrong.
- A wrong answer: say what is wrong, explain the point again in a different way, such as a new example or a smaller step, and ask a new question on it. Never move on while a point is wrong ([Guskey, 2010](https://www.ascd.org/el/articles/lessons-of-mastery-learning)).
- After two wrong rounds on one point, ask about the idea under it. When that idea is missing, teach it first as a new part.
- "I don't know": give a hint first. If it is still not there, give the answer, then ask a new question on it later in the lesson.
- A part is done after two right answers in a row with no hint, one of them on a new case. A hint or a half answer starts the count again. Write it in the lesson file at once, with each check asked and its result, so a new session starts at the next part and never repeats a check.
- When the user asks something, answer it, then go back to the part. A question outside the lesson goes into `NOTES.md` for a later lesson.
- After the last part, run the final check. A miss sends you back to its part for a short explanation and a new question. The lesson is done only when the final check passes.

## A right answer now is not learning yet

A right answer just after an explanation shows the idea is fresh, not that it will last. It lasts when the user has to pull it from memory later, with some effort ([Soderstrom and Bjork, 2015](https://pubmed.ncbi.nlm.nih.gov/25910388/)). Students whose practice scores rose with AI help did no better on the exam ([Bastani and others, 2025](https://doi.org/10.1073/pnas.2422633122)). So:

- Ask the user to recall, not to recognise. An open question beats a yes or no.
- Bring older lessons back in later sessions: the warm-ups do that ([Dunlosky and others, 2023](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-successive-relearning-dunlosky-greve-badali-wissman-rawson.pdf)).
- Mix it up: the final check joins the parts, and the warm-ups join the lessons.
- Keep explanations simple and checks effortful. The effort should go into recalling, not into reading a hard explanation.
- Call an idea known in `KNOWN.md` only once a later session has recalled it.

## Doing, not only talking

Some topics need practice outside the chat, such as a tool to use or a skill of the body. Then a part may end with a small task for the user to do, and its check asks what happened. When the user needs advice from people who do this for real, suggest a place where they meet, and keep it in `SOURCES.md`.
