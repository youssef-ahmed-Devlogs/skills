# Engineering

Skills for daily code work.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[delegating-to-cli](./delegating-to-cli/SKILL.md)**: Work through a list of fixes by handing each one to its own Claude Code CLI session in a terminal tab. You write the issue, answer the worker, review its diff, merge and clean up.
- **[refactor-issues](./refactor-issues/SKILL.md)**: Open the next batch of refactor issues that bring old code in line with the project's own code rules, safest first. Works in any project and any language.
