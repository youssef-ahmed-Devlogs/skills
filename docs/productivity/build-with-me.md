# build-with-me

You build a real project with your own hands, and the agent sits beside you like a senior reviewer. It checks what you ask about against the official docs of your versions and other trusted sources, says what is right and what is wrong and why, with a link, and checks your fixes. You write the code.

**Start it:** `/build-with-me <what you are building>`, inside the project's folder. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill build-with-me --skill interview-me
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** The [`interview-me`](./interview-me.md) skill, installed by the command above. Git in the project helps: without it, you say which files to review each time.

**Where to run it:** Inside the project's folder. For a project you have not started, the folder it will live in, even when it is empty. Make no folder for the skill: it makes its own, `.build-with-me/<project>` in your home folder, and never writes in the project. Run it from the same project folder each time, so it finds its notes.

**Call it:** in Claude Code or GitHub Copilot, type `/build-with-me a small online shop`. In Codex, type `$build-with-me a small online shop`. Type it once at the start of each new chat: it finds its notes and goes on from where you stopped. A chat without it is a normal chat, where the agent can write code.

**Agents:** Claude Code, Codex and GitHub Copilot, or any agent that reads skills. Its notes are plain Markdown outside the project, so you can go on with another agent.

## What it does

1. It asks what you are doing: a project you want to build, one you are building, or one already built that it should follow from here. You can bring a description, a README, or a course or repo you follow.
2. It runs an interview with `interview-me` until the shape of the project is clear. When you do not know the domain, such as how an online shop works as a business, it finds sources on it and explains the few ideas the project needs.
3. In the same interview, it asks your stack, any course or repo you follow, any source of your own you want to add, and how you want to work: in parts with fixed steps, or no fixed way, only reviews when you ask.
4. It gathers the sources before it judges anything: the official docs of each tool for your versions, read from your lock files, and the main community and security references, such as OWASP for auth.
5. You ask for a review whenever you want: two lines, a file, a plan, a commit, or the whole project. It checks it against the sources, the project's own rules and what the project must do, and runs it or its tests when it can.
6. Each point gets one of five labels, with its source: official, community advice, sound preference, wrong preference, or old. A real danger, such as a security hole, is said at once.
7. You fix each point by hand. It reads your fix, checks it against the same source, and marks it fixed.

It never quizzes you. A course or repo you follow is only a list of what to build: its code is judged like yours.

## When to use it

| Your situation | Use |
| --- | --- |
| You build your own project by hand, and want it reviewed against the docs | `build-with-me` |
| You follow a course to its end, and want each step checked | [`study-with-me`](./study-with-me.md) |
| You want to learn a topic, with no project | [`tutor-me`](./tutor-me.md) |
| You need to understand a project that others or agents wrote | [`catch-me-up`](./catch-me-up.md) |

## Example

A small online shop with a REST API, built by hand in Node and Express, with no course.

```text
You:    /build-with-me a small online shop API

Agent:  What I understand: you want to build an online shop's API yourself, and have
        each part checked.
        How sure: 40%. Missing: what it sells, and what done looks like.

        ❓ Is this a shop you are starting now, with no code yet?

        ➡️ My guess: yes, the folder is empty.

You:    Yes. I have never built a shop. I don't know how orders and stock work.
```

It finds sources on how an online shop handles orders, payment and stock, explains the few ideas the API needs, and goes on with the interview: the stack, a source of your own, and how you want to work. You pick small parts, each with a review of the plan before the code. It gathers the docs of Express and the other tools for your versions, and OWASP for auth.

A week later, you ask for a review of the sign-in part:

```text
You:    Review src/auth. I finished the refresh tokens.

Agent:  Right: the access token is short-lived, and the secret comes from the
        environment, as the docs say.

        🏷️ Wrong preference: src/auth/tokens.js:22 hashes the refresh token with bcrypt.
        bcrypt reads only the first 72 bytes of its input, and your tokens are longer,
        so two tokens that share their first 72 bytes match each other. An old token
        can still work. A token is not a password: store a SHA-256 hash of it instead.
        Source: OWASP Password Storage Cheat Sheet, bcrypt section ([link]).

        Two more points: the error filter turns a 401 into a 500, and the cookie has no
        `sameSite`. Which one next?
```

You change the hash by hand, and say it is done. It reads the change, runs the tests, and marks the point fixed.

## More use cases

- **A project you already built:** it reads the code and the lock files first, asks only what it cannot find, and reviews what you point at.
- **A course you build beside:** it reads the course for what to build only, and checks your code against the docs, not against the teacher's code.
- **A source of your own:** an article or a repo you trust goes into the sources, marked as yours. When it disagrees with the official docs, it says so, with both links.
- **Stuck on an idea:** a point rests on something you do not know, such as how a transaction works. It explains only what the point needs, with its source, and goes back to the point.

## What you get

All in `~/.build-with-me/<project>/`, never inside the project:

- `PROJECT.md`: what you build, its stack and versions, and how you work together.
- `SOURCES.md`: the sources for the domain and each topic, with their versions, yours marked.
- `REVIEWS.md`: every review, the points still open, the ones you fixed, and the ones you kept.

The project itself is only read: no files, no commits, no branch changes, unless you say yes to one fix of a real danger.


## Tips

- Say what to review, such as a folder or a commit. "Review my work" reviews what changed since the last review.
- Type `/build-with-me` again in a new chat when one grows long: it goes on from its notes.
