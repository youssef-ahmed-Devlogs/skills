# Workspace format

The shape of each file in the workspace. Keep every file short: it is read at the start of each session.

## `PROJECT.md`

```md
# {Project name}

What it is: {What the project does, and for whom, in one or two sentences, from the interview.}
State: idea | in progress | built. Folder: {absolute path of the project}.
Done when: {from the interview}.
Not doing: {from the interview}.

Stack: {language} {version}, {framework} {version}, {tool} {version}. From: {dependency or lock file, or "newest stable, no lock file yet"}.
Reference: [{course, book or repo}]({link}), or "none". Read for: what to build only.

## How we work

{What the user picked in the interview: the parts and their steps, or "no fixed way, reviews when the user asks".}

Parts:
- [x] {Part}
- [ ] {Part} (now)

Last commit reviewed: {short hash}, {date}, or "none".

Now: {The review in progress, such as `src/auth` on {date}. Talking about: {point title}. Waiting: {point titles}.} Or "nothing in progress".

## Changes

- {date}: {what changed in the way of working, or the project, and why}.
```

- Leave out "Parts" when the user works without them.
- Keep "Now" true after each message: another chat, or another agent, goes on from it with nothing else.
- Change what the project is, or how you work, only after the user agrees, and write why under "Changes".

## `SOURCES.md`

```md
# Sources

Versions: {tool} {version}, {tool} {version}, as in PROJECT.md.

## The domain

- [{Title}]({link}), {author or site}. Good for: {what it explains about the domain}.

## {Topic, such as auth}

- [{Title}]({link}), {author or project}. Version: {version, or "any"}. Kind: official | community | security | reference. Good for: {what it covers, and when to reach for it}.
- [{Title}]({link}), {author}. Kind: community. The user's own. Good for: {what it covers}.

## Still looking for

- {A topic of the project with no good source yet.}
```

- Order the sources of each topic as "Sources" in SKILL.md says: the subject's official docs, for the versions in `PROJECT.md`, then its community, then the docs and community of each inner tool. Security references, such as OWASP, go under the topic they guard. No sales pages.
- A source the user brought says "The user's own", and its kind says where it ranks.
- A docs source says its version: the docs of another version can say something else.
- When a version in the project changes, replace the docs sources of that tool with the docs of the new version.
- Remove a source that turned out wrong, and check again what rests on it, as SKILL.md says.

## `REVIEWS.md`

```md
# Reviews

## Open

- **{Short title}** ({Wrong preference | Old}). Where: `{file}:{line}`. Found: {date}. Is: {what the code does}. Right: {what, and why}. Source: [{title}]({link}), version {v}.

## Fixed

- **{Short title}**. Fixed {date}, by the user | by the agent, on the user's yes. Checked: {how, such as read against the same source}.

## Kept

- **{Short title}** ({Sound preference | Wrong preference}). Kept {date}. The user's reason: {why}.

## Log

### {date}: {what was reviewed, such as `src/auth/` or commit {hash}}

- {Label}: {the point, in one line}. Source: [{title}]({link}).
```

- "Open" holds only wrong and old points. Official, community and sound points live in the log only.
- "Fixed by the user" is the normal case. Write "by the agent, on the user's yes" only for a danger you fixed yourself.

## `NOTES.md`

A plain list: how the user likes to be helped, questions to come back to, and anything the next session should know.
