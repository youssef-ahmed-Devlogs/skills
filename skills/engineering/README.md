# Engineering

Skills for daily code work.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[delegating-to-cli](./delegating-to-cli/SKILL.md)**: Work through a list of fixes by handing each one to its own Claude Code CLI session in a terminal tab. You write the issue, answer the worker, review its diff, merge and clean up.
- **[implement-refactor-issues](./implement-refactor-issues/SKILL.md)**: Do the open refactor issues that `refactor-issues` opened, one batch in one pull request, with what users get kept the same. Works in any project and any language.
- **[refactor-issues](./refactor-issues/SKILL.md)**: Open the next batch of refactor issues that bring old code in line with the project's own code rules, safest first. Works in any project and any language.
- **[setup-refactor-issues](./setup-refactor-issues/SKILL.md)**: Prepare a project for `refactor-issues`: write its checks file and reading list from its own code rules, wire in the ready checks of a stack's rules, and make the labels. Works in any project and any language.
