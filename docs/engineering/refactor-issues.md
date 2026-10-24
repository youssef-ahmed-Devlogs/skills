# refactor-issues

Opens GitHub issues that bring old code in line with the rules your project already wrote, without changing what users get. Each run opens the next batch, safest files first, at most 10 open at once.

**Start it:** `/refactor-issues`, in the project. It starts only when you type it.

## What it does

1. It checks the project is set up by [`setup-refactor-issues`](./setup-refactor-issues.md). Without it, it stops.
2. It reads the project's code rules. These rules are the only source of what counts as a break.
3. It runs the project's searches and linters, then reads the files the rules are about.
4. It grades each file by how much a mistake could hurt: `review-optional`, `review-suggested` or `review-required`.
5. It takes the safest level that still has work, and the simplest files in it first.
6. It reads each file in full, drops false hits, and writes how the output stays the same for each break.
7. It opens one issue per file, with every rule that file breaks.

A change that cannot keep the output the same, such as a JSON key that a client reads, is never forced in. It becomes a separate question for you, labelled `review-critical`, and no work starts on it until you decide.

## When to use it

| Your situation | Use |
| --- | --- |
| A project with written code rules, in any language | `refactor-issues` |
| A Laravel project | The rules from [laravel-rules](https://github.com/youssef-ahmed-Devlogs/laravel-rules), then `setup-refactor-issues` and this skill |
| A project with no written rules | Write the rules first: this skill stops without them |
| The batch is open, and you want it done | [`implement-refactor-issues`](./implement-refactor-issues.md) |

## Example

The TypeScript project from the setup page, with no refactor issue open yet:

```text
You:    /refactor-issues

Agent:  0 refactor issues are open, so the batch is 10.
        17 files break a rule. 11 are review-optional: nothing people see changes, and a
        test runs the code. I took the 10 with the fewest breaks.

        Opened:
        - #20 Refactor src/utils/date.ts: console.log
        - #21 Refactor src/api/client.ts: console.log
        - #22 Refactor src/pages/Cart.tsx: a component outside src/components
        - ...

        Asked you one question in #19 (review-critical): the API answer key `user_name`
        breaks the naming rule, but a mobile app reads it. Renaming it would break the app.

        1 file is left at this level. Next step: /implement-refactor-issues.
```

Each issue says why the file breaks the rule, what to do, and how the output stays the same.

## More use cases

- **A rule added last month:** new code follows it, and this skill finds the old files that do not.
- **A big old project:** batch after batch, the safest files go first, and the risky ones come last, when the work has shown the way.
- **A rule only reading can check:** such as "a handler holds no logic". It reads the files that rule is about.

## What you get

Up to 10 issues labelled `refactor`, a review flag and `ready-for-agent`, plus a `review-critical` question for each break that would change what users get.

## What it needs

[`setup-refactor-issues`](./setup-refactor-issues.md) run once, `gh`, and a GitHub remote.
