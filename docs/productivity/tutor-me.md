## What it does

`tutor-me` teaches you a topic over many sessions, in the chat. It asks what you want to do with the topic, and what you know already. Then it builds a small lesson from trusted sources, as a Markdown file for itself, and teaches it to you one part at a time. Each part starts by asking whether you know it already, and ends with questions that make you recall or use the idea, one per message. It moves on only after you answer them right. A final check joins the parts, and each new session starts with a short recall of older lessons.

Every answer gets a reply. A right one gets "right, because …" in two or three lines. A half one gets which piece is missing or wrong, and the right answer for it. A wrong one gets the right answer and why, with no hints, then "what did you understand?". "I don't know" gets the explanation first.

It keeps everything in the folder you run it in: your goal, the sources, the lessons, what you know, the terms, and short sheets you can read later.

## When to reach for it

Make an empty folder for the topic, open your agent there, and type `/tutor-me <topic>`, such as `/tutor-me Docker`. Run it again in the same folder for the next session: it goes on where you stopped.

## Prerequisites

None.
